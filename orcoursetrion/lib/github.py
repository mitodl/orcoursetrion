# -*- coding: utf-8 -*-
"""
Github class for making needed API calls to github
"""
import requests


class GitHubRepoExists(Exception):
    """Repo exists, and thus cannot be created."""
    pass


class GitHubUnknownError(Exception):
    """Unexpected status code exception"""
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
        self.session = requests.Session()
        # Add OAUTH2 token to session headers and set Agent
        self.session.headers = {
            'Authorization': 'token {0}'.format(oauth2_token),
            'User-Agent': 'Orcoursetrion',
        }

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
