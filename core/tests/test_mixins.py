from django import forms
from django.test import TestCase

from account.factories import UserFactory

from .. import mixins


class MockForm(mixins.UserKwargsForm, forms.Form):
    field = forms.BooleanField()


class TestMixins(TestCase):
    def test_kwarg_mixin_sets_user(self):
        user = UserFactory()
        form = MockForm(user=user)
        self.assertEqual(form.user, user)
        
    def test_kwarg_mixin_sets_user_as_none_if_not_supplied(self):
        form = MockForm(user=None)
        self.assertIsNone(form.user)
        
        form = MockForm()
        self.assertIsNone(form.user)
        
    def test_error_not_none_or_user(self):
        with self.assertRaises(TypeError):
            MockForm(user=[])
        