from django.contrib.auth import get_user_model

from core.test import TestCase

from .. import factories
from ..templatetags import user_tags


User = get_user_model()


class TestTags(TestCase):
    
    def test_returns_list_of_full_names(self):
        user = factories.UserFactory()
        self.assertListEqual(
            user_tags.users_full_name([user]),
            [user.profile.full_name]
        )
    
    def test_returns_none(self):
        self.assertIsNone(user_tags.users_full_name(None))
        self.assertFalse(user_tags.users_full_name([]))