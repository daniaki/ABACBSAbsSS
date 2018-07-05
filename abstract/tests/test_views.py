from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse
from django.http import Http404

from core.test import TestCase

from account import factories as a_factories

from .. import views, factories


class TestSubmissionView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.path = reverse('abstract:submit_abstract')
        
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = a_factories.ReviewerFactory()
        with self.assertRaises(PermissionDenied):
            response = views.SubmissionView.as_view()(request)
            self.assertEqual(response.status_code, 403)
        
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = views.SubmissionView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = views.SubmissionView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class TestEditSubmissionView(TestCase):
    @staticmethod
    def mock_data():
        category = factories.PresentationCategoryFactory(
            text='poster')
        kw = factories.KeywordFactory()
        return {
            "keywords": [kw.text, ],
            "categories": [category, ],
            "text": 'Hello, world!',
            "title": 'A test abstract',
            "contribution": "I don't feel so good...",
            "authors": 'Tony Stark,Spider-man',
            "author_affiliations": 'The Avengers,The Avengers',
        }
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.absract = factories.AbstractFactory(submitter=self.user)
        self.path = reverse('abstract:edit_abstract',
                            kwargs={'id': self.absract.id})
        
    def test_404_editing_abstract_that_does_not_belong_to_user(self):
        request = self.factory.get(self.path)
        request.user = self.user
        self.absract.submitter = None
        self.absract.save()
        with self.assertRaises(Http404):
            views.EditSubmissionView.as_view()(request, id=self.absract.id)
    
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = a_factories.ReviewerFactory()
        self.absract.submitter = request.user
        self.absract.save()
        with self.assertRaises(PermissionDenied):
            response = views.EditSubmissionView.as_view()(
                request, id=self.absract.id)
            self.assertEqual(response.status_code, 403)
    
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = views.EditSubmissionView.as_view()(
            request, id=self.absract.id)
        self.assertEqual(response.status_code, 302)
    
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = views.EditSubmissionView.as_view()(
            request, id=self.absract.id)
        self.assertEqual(response.status_code, 200)