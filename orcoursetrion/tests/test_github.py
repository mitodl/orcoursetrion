# -*- coding: utf-8 -*-
"""
Test github actions and backing library
"""
from functools import partial
import json
import os
import re
import shutil
import tempfile

import httpretty
import mock
import sh

from orcoursetrion.actions import (
    create_export_repo,
    rerun_studio,
    create_xml_repo,
    put_team,
    rerun_xml
)
from orcoursetrion.lib import (
    GitHub,
    GitHubRepoExists,
    GitHubUnknownError,
    GitHubNoTeamFound,
    GitHubRepoDoesNotExist
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
    def test_lib_get_all_bad_status(self):
        """Test how we handle _get_all getting a bad status code"""
        error = json.dumps({'error': 'error'})
        test_url = '{url}repos/{org}/{repo}/hooks'.format(
            url=self.URL,
            org=self.ORG,
            repo=self.TEST_REPO
        )
        self.register_hook_list(
            body=error,
            status=422
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaisesRegexp(GitHubUnknownError, re.escape(error)):
            git_hub._get_all(test_url)

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
    def test_lib_delete_hook_fail(self):
        """Test the deletion of hooks"""
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)

        # Test where repo does not exist
        self.register_repo_check(self.callback_repo_check)
        with self.assertRaises(GitHubRepoDoesNotExist):
            git_hub.delete_web_hooks(self.ORG, self.TEST_REPO)

        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )

        # Test no hooks to delete
        self.register_hook_list(status=404)
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # Will raise if hooks are found since I haven't registered
        # the hook delete URL.
        num_deleted_hooks = git_hub.delete_web_hooks(self.ORG, self.TEST_REPO)
        self.assertEqual(0, num_deleted_hooks)

        # Set list to return on hook that we have registered for
        # explicitly
        self.register_hook_list(body=json.dumps(
            [{
                'url': '{url}repos/{org}/{repo}/hooks/1'.format(
                    url=self.URL, org=self.ORG, repo=self.TEST_REPO
                )
            }]
        ))
        # Reregister ``repo_check`` 200
        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )
        # Fail the deletion
        self.register_hook_delete(status=422)
        with self.assertRaisesRegexp(GitHubUnknownError, ''):
            git_hub.delete_web_hooks(self.ORG, self.TEST_REPO)

    @httpretty.activate
    def test_lib_delete_hook_success(self):
        """Test successful hook deletion."""
        self.register_repo_check(
            partial(self.callback_repo_check, status_code=200)
        )
        self.register_hook_list(body=json.dumps(
            [{
                'url': '{url}repos/{org}/{repo}/hooks/1'.format(
                    url=self.URL, org=self.ORG, repo=self.TEST_REPO
                )
            }]
        ))
        self.register_hook_delete()
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        deleted_hooks = git_hub.delete_web_hooks(self.ORG, self.TEST_REPO)
        self.assertEqual(1, deleted_hooks)

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
                re.escape("No teams found in org. This shouldn't happen")
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
    def test_lib_add_team_repo_team_spaces_case_match(self):
        """The API sometimes returns spaces in team names, so make sure we
        still match when stripped. Additionally, be case insensitive
        since github is.
        """
        self.register_team_list(self.callback_team_list)
        self.register_team_repo_add(self.callback_team_repo)
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        # This will raise if we aren't stripping team names
        git_hub.add_team_repo(
            self.ORG, self.TEST_REPO, ' {0} '.format(self.TEST_TEAM)
        )
        # This will raise if we aren't doing lower()
        git_hub.add_team_repo(
            self.ORG, self.TEST_REPO, self.TEST_TEAM.upper()
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
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
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
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
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
        self.register_team_membership(
            partial(self.callback_team_membership, action_list=member_changes)
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
        self.register_team_membership(
            partial(self.callback_team_membership, success=False)
        )
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        with self.assertRaisesRegexp(
                GitHubUnknownError, '^Failed to add or remove.+$'
        ):
            git_hub.put_team(self.ORG, self.TEST_TEAM, True, [])

    def test_lib_copy_repo(self):
        """Verify that we can do a single commit, single branch copy of a
        repo."""

        from orcoursetrion import config

        commit_1 = 'hello'
        commit_2 = 'world'
        branch = 'foo'

        SRC_REPO = 'Thing1'
        DST_REPO = 'Thing2'

        prefix = 'orc_git_test'

        # Create directories to use.

        # Note: If you are getting weird errors about ``[No such file
        # or directory]: getcwd()`` when this test fails and you are
        # debugging, disable the cleanup here. Even with the cleanup
        # of changing the working directory below, pytest seems to run
        # and the working directory is the tmp directories we nuked in
        # cleanup.
        tmp_dir_src = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(shutil.rmtree, tmp_dir_src)
        tmp_dir_dst = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(shutil.rmtree, tmp_dir_dst)

        # Add cleanup to return to where we came from
        cwd = unicode(sh.pwd().rstrip('\n'))

        self.addCleanup(sh.cd, cwd)

        # Create a base repo with some commits, then
        # Run the copy and verify the results
        sh.cd(tmp_dir_src)
        sh.mkdir(SRC_REPO)
        sh.cd(SRC_REPO)
        git = sh.git.bake(_cwd=os.path.join(tmp_dir_src, SRC_REPO))
        git.init()
        git.config('user.email', config.ORC_GH_EMAIL)
        git.config('user.name', config.ORC_GH_NAME)
        for commit in [commit_1, commit_2]:
            with open('test', 'w') as test_file:
                test_file.write(commit)
            git.add('.')
            git.commit(m=commit_2)

        # Also create a branch to test branches
        git.checkout('-b', branch)
        with open('test', 'w') as test_file:
            test_file.write(branch)
        git.add('.')
        git.commit(m=branch)

        git.checkout('master')

        # Now create the initial bare repo at the destination
        sh.cd(tmp_dir_dst)
        sh.mkdir(DST_REPO)
        sh.cd(DST_REPO)
        sh.git.init(bare=True)

        # Alright, run the copy and verify the expected commit
        # message, and that the test file has the last commit string
        git_hub = GitHub(self.URL, self.OAUTH2_TOKEN)
        src_repo_url = 'file://{0}'.format(os.path.join(tmp_dir_src, SRC_REPO))
        dst_repo_url = 'file://{0}'.format(os.path.join(tmp_dir_dst, DST_REPO))

        git_hub.shallow_copy_repo(
            src_repo_url,
            dst_repo_url,
            {'email': config.ORC_GH_EMAIL, 'name': config.ORC_GH_NAME}
        )

        # Verify things are looking right.
        sh.cd(tmp_dir_dst)
        # Clone bare destination repo and verify contents
        DST_REPO_CLONE = 'cloned'
        sh.git.clone(dst_repo_url, DST_REPO_CLONE)
        sh.cd(DST_REPO_CLONE)

        # Assert file is as expected
        with open('test', 'r') as test_file:
            self.assertEqual(commit_2, test_file.read())
        git_log = sh.git.log(
            '-1', format='%s', _tty_out=False
        ).rstrip('\n')

        # Assert commit message is correct
        self.assertEqual(
            git_log,
            'Initial rerun copy by Orcoursetrion from {0}'.format(src_repo_url)
        )

        # Assert author is correct
        git_log = sh.git.log(
            '-1', format='%cn', _tty_out=False
        ).rstrip('\n')
        self.assertEqual(git_log, config.ORC_GH_NAME)
        git_log = sh.git.log(
            '-1', format='%ce', _tty_out=False
        ).rstrip('\n')
        self.assertEqual(git_log, config.ORC_GH_EMAIL)

        # Delete old clone and run it with a different branch
        sh.cd(tmp_dir_dst)
        shutil.rmtree(DST_REPO_CLONE)
        git_hub.shallow_copy_repo(
            src_repo_url,
            dst_repo_url,
            {'email': config.ORC_GH_EMAIL, 'name': config.ORC_GH_NAME},
            branch=branch
        )

        # Verify things are looking right in the branch clone
        sh.cd(tmp_dir_dst)
        # Clone bare destination repo and verify contents
        DST_REPO_CLONE = 'cloned'
        sh.git.clone(dst_repo_url, DST_REPO_CLONE)
        sh.cd(DST_REPO_CLONE)

        # Assert file is as expected
        with open('test', 'r') as test_file:
            self.assertEqual(branch, test_file.read())

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
    def test_actions_rerun_studio_success(self, config):
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

        rerun_studio(
            self.TEST_COURSE,
            self.TEST_TERM,
            self.TEST_NEW_TERM,
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
    def test_actions_rerun_xml_success(self, config):
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
