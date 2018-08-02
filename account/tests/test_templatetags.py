from django.contrib.auth import get_user_model

from core.test import TestCase

from abstract.factories import PresentationCategoryFactory, AbstractFactory

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
        
    def test_has_category(self):
        a = AbstractFactory()
        a.categories.clear()
        c1 = PresentationCategoryFactory(text='C1')
        c2 = PresentationCategoryFactory(text='C2')
        a.categories.add(c1)
        self.assertTrue(user_tags.has_category(c1, a))
        self.assertFalse(user_tags.has_category(c2, a))