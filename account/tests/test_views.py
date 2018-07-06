from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse

from core.test import TestCase, TestMessageMixin

from account import factories as a_factories

from .. import views, models, factories


class TestScholarshipApplicationView(TestMessageMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.path = reverse('account:scholarship_application')
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
    def test_creates(self):
        data = {'text': 'hello', 'has_other_funding': False, 'other_funding': ''}
        request = self.create_request(method='post', path=self.path, data=data)
        request.user = self.user
        self.assertEqual(models.ScholarshipApplication.objects.count(), 0)
        response = views.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(models.ScholarshipApplication.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
    
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = a_factories.ReviewerFactory()
        with self.assertRaises(PermissionDenied):
            response = views.ScholarshipApplicationView.as_view()(request)
            self.assertEqual(response.status_code, 403)
    
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = views.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(response.status_code, 302)
    
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = views.ScholarshipApplicationView.as_view()(request)
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
        
        response = views.ScholarshipApplicationView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.ScholarshipApplication.objects.count(), 0)
