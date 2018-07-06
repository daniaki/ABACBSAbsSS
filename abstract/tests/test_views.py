from django.conf import settings
from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse
from django.http import Http404

from core.test import TestCase, TestMessageMixin

from account import factories as a_factories

from .. import views, factories, models


def mock_data():
    factories.PresentationCategoryFactory(
        text=settings.STUDENT_CATEGORY)
    category = factories.PresentationCategoryFactory(
        text='poster')
    kw = factories.KeywordFactory()
    return {
        "keywords": [kw.text, ],
        "categories": [category.id, ],
        "text": 'Hello, world!',
        "title": 'A test abstract',
        "contribution": "I don't feel so good...",
        "authors": 'Tony Stark,Spider-man',
        "author_affiliations": 'The Avengers,The Avengers',
    }


class TestSubmissionView(TestMessageMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.path = reverse('abstract:submit_abstract')
        
    def test_creates(self):
        data = mock_data()
        request = self.create_request(method='post', path=self.path, data=data)
        request.user = self.user

        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()

        self.assertEqual(models.Abstract.objects.count(), 0)
        response = views.SubmissionView.as_view()(request)
        self.assertEqual(models.Abstract.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        
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


class TestEditSubmissionView(TestMessageMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.abstract = factories.AbstractFactory(submitter=self.user)
        self.path = reverse('abstract:edit_abstract',
                            kwargs={'id': self.abstract.id})
        
    def test_edits(self):
        data = mock_data()
        request = self.create_request(method='post', path=self.path, data=data)
        request.user = self.user

        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()

        self.assertNotEqual(data['text'], self.abstract.text)
        response = views.EditSubmissionView.as_view()(request, id=self.abstract.id)
        self.assertEqual(response.status_code, 302)
        self.abstract.refresh_from_db()
        self.assertEqual(data['text'], self.abstract.text)
        
    def test_404_editing_abstract_that_does_not_belong_to_user(self):
        request = self.factory.get(self.path)
        request.user = self.user
        self.abstract.submitter = None
        self.abstract.save()
        with self.assertRaises(Http404):
            views.EditSubmissionView.as_view()(request, id=self.abstract.id)
    
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = a_factories.ReviewerFactory()
        self.abstract.submitter = request.user
        self.abstract.save()
        with self.assertRaises(PermissionDenied):
            response = views.EditSubmissionView.as_view()(
                request, id=self.abstract.id)
            self.assertEqual(response.status_code, 403)
    
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = views.EditSubmissionView.as_view()(
            request, id=self.abstract.id)
        self.assertEqual(response.status_code, 302)
    
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = views.EditSubmissionView.as_view()(
            request, id=self.abstract.id)
        self.assertEqual(response.status_code, 200)


class TestDeleteSubmissionView(TestMessageMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = a_factories.SubmitterFactory()
        self.abstract = factories.AbstractFactory(submitter=self.user)
        self.path = reverse('abstract:delete_abstract',
                            kwargs={'id': self.abstract.id})
    
    def test_404_deleting_abstract_that_does_not_belong_to_user(self):
        request = self.factory.get(self.path)
        request.user = self.user
        self.abstract.submitter = None
        self.abstract.save()
        with self.assertRaises(Http404):
            views.DeleteSubmissionView.as_view()(request, id=self.abstract.id)
    
    def test_restricted_to_submitter(self):
        request = self.factory.get(self.path)
        request.user = a_factories.ReviewerFactory()
        self.abstract.submitter = request.user
        self.abstract.save()
        with self.assertRaises(PermissionDenied):
            response = views.DeleteSubmissionView.as_view()(
                request, id=self.abstract.id)
            self.assertEqual(response.status_code, 403)
    
    def test_incomplete_profile_redirects(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = False
        profile.save()
        
        response = views.DeleteSubmissionView.as_view()(
            request, id=self.abstract.id)
        self.assertEqual(response.status_code, 302)
    
    def test_compelete_profile_not_redirected(self):
        request = self.factory.get(self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        response = views.DeleteSubmissionView.as_view()(
            request, id=self.abstract.id)
        self.assertEqual(response.status_code, 200)
        
    def test_deletes(self):
        request = self.create_request('post', path=self.path)
        request.user = self.user
        
        profile = self.user.profile
        profile.completed_intial_login = True
        profile.save()
        
        self.assertEqual(models.Abstract.objects.count(), 1)
        views.DeleteSubmissionView.as_view()(request, id=self.abstract.id)
        self.assertEqual(models.Abstract.objects.count(), 0)
