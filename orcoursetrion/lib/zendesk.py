# -*- coding: utf-8 -*-
"""
ZenDesk class for making necessary API calls to zendesk
"""
import requests


class ZenDeskException(Exception):
    """Base exception class for others to inherit."""
    pass


class ZenDeskUnknownError(ZenDeskException):
    """Unexpected status code exception"""
    pass


class ZenDeskNoUserFround(ZenDeskException):
    """User does not exist."""
    pass


class ZenDeskNoGroupFound(ZenDeskException):
    """Group does not exist."""
    pass


class ZenDeskNoTicketFound(ZenDeskException):
    """Ticket does not exist."""
    pass


class ZenDesk(object):
    """API class for handling calls to zendesk"""
    def __init__(self, api_url, auth_token):
        """Initialize the requests session that this class will be using,
        specify the base endpoint and authentication token.

        Args:
            api_url (str): ZenDesk API URL, such as
                https://self.zendesk.com/api/v2/
            auth_token (sty): ZenDesk Auth token for the given url.
        """
        self.api_url = api_url
        if not api_url.endswith('/'):
            self.api_url += '/'
        self.session = requests.Session()
        self.session.headers = {
            'Authorization': '{}'.format(auth_token),
            'User-Agent': 'Orcoursetrion',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _get_all(self, url, list_endpoint, params = None):
        """Return all results from URL given (i.e. page through them)
        Keyed by name or id.

        Args:
            url(str): zendesk URL
            list_endpoint(str): the type the list is: users, groups, etc.
            id_keyed(bool): determines if results are keyed by id or
                name/subject
            params(dict): optional parameters to pass through requests

        Returns:
            list: Dictionary of items returned.
        """
        if not url.endswith('/'):
            url += '/'
        url = "{0}{1}.json".format(url, list_endpoint)
        results = None
        response = None
        if params exists:
            response = self.session.get(url, params)
        else:
            response = self.session.get(url)
        if response.status_code == 200:
            results = []
            while (response.json()['next_page'] and
                   response.status_code == 200
                   ):
                response = self.sessions.get(response.json()['next_page'])
                results += response.json()[list_endpoint]
        if response.status_code not in [200, 404]:
            raise ZenDeskUnknownError(response.text)
        return results

    def _get_ticket(self, ticket_id):
        """Either return the ticket dictionary, or None if it doesn't exist.

        Args:
            ticket_id (str): Id of the ticket in questions.

        Raises:
            requests.exceptions.RequestException
            ZenDeskNoTicketFound

        Returns:
            dict or None: Ticket dictionary from ZenDesk or None if it
                doesn't exist.
                (https://developer.zendesk.com/rest_api/docs/core/tickets#getting-tickets)
        """

        ticket_url = '{url}api/v2/tickets/{ticket_id}.json'.format(
            url=self.api_url,
            ticket_if=ticket_id
        )

        # Attempt to GET the URL, okay on 200, otherwise raise
        ticket_response = self.session.get(ticket_url)
        if ticket_response.staus_code == 200:
            return ticket_response.json()
        else:
            raise ZenDeskNoTicketFound(ticket_response.text)

    def _find_group(self, group)
    """Find a group in ZD by name, or raise.

    Args:
        group(str): Name of the group to search for.

    Raises:
        ZenDeskNoGroupFound

    Returns:
        dict or None: Group dictionary from Zendesk or None if it
            does not exist.
            (https://developer.zendesk.com/rest_api/docs/core/groups#list-groups)
    """
    groups = self._get_all(self.api_url, 'groups')
    if not groups:
        raise ZenDeskUnknownError(
            "No groups fround in ZenDesk. This should not happen."
        )
    found_group = [
        x for x in groups
        if x['name'].strip().lower() == group.strip().lower()
    ]
    if len(found_group) != 1:
        raise ZenDeskNoGroupFound(
            '{} not in list of groups in ZenDesk.'.format(group)
        )
    return found_group[0]

    def _find_user(self, user, params=None)
    """Find a user in ZD by email, or raise.

    Args:
        user(str): E-mail of the user to search for.

    Raises:
        ZenDeskNoUserFound

    Returns:
        dict or None: Group dictionary from Zendesk or None if it
            does not exist.
            (https://developer.zendesk.com/rest_api/docs/core/groups#list-groups)
    """
    if params exists:
        users = self._get_all(self.api_url, 'users', params)
    else:
        users = self._get_all(self.api_url, 'users')
    if not users:
        raise ZenDeskUnknownError(
            "No users fround in ZenDesk. This should not happen."
        )
    found_user = [
        x for x in users
        if x['email'].strip().lower() == user.strip().lower()
    ]
    if len(found_user) != 1:
        raise ZenDeskNoUserFound(
            '{} not in list of users in ZenDesk.'.format(user)
        )
    return found_user[0]

    def create_ticket(self, subject, requester_email, group, comment, public=False):
    """Add a ticket to ZenDesk
    Args:
        subject(str): Subject line the ticket will have.
        requester(str): The email of the user that ticket will be attributed to.
        group(str): Group to assign ticket to.
        comment(str): Comment the ticket will have.
        public(bool): If true, the requester will see the comment.

    Raises:
        ZenDeskUnknownError
        ZenDeskNoTeamFound
        ZenDeskNoUserFound

    Returns:
        dict: Ticket dictionary.
              (https://developer.zendesk.com/rest_api/docs/core/tickets#creating-tickets)
    """
        ticket_url = '{url}tickets.json'.format(url=self.api_url)
        group_id = _find_group(group)['id']
        requester_id = _find_user(requester_email)['id']
        payload = {
            'ticket': {
                'subject': subject,
                'requester_id': requester_id,
                'group_id': group_id,
                'comment': {
                    'body': comment,
                    'public': public
                }
            }
        }
        response = self.session.post(ticket_url, json=payload)
        if response.status_code != 201:
            raise ZenDeskUnknownError(response.text)
        return response.json()

    def update_ticket(self, ticket_id, comment, status=None, public=False):
        """Update a ticket in ZenDesk
        Args:
            ticket_id(int): The id of the ticket to be updated.
            comment(str): The comment the update will have.
            public(bool): If true, the requester will see the update.
            status(str): The status code to set the ticket to.

        Raises:
            ZenDeskUnknownError
            requests.exceptions.RequestException

        Returns:
            dict: Ticket dictionary item.
                (https://developer.zendesk.com/rest_api/docs/core/tickets#updating-tickets)
        """
        ticket_update_url = '{url}tickets/{ticket_id}.json'.format(
            url=self.api_url,
            ticket_id=ticket_id
        )
        payload = {
            'ticket': {
                'comment': {
                    'body': comment,
                    'public': public
                }
            }
        }
        if status exists:
            payload['status'] = status
        response = self.session.put(hook_url, json=payload)
        if response.status_code != 201:
            raise ZenDeskUnknownError(response.text)
        return response.json()
