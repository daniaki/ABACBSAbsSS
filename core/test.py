from django import test

from account.models import UserGroups


class TestCase(test.TestCase):
    """Sets up the test environment by creating user groups."""
    def setUp(self):
        UserGroups.create_groups()