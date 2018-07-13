import mock

from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse

import account.views.submitter
from core.test import TestCase, TestMessageMixin

from abstract import factories as abstract_factories

from .. import views, models, factories


class TestScholarshipApplicationView(TestMessageMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.SubmitterFactory()
        self.path = reverse('account:scholarship_application')
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
    def test_creates(self):
        data = {'text': 'hello', 'has_other_funding': False, 'other_funding': ''}
        request = self.create_request(method='post', path=self.path, data=data)
        request.user = self.user
        self.assertEqual(models.ScholarshipApplication.objects.count(), 0)
        response = account.views.submitter.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(models.ScholarshipApplication.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
    
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = factories.ReviewerFactory()
        with self.assertRaises(PermissionDenied):
            response = account.views.submitter.ScholarshipApplicationView.as_view()(request)
            self.assertEqual(response.status_code, 403)
    
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = account.views.submitter.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(response.status_code, 302)
    
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = account.views.submitter.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_delete_button_deletes_scholarship(self):
        request = self.create_request(
            method='get', path=self.path, data={'delete': 'True'})
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        factories.ScholarshipApplicationFactory(submitter=self.user)
        self.assertEqual(models.ScholarshipApplication.objects.count(), 1)
        
        response = account.views.submitter.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.ScholarshipApplication.objects.count(), 0)


class SubmitterView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.SubmitterFactory()
        self.user.profile.set_profile_as_complete()
        self.view = views.submitter.ProfileView.as_view()
    
    def test_works(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_permission_denied_non_submitter(self):
        request = self.factory.get('/profile/')
        with self.assertRaises(PermissionDenied):
            request.user = factories.ReviewerFactory()
            request.user.profile.set_profile_as_complete()
            self.view(request)
        with self.assertRaises(PermissionDenied):
            request.user = factories.AssignerFactory()
            self.view(request)
        with self.assertRaises(PermissionDenied):
            request.user = factories.ConferenceChairFactory()
            self.view(request)
            
    def test_requires_completed_profile(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        self.user.profile.set_profile_as_incomplete()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)