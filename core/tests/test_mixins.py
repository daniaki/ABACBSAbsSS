from django import forms
from django.test import TestCase

from account.factories import UserFactory

from .. import mixins


class MockUserKwargsForm(mixins.UserKwargsMixin, forms.Form):
    user_kwarg = 'user'
    field = forms.BooleanField()
    
    
class TestMixins(TestCase):
    def test_kwarg_mixin_sets_user(self):
        user = UserFactory()
        form = MockUserKwargsForm(user=user)
        self.assertEqual(form.user, user)
        
    def test_kwarg_mixin_sets_user_as_none_if_not_supplied(self):
        form = MockUserKwargsForm(user=None)
        self.assertIsNone(form.user)
        
        form = MockUserKwargsForm()
        self.assertIsNone(form.user)
        
    def test_error_not_none_or_user(self):
        with self.assertRaises(TypeError):
            MockUserKwargsForm(user=[])
    