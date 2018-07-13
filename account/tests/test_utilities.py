from django.contrib.auth.models import AnonymousUser


from core.test import TestCase

from .. import factories, utilities


class TestUtilities(TestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.UserFactory()
        
    def test_is_anonymous(self):
        self.assertFalse(utilities.user_is_anonymous(self.user))
        self.assertTrue(utilities.user_is_anonymous(AnonymousUser()))