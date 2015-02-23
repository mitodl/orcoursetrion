# -*- coding: utf-8 -*-
"""
Test github actions and backing library
"""
from functools import partial
import json

import httpretty
import mock

from orcoursetrion.actions import create_export_repo, create_xml_repo, put_team
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

    @httpretty.activate
    def test_lib_put_team_success_exists(self):
        """Change team membership successfully for team that exists."""
        team = ['archlight', 'ereshkigal']
        member_changes = []
        self.register_team_list(self.callback_team_list)
        self.register_team_members(self.callback_team_members)
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, action_list=member_changes)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        git_hub.put_team(self.ORG, self.TEST_TEAM, True, team)
        self.assertItemsEqual(
            [
                ('bizarnage', False),
                ('chemistro', False),
                ('dreadnought', False),
                ('ereshkigal', True)
            ],
            member_changes
        )

    @httpretty.activate
    def test_lib_put_team_create(self):
        """Create a team with membership."""
        member_changes = []
        self.register_team_list(self.callback_team_list)
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_create(self.callback_team_create)
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, action_list=member_changes)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        git_hub.put_team(
            self.ORG, 'New Team', True, self.TEST_TEAM_MEMBERS
        )
        self.assertItemsEqual(
            [(unicode(x), True) for x in self.TEST_TEAM_MEMBERS],
            member_changes
        )

    @httpretty.activate
    def test_lib_put_team_create_permission(self):
        """Create a team with membership."""
        member_changes = []
        self.register_team_list(self.callback_team_list)
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, action_list=member_changes)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)

        # Verify permission is pull:
        self.register_team_create(self.callback_team_create)
        git_hub.put_team(
            self.ORG, 'New Team', True, self.TEST_TEAM_MEMBERS
        )
        # Verify permission is push:
        self.register_team_create(
            partial(self.callback_team_create, read_only=False)
        )
        git_hub.put_team(
            self.ORG, 'New Team', False, self.TEST_TEAM_MEMBERS
        )

    @httpretty.activate
    def test_lib_put_team_creation_fail(self):
        """Create a team with membership."""
        self.register_team_list(self.callback_team_list)
        self.register_team_create(
            partial(self.callback_team_create, status_code=422)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaisesRegexp(
                GitHubUnknownError, json.dumps({'id': 2})
        ):
            git_hub.put_team(
                self.ORG, 'New Team', True, self.TEST_TEAM_MEMBERS
            )

    @httpretty.activate
    def test_lib_put_team_membership_fail(self):
        """Change team membership successfully for team that exists."""
        self.register_team_list(self.callback_team_list)
        self.register_team_members(self.callback_team_members)
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, success=False)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaisesRegexp(
                GitHubUnknownError, '^Failed to add or remove.+$'
        ):
            git_hub.put_team(self.ORG, self.TEST_TEAM, True, [])

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
            course=self.TEST_COURSE,
            term=self.TEST_TERM,
            team=self.TEST_TEAM,
            description=self.TEST_DESCRIPTION,
        )

        # Now create repo with a new team
        member_changes = []
        member_list = ['fenris']
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_create(
            partial(self.callback_team_create, read_only=False)
        )
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, action_list=member_changes)
        )
        create_xml_repo(
            course=self.TEST_COURSE,
            term=self.TEST_TERM,
            team='Other Team',
            members=member_list,
            description=self.TEST_DESCRIPTION
        )
        self.assertItemsEqual(
            [(unicode(x), True) for x in member_list],
            member_changes
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_actions_put_team_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_XML_ORG = self.ORG
        config.ORC_XML_DEPLOY_TEAM = self.TEST_TEAM
        config.ORC_STAGING_GITRELOAD = self.TEST_STAGING_GR

        member_changes = []
        self.register_team_list(
            partial(self.callback_team_list, more=True)
        )
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_create(
            partial(self.callback_team_create, read_only=False)
        )
        self.register_team_memberhip(
            partial(self.callback_team_memberhip, action_list=member_changes)
        )

        put_team(
            org=self.ORG,
            team=self.TEST_TEAM,
            read_only=True,
            members=self.TEST_TEAM_MEMBERS
        )
        self.assertItemsEqual(
            [(unicode(x), True) for x in self.TEST_TEAM_MEMBERS],
            member_changes
        )
