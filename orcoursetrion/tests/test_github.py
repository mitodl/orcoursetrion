# -*- coding: utf-8 -*-
"""
Test github actions and backing library
"""
from functools import partial
import json

import httpretty
import mock

from orcoursetrion.actions import create_export_repo, create_xml_repo
from orcoursetrion.lib import (
    GitHub,
    GitHubRepoExists,
    GitHubUnknownError,
    GitHubNoTeamFound
)
from orcoursetrion.tests.base import TestGithubBase


class TestGithub(TestGithubBase):
    """Test Github actions and backing library."""

    @httpretty.activate
    def test_lib_create_repo_success(self):
        """Test the API call comes through as expected.
        """
        self.register_repo_check(self.callback_repo_check)
        self.register_repo_create(self.callback_repo_create)

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        repo = git_hub.create_repo(
            self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
        )
        self.assertEqual(repo['html_url'], 'testing')

    @httpretty.activate
    def test_lib_create_repo_exists(self):
        """Test what happens when the repo exists."""

        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubRepoExists):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )

    @httpretty.activate
    def test_lib_create_repo_unknown_errors(self):
        """Test what happens when we don't get expected status_codes
        """

        self.register_repo_check(self.callback_repo_check)
        self.register_repo_create(
            partial(self.callback_repo_create, status_code=500)
        )

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubUnknownError):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )
        self.register_repo_check(
            partial(self.callback_repo_check, status_code=422)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubUnknownError):
            git_hub.create_repo(
                self.ORG, self.TEST_REPO, self.TEST_DESCRIPTION
            )

    @httpretty.activate
    def test_lib_create_hook(self):
        """Test valid hook creation"""
        self.register_hook_create(json.dumps({'id': 1}), status=201)
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # Will raise if it is invalid
        git_hub.add_web_hook(self.ORG, self.TEST_REPO, 'http://fluff')

        # Setup for failure mode
        error_body = json.dumps({u'message': u'Validation Failed'})
        self.register_hook_create(
            body=error_body,
            status=422
        )
        with self.assertRaisesRegexp(GitHubUnknownError, error_body):
            git_hub.add_web_hook(self.ORG, self.TEST_REPO, 'http://fluff')

    @httpretty.activate
    def test_lib_add_team_repo_success(self):
        """Test what happens when we don't get expected status_codes
        """
        self.register_team_list(partial(self.callback_team_list, more=True))
        self.register_team_repo_add(self.callback_team_repo)

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # This will raise on any failures
        git_hub.add_team_repo(self.ORG, self.TEST_REPO, self.TEST_TEAM)

    @httpretty.activate
    def test_lib_add_team_repo_no_teams(self):
        """Test what happens when we don't have any teams
        """
        self.register_team_list(
            partial(self.callback_team_list, status_code=404)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # See how we handle no teams
        with self.assertRaisesRegexp(
                GitHubUnknownError,
                'No teams found in {0} organization'.format(self.ORG)
        ):
            git_hub.add_team_repo(self.ORG, self.TEST_REPO, self.TEST_TEAM)

    @httpretty.activate
    def test_lib_add_team_repo_team_not_found(self):
        """Test what happens when the team isn't in the org
        """
        self.register_team_list(self.callback_team_list)
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaises(GitHubNoTeamFound):
            git_hub.add_team_repo(self.ORG, self.TEST_REPO, 'foobar')

    @httpretty.activate
    def test_lib_add_team_repo_team_spaces_match(self):
        """The API sometimes returns spaces in team names, so make sure we
        still match when stripped.
        """
        self.register_team_list(self.callback_team_list)
        self.register_team_repo_add(self.callback_team_repo)
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # This will raise if we aren't stripping team names
        git_hub.add_team_repo(
            self.ORG, self.TEST_REPO, ' {0} '.format(self.TEST_TEAM)
        )

    @httpretty.activate
    def test_lib_add_team_repo_fail(self):
        """Test what happens when the repo can't be added to the team
        """
        self.register_team_list(self.callback_team_list)
        self.register_team_repo_add(
            partial(self.callback_team_repo, status_code=422)
        )

        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaisesRegexp(GitHubUnknownError, json.dumps({
                "message": "Validation Failed",
        })):
            git_hub.add_team_repo(self.ORG, self.TEST_REPO, self.TEST_TEAM)

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_actions_create_export_repo_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        # While we are at it, make sure we can handle configured
        # github API urls that don't have a trailing slash.
        config.ORC_GH_API_URL = self.URL[:-1]
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_STUDIO_ORG = self.ORG
        config.ORC_STUDIO_DEPLOY_TEAM = self.TEST_TEAM

        self.register_repo_check(self.callback_repo_check)
        self.register_repo_create(self.callback_repo_create)
        self.register_team_list(
            partial(self.callback_team_list, more=True)
        )
        self.register_team_repo_add(self.callback_team_repo)

        create_export_repo(
            self.TEST_COURSE,
            self.TEST_TERM,
            description=self.TEST_DESCRIPTION
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_actions_create_xml_repo_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_XML_ORG = self.ORG
        config.ORC_XML_DEPLOY_TEAM = self.TEST_TEAM
        config.ORC_STAGING_GITRELOAD = self.TEST_STAGING_GR

        self.register_repo_check(self.callback_repo_check)
        self.register_repo_create(self.callback_repo_create)
        self.register_team_list(
            partial(self.callback_team_list, more=True)
        )
        self.register_team_repo_add(self.callback_team_repo)
        self.register_hook_create(
            body=json.dumps({'id': 1}),
            status=201
        )

        create_xml_repo(
            self.TEST_COURSE,
            self.TEST_TERM,
            team=self.TEST_TEAM,
            description=self.TEST_DESCRIPTION,
        )
