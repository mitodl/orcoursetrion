# -*- coding: utf-8 -*-
"""
Test github actions and backing library
"""
from functools import partial

import httpretty
import mock

from orcoursetrion.actions import create_export_repo
from orcoursetrion.lib import GitHub, GitHubRepoExists, GitHubUnknownError
from orcoursetrion.tests.base import TestGithubBase


class TestGithub(TestGithubBase):
    """Test Github actions and backing library."""

    @httpretty.activate
    def test_lib_create_repo_success(self):
        """Test the API call comes through as expected.
        """

        # Register for repo check
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=self.callback_repo_check
        )
        # Register for repo create
        httpretty.register_uri(
            httpretty.POST,
            '{url}orgs/{org}/repos'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=self.callback_repo_create
        )

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        repo = git_hub.create_repo(
            self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
        )
        self.assertEqual(repo['html_url'], 'testing')

    @httpretty.activate
    def test_lib_create_repo_exists(self):
        """Test what happens when the repo exists."""

        # Register for repo check
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=partial(self.callback_repo_check, status_code=200)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubRepoExists):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )

    @httpretty.activate
    def test_unknown_errors(self):
        """Test what happens when we don't get expected status_codes
        """

        # Register for repo check
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=self.callback_repo_check
        )
        # Register for repo create
        httpretty.register_uri(
            httpretty.POST,
            '{url}orgs/{org}/repos'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=partial(self.callback_repo_create, status_code=500)
        )

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubUnknownError):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )

        # Register for repo check with bad something or other
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=partial(self.callback_repo_check, status_code=422)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubUnknownError):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_actions_create_export_repo_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_STUDIO_ORG = self.ORG

        # Register for repo check
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=self.callback_repo_check
        )
        httpretty.register_uri(
            httpretty.POST,
            '{url}orgs/{org}/repos'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=self.callback_repo_create
        )

        create_export_repo(
            self.TEST_COURSE,
            self.TEST_TERM,
            description=self.TEST_DESCRIPTION
        )
