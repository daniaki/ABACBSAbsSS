import mock

from django import forms
from django.test import TestCase, RequestFactory
from django.views.generic import TemplateView
from datetime import timedelta
from django.utils import timezone

from account.factories import UserFactory

from .. import mixins, test


class MockUserKwargsForm(mixins.UserKwargsMixin, forms.Form):
    user_kwarg = 'user'
    field = forms.BooleanField()


class MockView(mixins.CheckClosingDateMixin, TemplateView):
    closing_dates = [(timezone.now() - timedelta(days=1)).astimezone(
        tz=timezone.get_current_timezone()),]
    template_name = 'account/profile.html'
    ignore_for_debug = False


#  -------------- Test Classes --------------------------------------------- #
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
    

class TestClosingDateMixin(TestCase, test.TestMessageMixin):
    def setUp(self):
        self.factory = RequestFactory()
    
    @mock.patch('core.mixins.add_closed_message')
    def test_calls_redirect_if_closing_date_passed(self, patch):
        MockView.closing_dates = [(timezone.now() - timedelta(days=1)).astimezone(
        tz=timezone.get_current_timezone()),]
        MockView.ignore_for_debug = False
        request = self.create_request('get', path='/')
        MockView.as_view()(request)
        patch.assert_called()

    @mock.patch('core.mixins.add_closed_message')
    def test_does_not_call_redirect_if_closing_date_has_NOT_passed(self, patch):
        MockView.closing_dates = [(timezone.now() + timedelta(days=1)).astimezone(
        tz=timezone.get_current_timezone()),]
        MockView.ignore_for_debug = False
        request = self.create_request('get', path='/')
        MockView.as_view()(request)
        patch.assert_not_called()
        
    @mock.patch('core.mixins.add_closed_message')
    def test_does_not_call_redirect_if_closing_date_has_passed_and_ignore_is_true(self, patch):
        MockView.closing_dates = [(timezone.now() - timedelta(days=1)).astimezone(
        tz=timezone.get_current_timezone()),]
        MockView.ignore_for_debug = True
        request = self.create_request('get', path='/')
        MockView.as_view()(request)
        patch.assert_not_called()
