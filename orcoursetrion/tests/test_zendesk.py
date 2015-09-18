import unittest
import vcr
from orcoursetrion.lib import (
    ZenDesk,
    ZenDeskUnknownError,
    ZenDeskNoUserFound,
    ZenDeskNoGroupFound,
    ZenDeskNoTicketFound
)
from orcoursetrion import config


class TestZenDesk(unittest.TestCase):
    """Test ZenDesk backing library"""

    def setUp(self):
        self.zendesk = ZenDesk(config.ORC_ZD_API_URL,
                               config.ORC_ZD_EMAIL,
                               config.ORC_ZD_AUTH_TOKEN)
        self.test_ticket_id = 3060  # TODO: Fix this

    @vcr.use_cassette(
        'cassettes/zendesk/get_all.yml',
        filter_headers=['authorization']
    )
    def test_get_all(self):
        """
        Test protected method _find_user()
        """
        self.assertIsNotNone(self.zendesk._get_all('groups'))
        self.assertRaises(ZenDeskUnknownError, self.zendesk._get_all('foo'))

    @vcr.use_cassette(
        'cassettes/zendesk/get_ticket.yml',
        filter_headers=['authorization']
    )
    def test_get_ticket(self):
        """
        Test get_ticket method.
        """
        self.assertIsNotNone(self.zendesk._get_ticket('2700'))
        with self.assertRaises(ZenDeskNoTicketFound):
            self.zendesk._get_ticket('florp')

    @vcr.use_cassette(
        'cassettes/zendesk/find_group.yml',
        filter_headers=['authorization']
    )
    def test_find_group(self):
        """
        Test find_group method
        """
        self.assertIsNotNone(self.zendesk._find_group('test'))
        with self.assertRaises(ZenDeskNoGroupFound):
            self.zendesk._find_group('florp')

    @vcr.use_cassette(
        'cassettes/zendesk/find_user.yml',
        filter_headers=['authorization']
    )
    def test_find_user(self):
        """
        Test find_user method
        """
        self.assertIsNotNone(self.zendesk._find_user('noreply@zendesk.com'))
        with self.assertRaises(ZenDeskNoUserFound):
            self.zendesk._find_user('florp')

    @vcr.use_cassette(
        'cassettes/zendesk/create_ticket.yml',
        filter_headers=['authorization']
    )
    def test_create_ticket(self):
        """
        Test create_ticket method
        """
        self.assertIsNotNone(
            self.zendesk.create_ticket(
                'This is but a test',
                'noreply@zendesk.com',
                'test',
                'This is just a trial run.',
                public=True
            )
        )
        with self.assertRaises(ZenDeskNoUserFound):
            self.zendesk.create_ticket(
                'florp',
                'florp',
                'test',
                'florp',
                public=True
            )
        with self.assertRaises(ZenDeskNoGroupFound):
            self.zendesk.create_ticket(
                'florp',
                'noreply@zendesk.com',
                'florp',
                'florp',
                public=True
            )

    @vcr.use_cassette(
        'cassettes/zendesk/update_ticket.yml',
        filter_headers=['authorization']
    )
    def test_update_ticket(self):
        """
        Tests the update_ticket method works in all permutations.
        """
        self.assertIsNotNone(
            self.zendesk.update_ticket(
                self.test_ticket_id,
                'this is but a test'
            )
        )
        self.assertIsNotNone(
            self.zendesk.update_ticket(
                self.test_ticket_id,
                'this is but a toast',
                public=True
            )
        )
        self.assertIsNotNone(
            self.zendesk.update_ticket(
                self.test_ticket_id,
                'this is but a toss',
                public=True,
                status="pending"
            )
        )
        self.assertIsNotNone(
            self.zendesk.update_ticket(
                self.test_ticket_id,
                'this is but a jest',
                status="solved"
            )
        )
        self.assertIsNotNone(
            self.zendesk.update_ticket(
                self.test_ticket_id,
                status="closed"
            )
        )
        with self.assertRaises(ZenDeskUnknownError):
            self.zendesk.update_ticket(
                8675309,
                'this update is built to break'
            )

    @vcr.use_cassette(
        'cassettes/zendesk/create_user.yml',
        filter_headers=['authorization']
    )
    def test_create_user(self):
        """
        Test create_user method.
        """
        self.assertIsNotNone(
            self.zendesk.create_user(
                "noreply@zendesk.com",
                "ZenDesk"
            )
        )

        with self.assertRaises(ZenDeskUnknownError):
            self.zendesk.create_user(
                "noreply",
                "ZD"
            )
