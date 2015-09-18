# -*- coding: utf-8 -*-
"""
Test base class with commonly used methods and variables
"""
import json
import re
import unittest

import httpretty


class TestGithubBase(unittest.TestCase):
    """Test Github actions and backing library."""

    OAUTH2_TOKEN = '12345'
    ORG = 'NOT_REAL'
    URL = 'http://localhost/'

    TEST_COURSE = 'devops.001'
    TEST_TERM = 'Spring_2999'
    TEST_NEW_TERM = 'Spring_9999'
    TEST_DESCRIPTION = 'foo'
    TEST_PREFIX = 'testo'
    TEST_REPO = '{0}-{1}-{2}'.format(
        TEST_PREFIX, TEST_COURSE.replace('.', ''), TEST_TERM
    )
    TEST_RERUN_REPO = '{0}-{1}-{2}'.format(
        TEST_PREFIX, TEST_COURSE.replace('.', ''), TEST_NEW_TERM
    )
    TEST_TEAM = 'Test-Deploy'
    TEST_TEAM_ID = 1
    TEST_TEAM_MEMBERS = ['archlight', 'bizarnage', 'chemistro', 'dreadnought']
    TEST_STAGING_GR = 'http://gr/'
    TEST_PRODUCTION_GR = 'http://prod-gr/'

    def callback_repo_check(self, request, uri, headers, status_code=404):
        """Handle mocked API request for repo existence check."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        # Handle the new "rerun" repo differently
        if self.TEST_RERUN_REPO in uri:
            status_code = 404
        return (status_code, headers, json.dumps({'message': 'testing'}))

    def callback_repo_create(self, request, uri, headers, status_code=201):
        """Mock repo creation API call."""
        # Disabling unused-argument because this is a callback with
        # required method signature.
        # pylint: disable=unused-argument
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        repo_dict = json.loads(request.body)
        self.assertTrue(
            repo_dict['name'] in [self.TEST_REPO, self.TEST_RERUN_REPO]
        )
        self.assertEqual(repo_dict['description'], self.TEST_DESCRIPTION)
        self.assertEqual(repo_dict['private'], True)

        return (status_code, headers, json.dumps({'html_url': 'testing'}))

    def callback_team_list(
            self, request, uri, headers, status_code=200, more=False
    ):
        """Mock team listing API call."""
        # All arguments needed for tests
        # pylint: disable=too-many-arguments
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        page1 = [
            {
                'id': 1,
                'name': self.TEST_TEAM
            },

            {
                'id': 1,
                'name': self.TEST_REPO
            }
        ]
        page2 = [
            {
                'id': 3,
                'name': 'Other Team'
            },
        ]
        current_page = request.querystring.get('page', [u'1'])
        current_page = int(current_page[0])
        if current_page == 2:
            body = page2
        else:
            body = page1
        if more and current_page == 1:
            headers['Link'] = (
                '<{uri}?page=2>; rel="next",'
                '<{uri}?page=2>; rel="last"'
            ).format(uri=uri)
        if status_code == 404:
            return (status_code, headers, json.dumps({'error': 'error'}))
        return (status_code, headers, json.dumps(body))

    def callback_team_members(
            self, request, uri, headers,
            status_code=200, members=None
    ):
        """
        Return team membership list
        """
        # Disabling unused-argument because this is a callback with
        # required method signature.
        # pylint: disable=unused-argument,too-many-arguments
        if members is None:
            members = self.TEST_TEAM_MEMBERS
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        return (status_code, headers, json.dumps(
            [dict(login=x) for x in members]
        ))

    def callback_team_create(
            self, request, uri, headers, status_code=201, read_only=True
    ):
        """
        Create a new team as requested
        """
        # Disabling unused-argument because this is a callback with
        # required method signature.
        # pylint: disable=unused-argument,too-many-arguments
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        json_body = json.loads(request.body)
        for item in ['name', 'permission']:
            self.assertTrue(item in json_body.keys())
        if read_only:
            self.assertEqual(json_body['permission'], 'pull')
        else:
            self.assertEqual(json_body['permission'], 'push')
        return (status_code, headers, json.dumps({'id': 2}))

    @staticmethod
    def callback_team_membership(
            request, uri, headers, success=True, action_list=None
    ):
        """Manage both add and delete of team membership.

        ``action_list`` is a list of tuples with (``username``,
        ``added (bool)``) to track state of membership since this will
        get called multiple times in one library call.
        """
        # pylint: disable=too-many-arguments

        username = uri.rsplit('/', 1)[1]
        if not success:
            status_code = 500

        if request.method == 'DELETE':
            if success:
                status_code = 204
                action_list.append((username, False))
        if request.method == 'PUT':
            status_code = 200
            action_list.append((username, True))
        return (status_code, headers, '')

    def callback_team_repo(self, request, uri, headers, status_code=204):
        """Mock adding a repo to a team API call."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        self.assertIsNotNone(re.match(
            '{url}teams/[13]/repos/{org}/({repo}|{rerun_repo})'.format(
                url=re.escape(self.URL),
                org=self.ORG,
                repo=re.escape(self.TEST_REPO),
                rerun_repo=re.escape(self.TEST_RERUN_REPO)
            ),
            uri
        ))
        if status_code == 422:
            return (status_code, headers, json.dumps({
                "message": "Validation Failed",
            }))
        return (status_code, headers, '')

    def register_repo_check(self, body):
        """Register repo check URL and method."""
        httpretty.register_uri(
            httpretty.GET,
            re.compile(
                '^{url}repos/{org}/({repo}|{repo_rerun})$'.format(
                    url=self.URL,
                    org=self.ORG,
                    repo=re.escape(self.TEST_REPO),
                    repo_rerun=re.escape(self.TEST_RERUN_REPO)
                )
            ),
            body=body
        )

    def register_repo_create(self, body):
        """Register url for repo create."""
        httpretty.register_uri(
            httpretty.POST,
            '{url}orgs/{org}/repos'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=body
        )

    def register_hook_create(self, body, status):
        """
        Simple hook creation URL registration.
        """
        test_url = '{url}repos/{org}/{repo}/hooks'.format(
            url=self.URL,
            org=self.ORG,
            repo=self.TEST_REPO
        )
        # Register for hook endpoint
        httpretty.register_uri(
            httpretty.POST,
            test_url,
            body=body,
            status=status
        )

    def register_hook_list(self, body=None, status=200):
        """
        Simple hook list URL.
        """
        if body is None:
            body = json.dumps(
                [{
                    'url': '{url}repos/{org}/{repo}/hooks/1'.format(
                        url=self.URL, org=self.ORG, repo=self.TEST_REPO
                    )
                }]
            )
        test_url = '{url}repos/{org}/{repo}/hooks'.format(
            url=self.URL,
            org=self.ORG,
            repo=self.TEST_REPO
        )
        # Register for hook endpoint
        httpretty.register_uri(
            httpretty.GET,
            test_url,
            body=body,
            status=status
        )

    def register_hook_delete(self, status=204):
        """
        Simple hook list URL.
        """
        test_url = '{url}repos/{org}/{repo}/hooks/1'.format(
            url=self.URL,
            org=self.ORG,
            repo=self.TEST_REPO
        )
        # Register for hook endpoint
        httpretty.register_uri(
            httpretty.DELETE,
            test_url,
            body='',
            status=status
        )

    def register_team_list(self, body):
        """
        Team listing API.
        """
        httpretty.register_uri(
            httpretty.GET,
            '{url}orgs/{org}/teams'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=body
        )

    def register_team_create(self, body):
        """
        Create team URL/method
        """
        httpretty.register_uri(
            httpretty.POST,
            '{url}orgs/{org}/teams'.format(
                url=self.URL,
                org=self.ORG,
            ),
            body=body
        )

    def register_team_members(self, body):
        """
        Team membership list API.
        """
        httpretty.register_uri(
            httpretty.GET,
            re.compile(
                r'^{url}teams/\d+/members$'.format(
                    url=re.escape(self.URL)
                )
            ),
            body=body
        )

    def register_team_membership(self, body):
        """
        Register adding and removing team members.
        """
        url_regex = re.compile(r'^{url}teams/\d+/memberships/\w+$'.format(
            url=re.escape(self.URL),
        ))
        httpretty.register_uri(
            httpretty.PUT, url_regex, body=body
        )
        httpretty.register_uri(
            httpretty.DELETE, url_regex, body=body
        )

    def register_team_repo_add(self, body):
        """
        Register team repo addition.
        """
        httpretty.register_uri(
            httpretty.PUT,
            re.compile(
                r'^{url}teams/\d+/repos/{org}/({repo}|{rerun_repo})$'.format(
                    url=self.URL,
                    org=self.ORG,
                    repo=re.escape(self.TEST_REPO),
                    rerun_repo=re.escape(self.TEST_RERUN_REPO)
                )
            ),
            body=body
        )

    def register_create_file(self, status=201):
        """
        File creation API
        """
        httpretty.register_uri(
            httpretty.PUT,
            re.compile(
                r'^{url}repos/{org}/{repo}/contents/.+$'.format(
                    url=re.escape(self.URL),
                    org=re.escape(self.ORG),
                    repo=re.escape(self.TEST_REPO),
                )
            ),
            status=status
        )
