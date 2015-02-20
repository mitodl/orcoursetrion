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
    TEST_DESCRIPTION = 'foo'
    TEST_PREFIX = 'testo'
    TEST_REPO = '{0}-{1}-{2}'.format(
        TEST_PREFIX, TEST_COURSE.replace('.', ''), TEST_TERM
    )
    TEST_TEAM = 'Test-Deploy'
    TEST_TEAM_ID = 1
    TEST_TEAM_MEMBERS = ['archlight', 'bizarnage', 'chemistro', 'dreadnought']
    TEST_STAGING_GR = 'http://gr/'

    def callback_repo_check(self, request, uri, headers, status_code=404):
        """Handle mocked API request for repo existence check."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        return (status_code, headers, "testing")

    def callback_repo_create(self, request, uri, headers, status_code=201):
        """Mock repo creation API call."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        repo_dict = json.loads(request.body)
        self.assertEqual(repo_dict['name'], self.TEST_REPO)
        self.assertEqual(repo_dict['description'], self.TEST_DESCRIPTION)
        self.assertEqual(repo_dict['private'], True)

        return (status_code, headers, json.dumps({'html_url': 'testing'}))

    def callback_team_list(
            self, request, uri, headers, status_code=200, more=False
    ):
        """Mock team listing API call."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        page1 = [
            {
                'id': 1,
                'name': self.TEST_TEAM
            },
        ]
        page2 = [
            {
                'id': 2,
                'name': 'Owners'
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
        return (status_code, headers, json.dumps(body))

    def callback_team_members(
            self, request, uri, headers,
            status_code=200, members=TEST_TEAM_MEMBERS
    ):
        """
        Return team membership list
        """
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

    def callback_team_memberhip(
            self, request, uri, headers, success=True, action_list=None
    ):
        """Manage both add and delete of team membership.

        ``action_list`` is a list of tuples with (``username``,
        ``added (bool)``) to track state of membership since this will
        get called multiple times in one library call.
        """
        username = uri.rsplit('/', 1)[1]
        if request.method == 'DELETE':
            if success:
                status_code = 204
                action_list.append((username, False))
            else:
                status_code = 500
        if request.method == 'PUT':
            if success:
                status_code = 200
                action_list.append((username, True))
            else:
                status_code = 422
        return (status_code, headers, '')

    def callback_team_repo(self, request, uri, headers, status_code=204):
        """Mock adding a repo to a team API call."""
        self.assertEqual(
            request.headers['Authorization'],
            'token {0}'.format(self.OAUTH2_TOKEN)
        )
        self.assertEqual('{url}teams/{id}/repos/{org}/{repo}'.format(
            url=self.URL,
            id=self.TEST_TEAM_ID,
            org=self.ORG,
            repo=self.TEST_REPO
        ), uri)
        if status_code == 422:
            return (status_code, headers, json.dumps({
                "message": "Validation Failed",
            }))
        return (status_code, headers, '')

    def register_repo_check(self, body):
        """Register repo check URL and method."""
        httpretty.register_uri(
            httpretty.GET,
            '{url}repos/{org}/{repo}'.format(
                url=self.URL,
                org=self.ORG,
                repo=self.TEST_REPO
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
                '^{url}teams/\d+/members$'.format(
                    url=re.escape(self.URL)
                )
            ),
            body=body
        )

    def register_team_memberhip(self, body):
        """
        Register adding and removing team members.
        """
        url_regex = re.compile('^{url}teams/\d+/memberships/\w+$'.format(
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
            '{url}teams/{id}/repos/{org}/{repo}'.format(
                url=self.URL,
                id=self.TEST_TEAM_ID,
                org=self.ORG,
                repo=self.TEST_REPO
            ),
            body=body
        )
