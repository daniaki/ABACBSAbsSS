from django.test import RequestFactory
from django.core.exceptions import PermissionDenied

from core.test import TestCase

from .. import factories, views


class TestProfileView(TestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.AssignerFactory()
        self.factory = RequestFactory()

    def test_does_not_require_compelete_profile(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        self.user.profile.set_profile_as_incomplete()
        response = views.assigner.ProfileView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_403_not_a_reviewer_profile(self):
        request = self.factory.get('/profile/')
        request.user = factories.SubmitterFactory()
        request.user.profile.set_profile_as_complete()
        with self.assertRaises(PermissionDenied):
            views.assigner.ProfileView.as_view()(request)
