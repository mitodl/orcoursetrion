# -*- coding: utf-8 -*-
"""
Test base class with commonly used methods and variables
"""
import json
import unittest


class TestGithubBase(unittest.TestCase):
    """Test Github actions and backing library."""

    OAUTH2_TOKEN = '12345'
    ORG = 'NOT_REAL'
    URL = 'http://localhost/'

    TEST_COURSE = 'devops.001'
    TEST_TERM = 'Spring_2999'
    TEST_DESCRIPTION = 'foo'
    TEST_PREFIX = 'testo'
    TEST_REPO = '{0}-{1}-{2}'.format(
        TEST_PREFIX, TEST_COURSE.replace('.', ''), TEST_TERM
    )

    def callback_repo_check(self, request, uri, headers, status_code=404):
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        return (status_code, headers, "testing")

    def callback_repo_create(self, request, uri, headers, status_code=201):
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        repo_dict = json.loads(request.body)
        self.assertEqual(repo_dict['name'], self.TEST_REPO)
        self.assertEqual(repo_dict['description'], self.TEST_DESCRIPTION)
        self.assertEqual(repo_dict['private'], True)

        return (status_code, headers, json.dumps({'html_url': 'testing'}))
