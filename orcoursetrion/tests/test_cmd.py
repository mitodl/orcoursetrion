# -*- coding: utf-8 -*-
"""
Test command line parsing and actions
"""
import mock

from orcoursetrion.cmd import execute
from orcoursetrion.tests.base import TestGithubBase


class TestGithubCommand(TestGithubBase):
    """Verify github commands via command line"""

    def test_cmd_create_export_repo(self):
        """
        Command line test of create_export_repo
        """
        args = [
            'orcoursetrion', 'create_export_repo',
            '-c', self.TEST_COURSE,
            '-t', self.TEST_TERM,
            '-d', self.TEST_DESCRIPTION,
        ]
        with mock.patch('sys.argv', args):
            with mock.patch('orcoursetrion.cmd.actions') as mocked_actions:
                execute()
                self.assertTrue(mocked_actions.create_export_repo.called)
                mocked_actions.create_export_repo.assert_called_with(
                    self.TEST_COURSE, self.TEST_TERM, self.TEST_DESCRIPTION
                )

    def test_cmd_create_xml_repo(self):
        """
        Command line test of create_export_repo
        """

        args = [
            'orcoursetrion', 'create_xml_repo',
            '-c', self.TEST_COURSE,
            '-t', self.TEST_TERM,
            '-d', self.TEST_DESCRIPTION,
            '-g', self.TEST_TEAM,
        ]
        with mock.patch('sys.argv', args):
            with mock.patch('orcoursetrion.cmd.actions') as mocked_actions:
                execute()
                self.assertTrue(mocked_actions.create_xml_repo.called)
                mocked_actions.create_xml_repo.assert_called_with(
                    self.TEST_COURSE,
                    self.TEST_TERM,
                    self.TEST_TEAM,
                    self.TEST_DESCRIPTION
                )
