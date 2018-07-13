from django.test import RequestFactory
from django.core.exceptions import PermissionDenied

from abstract.factories import AbstractFactory
from core.test import TestCase

from .. import factories, views


class TestProfileView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.ConferenceChairFactory()
        self.view = views.chair.ProfileView.as_view()
        self.abstract = AbstractFactory()
        self.path = '/profile/'

    def test_does_not_require_compelete_profile(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        self.user.profile.set_profile_as_incomplete()
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_403_not_a_reviewer_profile(self):
        request = self.factory.get('/profile/')
        request.user = factories.SubmitterFactory()
        request.user.profile.set_profile_as_complete()
        with self.assertRaises(PermissionDenied):
            self.view(request)

    def test_works(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_permission_denied_non_assigner(self):
        request = self.factory.get('/profile/')
        with self.assertRaises(PermissionDenied):
            request.user = factories.SubmitterFactory()
            request.user.profile.set_profile_as_complete()
            self.view(request)
        with self.assertRaises(PermissionDenied):
            request.user = factories.ReviewerFactory()
            request.user.profile.set_profile_as_complete()
            self.view(request)
        with self.assertRaises(PermissionDenied):
            request.user = factories.AssignerFactory()
            self.view(request)

    def test_demographic_buttons_visible_for_chairs(self):
        request = self.factory.get(self.path)
        request.user = self.user
        response = self.view(request)
        self.assertContains(response, 'Show demographics')

    def test_demographics_hidden_GET(self):
        request = self.factory.get(self.path)
        request.user = self.user
        response = self.view(request)
        self.assertNotContains(response, 'Career Stage')

    def test_demographics_shown_GET(self):
        request = self.factory.get(
            self.path, data={'show_demographics': 'True'})
        request.user = self.user
        response = self.view(request)
        response.render()
        self.assertContains(response, 'Career stage')

    def test_POST_approves_selected(self):
        self.fail()

    def test_POST_revokes_approved_unselected(self):
        self.fail()
        
    def test_POST_invalid_when_invalid_abstract_id_posted(self):
        self.fail()
    
    def test_GET_ajax_plot_data(self):
        self.fail()
        
    def test_GET_ajax_returns_error_invalid_abstract_id(self):
        self.fail()