# -*- coding: utf-8 -*-
"""
Github class for making needed API calls to github
"""
import requests


class GitHubException(Exception):
    """Base exception class others inherit."""
    pass


class GitHubRepoExists(GitHubException):
    """Repo exists, and thus cannot be created."""
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
            while response.links.get('next', False):
                response = self.session.get(response.links['next']['url'])
                results += response.json()
        return results

    def create_repo(self, org, repo, description):
        """Creates a new github repository or raises exceptions

        Args:
            org (str): Organization to create the repo in.
            repo (str): Name of the repo to create.
            description (str): Description of repo to use.
        Raises:
            GitHubRepoExists
            GitHubUnknownError
            requests.RequestException
        Returns:
            dict: Github dictionary of a repo
                (https://developer.github.com/v3/repos/#create)

        """
        repo_url = '{url}repos/{org}/{repo}'.format(
            url=self.api_url,
            org=org,
            repo=repo
        )
        # Try and get the URL, if it 404's we are good, otherwise raise
        repo_response = self.session.get(repo_url)
        if repo_response.status_code == 200:
            raise GitHubRepoExists('This repository already exists')
        if repo_response.status_code != 404:
            raise GitHubUnknownError(repo_response.text)

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
            requests.RequestException

        """
        list_teams_url = '{url}orgs/{org}/teams'.format(
            url=self.api_url,
            org=org
        )
        teams = self._get_all(list_teams_url)
        if not teams:
            raise GitHubUnknownError(
                'No teams found in {0} organization'.format(org)
            )
        found_team = [x for x in teams if x['name'].strip() == team.strip()]
        if len(found_team) != 1:
            raise GitHubNoTeamFound(
                '{0} not in list of teams for {1}'.format(team, org)
            )
        found_team = found_team[0]
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
            repo (str): Name of the repo to create.
            url (str): URL of the hook to add
        Raises:
            GitHubUnknownError
            requests.RequestException
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
