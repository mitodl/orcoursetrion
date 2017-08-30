# -*- coding: utf-8 -*-
"""
Github class for making needed API calls to github
"""
import base64
from itertools import chain
import shutil
import tempfile

import requests
import sh


CLONE_DIR = 'cloned_repo'


class GitHubException(Exception):
    """Base exception class others inherit."""
    pass


class GitHubRepoExists(GitHubException):
    """Repo exists, and thus cannot be created."""
    pass


class GitHubRepoDoesNotExist(GitHubException):
    """Repo does not exist, and therefore actions can't be taken on it."""
    pass


class GitHubUnknownError(GitHubException):
    """Unexpected status code exception"""
    pass


class GitHubNoTeamFound(GitHubException):
    """Name team not found in list"""
    pass


class GitHub(object):
    """
    API class for handling calls to github
    """
    def __init__(self, api_url, oauth2_token):
        """Initialize a requests session for use with this class by
        specifying the base API endpoint and key.

        Args:
            api_url (str): Github API URL such as https://api.github.com/
            oauth2_token (str): Github OAUTH2 token for v3
        """
        self.api_url = api_url
        if not api_url.endswith('/'):
            self.api_url += '/'
        self.session = requests.Session()
        # Add OAUTH2 token to session headers and set Agent
        self.session.headers = {
            'Authorization': 'token {0}'.format(oauth2_token),
            'User-Agent': 'Orcoursetrion',
        }

    def _get_all(self, url):
        """Return all results from URL given (i.e. page through them)

        Args:
            url(str): Full github URL with results.
        Returns:
            list: List of items returned.
        """
        results = None
        response = self.session.get(url)
        if response.status_code == 200:
            results = response.json()
            while (
                    response.links.get('next', False) and
                    response.status_code == 200
            ):
                response = self.session.get(response.links['next']['url'])
                results += response.json()
        if response.status_code not in [200, 404]:
            raise GitHubUnknownError(response.text)
        return results

    def _get_repo(self, org, repo):
        """Either return the repo dictionary, or None if it doesn't exists.

        Args:
            org (str): Organization the repo lives in.
            repo (str): The name of the repo.
        Raises:
            requests.exceptions.RequestException
            GitHubUnknownError
        Returns:
            dict or None: Repo dictionary from github
                (https://developer.github.com/v3/repos/#get) or None if it
                doesn't exist.
        """
        repo_url = '{url}repos/{org}/{repo}'.format(
            url=self.api_url,
            org=org,
            repo=repo
        )

        # Try and get the URL, if it 404's we are good, otherwise raise
        repo_response = self.session.get(repo_url)
        if repo_response.status_code == 200:
            return repo_response.json()
        if repo_response.status_code != 404:
            raise GitHubUnknownError(repo_response.text)

    def _find_team(self, org, team):
        """Find a team in an org by name, or raise.

        Args:
            org (str): Organization to create the repo in.
            team (str): Team to find by name.

        Raises:
            GitHubUnknownError
            GitHubNoTeamFound

        Returns:
            dict: Team dictionary
                  (https://developer.github.com/v3/orgs/teams/#response)
        """
        list_teams_url = '{url}orgs/{org}/teams'.format(
            url=self.api_url,
            org=org
        )
        teams = self._get_all(list_teams_url)
        if not teams:
            raise GitHubUnknownError(
                "No teams found in org. This shouldn't happen"
            )
        found_team = [
            x for x in teams
            if x['name'].strip().lower() == team.strip().lower()
        ]
        if len(found_team) != 1:
            raise GitHubNoTeamFound(
                '{0} not in list of teams for {1}'.format(team, org)
            )
        found_team = found_team[0]
        return found_team

    def create_repo(self, org, repo, description):
        """Creates a new github repository or raises exceptions

        Args:
            org (str): Organization to create the repo in.
            repo (str): Name of the repo to create.
            description (str): Description of repo to use.
        Raises:
            GitHubRepoExists
            GitHubUnknownError
            requests.exceptions.RequestException
        Returns:
            dict: Github dictionary of a repo
                (https://developer.github.com/v3/repos/#create)

        """
        repo_dict = self._get_repo(org, repo)
        if repo_dict is not None:
            raise GitHubRepoExists('This repository already exists')

        # Everything looks clean, create the repo.
        create_url = '{url}orgs/{org}/repos'.format(
            url=self.api_url,
            org=org
        )
        payload = {
            'name': repo,
            'description': description,
            'private': True,
        }
        repo_create_response = self.session.post(create_url, json=payload)
        if repo_create_response.status_code != 201:
            raise GitHubUnknownError(repo_create_response.text)
        return repo_create_response.json()

    def _create_team(self, org, team_name, read_only):
        """Internal function to create a team.

        Args:
            org (str): Organization to create the repo in.
            team_name (str): Name of team to create.
            read_only (bool): If false, read/write, if true read_only.

        Raises:
            GitHubUnknownError
            requests.RequestException
        Returns:
            dict: Team dictionary
                  (https://developer.github.com/v3/orgs/teams/#response)
        """
        if read_only:
            permission = 'pull'
        else:
            permission = 'push'

        create_url = '{url}orgs/{org}/teams'.format(
            url=self.api_url,
            org=org
        )
        response = self.session.post(create_url, json={
            'name': team_name,
            'permission': permission
        })
        if response.status_code != 201:
            raise GitHubUnknownError(response.text)
        return response.json()

    def put_team(self, org, team_name, read_only, members):
        """Create a team in a github organization.

        Utilize
        https://developer.github.com/v3/orgs/teams/#list-teams,
        https://developer.github.com/v3/orgs/teams/#create-team,
        https://developer.github.com/v3/orgs/teams/#list-team-members,
        https://developer.github.com/v3/orgs/teams/#add-team-membership,
        and
        https://developer.github.com/v3/orgs/teams/#remove-team-membership.
        to create a team and/or replace an existing team's membership
        with the ``members`` list.

        Args:
            org (str): Organization to create the repo in.
            team_name (str): Name of team to create.
            read_only (bool): If false, read/write, if true read_only.
            members (list): List of github usernames to add to the
                              team. If none, membership changes won't occur

        Raises:
            GitHubUnknownError
            requests.RequestException

        Returns:
            dict: The team dictionary
                (https://developer.github.com/v3/orgs/teams/#response-1)

        """
        # Disabling too-many-locals because I need them as a human to
        # keep track of the sets going on here.
        # pylint: disable=too-many-locals
        try:
            team_dict = self._find_team(org, team_name)
        except GitHubNoTeamFound:
            team_dict = self._create_team(org, team_name, read_only)

        # Just get the team and exit if no members are given
        if members is None:
            return team_dict

        # Have the team, now replace member list with the one we have
        members_url = '{url}teams/{id}/members'.format(
            url=self.api_url,
            id=team_dict['id']
        )
        existing_members = self._get_all(members_url)

        # Filter list of dicts down to just username list
        existing_members = [x['login'] for x in existing_members]

        # Grab everyone that should no longer be members
        remove_members = dict(
            [(x, False) for x in existing_members if x not in members]
        )
        # Grab everyone that should be added
        add_members = dict(
            [(x, True) for x in members if x not in existing_members]
        )
        # merge the dictionary of usernames dict with True to add,
        # False to remove.
        membership_dict = dict(
            chain(remove_members.items(), add_members.items())
        )
        # Now do the adds and removes of membership to sync them
        for member, add in membership_dict.items():
            url = '{url}teams/{id}/memberships/{member}'.format(
                url=self.api_url,
                id=team_dict['id'],
                member=member
            )
            if add:
                response = self.session.put(url)
            else:
                response = self.session.delete(url)

            if response.status_code not in [200, 204]:
                raise GitHubUnknownError(
                    'Failed to add or remove {0}. Got: {1}'.format(
                        member, response.text
                    )
                )

        return team_dict

    def add_team_repo(self, org, repo, team):
        """Add a repo to an existing team (by name) in the specified org.

        We first look up the team to get its ID
        (https://developer.github.com/v3/orgs/teams/#list-teams), and
        then add the repo to that team
        (https://developer.github.com/v3/orgs/teams/#add-team-repo).

        Args:
            org (str): Organization to create the repo in.
            repo (str): Name of the repo to create.
            team (str): Name of team to add.
        Raises:
            GitHubNoTeamFound
            GitHubUnknownError
            requests.exceptions.RequestException

        """
        found_team = self._find_team(org, team)
        team_repo_url = '{url}teams/{id}/repos/{org}/{repo}'.format(
            url=self.api_url,
            id=found_team['id'],
            org=org,
            repo=repo
        )
        response = self.session.put(team_repo_url)
        if response.status_code != 204:
            raise GitHubUnknownError(response.text)

    def add_web_hook(self, org, repo, url):
        """Adds an active hook to a github repository.

        This utilizes
        https://developer.github.com/v3/repos/hooks/#create-a-hook to
        create a form type Web hook that responds to push events
        (basically all the defaults).

        Args:
            org (str): Organization to create the repo in.
            repo (str): Name of the repo the hook will live in.
            url (str): URL of the hook to add.
        Raises:
            GitHubUnknownError
            requests.exceptions.RequestException
        Returns:
            dict: Github dictionary of a hook
                (https://developer.github.com/v3/repos/hooks/#response-2)

        """
        hook_url = '{url}repos/{org}/{repo}/hooks'.format(
            url=self.api_url,
            org=org,
            repo=repo
        )
        payload = {
            'name': 'web',
            'active': True,
            'config': {
                'url': url,
            }
        }
        response = self.session.post(hook_url, json=payload)
        if response.status_code != 201:
            raise GitHubUnknownError(response.text)
        return response.json()

    def delete_web_hooks(self, org, repo):
        """Delete all the Web hooks for a repository

        Uses https://developer.github.com/v3/repos/hooks/#list-hooks
        to get a list of all hooks, and then runs
        https://developer.github.com/v3/repos/hooks/#delete-a-hook
        to remove each of them.
        Args:
            org (str): Organization to create the repo in.
            repo (str): Name of the repo to remove hooks from.
        Raises:
            GitHubUnknownError
            GitHubRepoDoesNotExist
            requests.exceptions.RequestException
        Returns:
            int: Number of hooks removed

        """
        # Verify the repo exists first
        repo_dict = self._get_repo(org, repo)
        if repo_dict is None:
            raise GitHubRepoDoesNotExist(
                'Repo does not exist. Cannot remove hooks'
            )
        url = '{url}repos/{org}/{repo}/hooks'.format(
            url=self.api_url,
            org=org,
            repo=repo
        )
        hooks = self._get_all(url)
        num_hooks_removed = 0
        for hook in hooks or []:
            response = self.session.delete(hook['url'])
            if response.status_code != 204:
                raise GitHubUnknownError(response.text)
            num_hooks_removed += 1
        return num_hooks_removed

    @staticmethod
    def shallow_copy_repo(src_repo, dst_repo, committer, branch=None):
        """Copies one branch repo's contents to a new repo in the same
        organization without history.

        .. DANGER::
           This will overwrite the destination repo's default branch and
           rewrite its history.

        The basic workflow is:

        - Clone source repo
        - Remove source repo ``.git`` folder
        - Initialize as new git repo
        - Set identity
        - Add everything and commit
        - Force push to destination repo

        Args:
            src_repo (str): Full git url to source repo.
            dst_repo (str): Full git url to destination repo.
            committer (dict): {'name': ..., 'email': ...} for the name
                and e-mail to use in the initial commit of the
                destination repo.
            branch (str): Option branch, if not specified default is used.
        Raises:
            sh.ErrorReturnCode
        Returns:
            None

        """
        # Disable member use because pylint doesn't get dynamic members
        # pylint: disable=no-member

        # Grab current working directory so we return after we are done
        cwd = unicode(sh.pwd().rstrip('\n'))
        tmp_dir = tempfile.mkdtemp(prefix='orc_git')
        try:
            sh.cd(tmp_dir)
            if branch is None:
                sh.git.clone(src_repo, CLONE_DIR, depth=1)
            else:
                sh.git.clone(src_repo, CLONE_DIR, depth=1, branch=branch)

            sh.cd(CLONE_DIR)
            shutil.rmtree('.git')
            sh.git.init()
            sh.git.config('user.email', committer['email'])
            sh.git.config('user.name', committer['name'])
            sh.git.remote.add.origin(dst_repo)
            sh.git.add('.')
            sh.git.commit(
                m='Initial rerun copy by Orcoursetrion from {0}'.format(
                    src_repo
                )
            )
            sh.git.push.origin.master(f=True)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            sh.cd(cwd)

    def add_repo_file(self, org, repo, committer, message, path, contents):
        """Adds the ``contents`` provided to the ``path`` in the repo
        specified and committed by the ``commiter`` parameters
        provided.

        https://developer.github.com/v3/repos/contents/#create-a-file

        .. NOTE::
            This commits directly to the default branch of the repo.

        Args:
            org (str): Organization the repo lives in.
            repo (str): The name of the repo.
            committer (dict): {'name': ..., 'email': ...} for the name
                and e-mail to use in the initial commit of the
                destination repo.
            message (str): Commit message to use for the addition.
            path (str): The content path, i.e. ``docs/.gitignore``
            contents (str): The actual string Contents of the file.
        Raises:
            requests.exceptions.RequestException
            GitHubRepoDoesNotExist
            GitHubUnknownError
        Returns:
            None
        """
        repo_dict = self._get_repo(org, repo)
        if repo_dict is None:
            raise GitHubRepoDoesNotExist(
                'Repo does not exist. Cannot add file'
            )
        url = '{url}repos/{org}/{repo}/contents/{path}'.format(
            url=self.api_url,
            org=org,
            repo=repo,
            path=path
        )
        payload = {
            'message': message,
            'committer': committer,
            'content': base64.b64encode(contents).decode('ascii'),
        }
        response = self.session.put(url, json=payload)
        if response.status_code != 201:
            raise GitHubUnknownError(
                'Failed to add contents to {org}/{repo}/{path}. '
                'Got: {response}'.format(
                    org=org, repo=repo, path=path, response=response.text
                )
            )
