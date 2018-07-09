import mock

from django.test import RequestFactory
from django.http import Http404

from core.test import TestCase

from .. import views, factories


class TestProfileView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    @mock.patch('account.views.submitter.ProfileView.dispatch')
    def test_dispatches_to_submitter_view(self, patch):
        request = self.factory.get('/profile/')
        request.user = factories.SubmitterFactory()
        views.ProfileView.as_view()(request)
        patch.assert_called()

    @mock.patch('account.views.reviewer.ProfileView.dispatch')
    def test_dispatches_to_reviewer_view(self, patch):
        request = self.factory.get('/profile/')
        request.user = factories.ReviewerFactory()
        views.ProfileView.as_view()(request)
        patch.assert_called()

    @mock.patch('account.views.assigner.ProfileView.dispatch')
    def test_dispatches_to_assigner_view(self, patch):
        request = self.factory.get('/profile/')
        request.user = factories.AssignerFactory()
        views.ProfileView.as_view()(request)
        patch.assert_called()

    @mock.patch('account.views.chair.ProfileView.dispatch')
    def test_dispatches_to_chair_view(self, patch):
        request = self.factory.get('/profile/')
        request.user = factories.ConferenceChairFactory()
        views.ProfileView.as_view()(request)
        patch.assert_called()

    def test_404_invalid_group(self):
        request = self.factory.get('/profile/')
        request.user = factories.UserFactory()
        with self.assertRaises(Http404):
            views.ProfileView.as_view()(request)
