# -*- coding: utf-8 -*-
"""
Test github actions and backing library
"""
# Because pylint can't figure out dynamic attributes for config or sh
# pylint: disable=no-member

from functools import partial
import json

import httpretty
import mock

from orcoursetrion.actions import (
    create_export_repo,
    rerun_studio,
    release_studio,
    create_xml_repo,
    rerun_xml,
    release_xml,
    put_team,
)
from orcoursetrion.actions.github import (
    COMMITTER,
    GITIGNORE_CONTENTS,
    GITIGNORE_MESSAGE,
    GITIGNORE_PATH
)
from orcoursetrion.tests.base import TestGithubBase


class TestActions(TestGithubBase):
    """Test Github actions"""

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_create_export_repo_success(self, config):
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

        # Mocking out add_repo_file due to it needing the repo to exist
        # but other items in this test need it to not exist
        with mock.patch(
            'orcoursetrion.actions.github.GitHub.add_repo_file'
        ) as mock_add_file:
            create_export_repo(
                self.TEST_COURSE,
                self.TEST_TERM,
                description=self.TEST_DESCRIPTION
            )
            mock_add_file.assert_called_with(
                org=config.ORC_STUDIO_ORG,
                repo='{prefix}-{course}-{term}'.format(
                    prefix=self.TEST_PREFIX,
                    course=self.TEST_COURSE.replace('.', ''),
                    term=self.TEST_TERM
                ),
                committer=COMMITTER,
                message=GITIGNORE_MESSAGE,
                path=GITIGNORE_PATH,
                contents=GITIGNORE_CONTENTS
            )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_rerun_studio_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_STUDIO_ORG = self.ORG
        config.ORC_STUDIO_DEPLOY_TEAM = self.TEST_TEAM

        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )
        self.register_repo_create(self.callback_repo_create)
        self.register_team_list(
            partial(self.callback_team_list, more=True)
        )
        self.register_team_repo_add(self.callback_team_repo)
        self.register_hook_list()
        self.register_hook_delete()

        # Mocking out add_repo_file due to it needing the repo to exist
        # but other items in this test need it to not exist.
        with mock.patch(
            'orcoursetrion.actions.github.GitHub.add_repo_file'
        ) as mock_add_file:

            rerun_studio(
                self.TEST_COURSE,
                self.TEST_TERM,
                self.TEST_NEW_TERM,
                description=self.TEST_DESCRIPTION
            )

            mock_add_file.assert_called_with(
                org=config.ORC_STUDIO_ORG,
                repo='{prefix}-{course}-{term}'.format(
                    prefix=self.TEST_PREFIX,
                    course=self.TEST_COURSE.replace('.', ''),
                    term=self.TEST_NEW_TERM
                ),
                committer=COMMITTER,
                message=GITIGNORE_MESSAGE,
                path=GITIGNORE_PATH,
                contents=GITIGNORE_CONTENTS
            )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_release_studio_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_STUDIO_ORG = self.ORG
        config.ORC_PRODUCTION_GITRELOAD = self.TEST_PRODUCTION_GR

        self.register_hook_create(json.dumps({'id': 2}), status=201)
        self.register_team_repo_add(self.callback_team_repo)

        release_studio(
            self.TEST_COURSE,
            self.TEST_TERM,
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_create_xml_repo_success_old_team(self, config):
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

        # Create a repo with an old team.
        create_xml_repo(
            course=self.TEST_COURSE,
            term=self.TEST_TERM,
            team=self.TEST_TEAM,
            description=self.TEST_DESCRIPTION,
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_create_xml_repo_success_new_team(self, config):
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

        # Now create repo with a new team
        member_changes = []
        member_list = ['fenris']
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_create(
            partial(self.callback_team_create, read_only=False)
        )
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
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
    def test_create_xml_repo_success_no_team(self, config):
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

        # Now create repo without a team
        member_changes = []
        member_list = ['andrea', 'andreas']
        self.register_team_members(
            partial(self.callback_team_members, members=[])
        )
        self.register_team_create(
            partial(self.callback_team_create, read_only=False)
        )
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
        )
        create_xml_repo(
            course=self.TEST_COURSE,
            term=self.TEST_TERM,
            members=member_list,
            description=self.TEST_DESCRIPTION
        )
        self.assertItemsEqual(
            [(unicode(x), True) for x in member_list],
            member_changes
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_rerun_xml_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_XML_ORG = self.ORG

        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )
        self.register_hook_list()
        self.register_hook_delete()
        hooks_deleted = rerun_xml(self.TEST_COURSE, self.TEST_TERM)
        self.assertEqual(1, hooks_deleted)

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_release_xml_success(self, config):
        """Test the API call comes through as expected.
        """
        config.ORC_GH_OAUTH2_TOKEN = self.OAUTH2_TOKEN
        config.ORC_GH_API_URL = self.URL
        config.ORC_COURSE_PREFIX = self.TEST_PREFIX
        config.ORC_XML_ORG = self.ORG
        config.ORC_PRODUCTION_GITRELOAD = self.TEST_PRODUCTION_GR

        self.register_hook_create(json.dumps({'id': 2}), status=201)
        self.register_team_repo_add(self.callback_team_repo)

        release_xml(
            self.TEST_COURSE,
            self.TEST_TERM,
        )

    @mock.patch('orcoursetrion.actions.github.config')
    @httpretty.activate
    def test_put_team_success(self, config):
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
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
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
