from django.contrib.auth.models import AnonymousUser
from django.core import mail


from core.test import TestCase

from .. import factories, utilities


class TestUtilities(TestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.UserFactory()
        
    def test_is_anonymous(self):
        self.assertFalse(utilities.user_is_anonymous(self.user))
        self.assertTrue(utilities.user_is_anonymous(AnonymousUser()))
        
    def test_pw_reset(self):
        old_pw = self.user.password
        utilities.reset_password(self.user.profile)
        self.assertEqual(len(mail.outbox), 1)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, old_pw)