from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from django.http import Http404

from core.test import TestCase
from abstract.factories import AbstractFactory, AssignmnetFactory

from .. import factories, views


class TestProfileView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.AssignerFactory()
        self.view = views.assigner.ProfileView.as_view()

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
        
    def test_lists_abstracts(self):
        reviewer = factories.ReviewerFactory()
        abstract = AbstractFactory()
        AssignmnetFactory(abstract=abstract, reviewer=reviewer)
        
        request = self.factory.get('/profile/')
        request.user = self.user
        response = self.view(request)
        self.assertContains(response, abstract.title)
        self.assertContains(response, reviewer.profile.full_name)

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
            request.user = factories.ConferenceChairFactory()
            self.view(request)

    
class TestAssignReviewersView(TestCase):
    
    def mock_data(self):
        return {
            'reviewers': [self.reviewer.id,]
        }
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.AssignerFactory()
        self.view = views.assigner.assign_reviewers_view
        self.reviewer = factories.ReviewerFactory()
        self.abstract = AbstractFactory()
        self.user.first_name = 'Daniel'
        self.user.last_name = 'Danielson'
        self.user.save()
        
    def test_permission_denied_non_assigner(self):
        request = self.factory.get('/profile/')
        request.user = factories.SubmitterFactory()
        with self.assertRaises(PermissionDenied):
            self.view(request, self.abstract.id)
            
    def test_404_invalid_id(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        with self.assertRaises(Http404):
            self.abstract.delete()
            self.view(request, self.abstract.id)
    
    def test_invalid_reviewer_id(self):
        data = self.mock_data()
        self.reviewer.delete()
        request = self.factory.post('/profile/', data=data)
        request.user = self.user
        response = self.view(request, self.abstract.id)
        self.assertContains(response, 'invalid')
        
    def test_adds_reviewers(self):
        data = self.mock_data()
        request = self.factory.post('/profile/', data=data)
        request.user = self.user
        response = self.view(request, self.abstract.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.reviewer, self.abstract.assigned_reviewers.all())
        
    def test_removes_reviewers(self):
        data = self.mock_data()
        data['reviewers'] = []
        request = self.factory.post('/profile/', data=data)
        request.user = self.user
        AssignmnetFactory(abstract=self.abstract, reviewer=self.reviewer)

        self.assertIn(self.reviewer, self.abstract.assigned_reviewers.all())
        response = self.view(request, self.abstract.id)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.reviewer, self.abstract.assigned_reviewers.all())
    
    def test_shows_all_reviewers(self):
        request = self.factory.get('/profile/')
        request.user = self.user
        response = self.view(request, self.abstract.id)
        self.assertContains(response, self.reviewer.profile.full_name)
        self.assertNotContains(response, self.user.profile.full_name)
