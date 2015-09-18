# -*- coding: utf-8 -*-
"""
ZenDesk class for making necessary API calls to zendesk
"""
import requests


class ZenDeskException(Exception):
    """Base exception class for others to inherit."""
    pass


class ZenDeskTicketDoesNotExist(ZenDeskException):
    """Ticket does not exists, so nothing can be done to it."""
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
