import io
import csv
import json

from django.test import RequestFactory
from django.core.exceptions import PermissionDenied

from demographic.factories import (
    GenderFactory, CareerStageFactory,
    StateFactory, AboriginalOrTorresFactory
)
from abstract.factories import AbstractFactory
from core.test import TestCase, TestMessageMixin

from .. import factories, views


class TestProfileView(TestCase, TestMessageMixin):
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
        data = {'abstracts[]': [self.abstract.id]}
        abstract = AbstractFactory()
        request = self.create_request('post',
            path=self.path, data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.user
        self.assertFalse(self.abstract.accepted)
        response = json.loads(self.view(request).content.decode('utf-8'))

        self.assertIn('success', response)
        self.abstract.refresh_from_db()
        abstract.refresh_from_db()
        self.assertTrue(self.abstract.accepted)
        self.assertFalse(abstract.accepted)

    def test_POST_revokes_approved_unselected(self):
        data = {'abstracts[]': [self.abstract.id]}

        abstract = AbstractFactory()
        abstract.accepted = True
        abstract.save()

        request = self.create_request('post',
            path=self.path, data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.user
        self.assertFalse(self.abstract.accepted)
        self.assertTrue(abstract.accepted)
        response = json.loads(self.view(request).content.decode('utf-8'))

        self.assertIn('success', response)
        self.abstract.refresh_from_db()
        abstract.refresh_from_db()
        self.assertTrue(self.abstract.accepted)
        self.assertFalse(abstract.accepted)
        
    def test_POST_invalid_when_invalid_abstract_id_posted(self):
        data = {'abstracts[]': [self.abstract.id]}
        self.abstract.delete()
        request = self.create_request('post',
            path=self.path, data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.user
        response = json.loads(self.view(request).content.decode('utf-8'))
        self.assertIn('error', response)

    def test_GET_ajax_plot_data(self):
        data = {'abstracts[]': [self.abstract.id]}
        
        profile = self.abstract.submitter.profile
        demographic = GenderFactory()
        profile.gender = demographic
        profile.save()
        
        request = self.create_request('get',
            path=self.path, data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.user
        response = json.loads(self.view(request).content.decode('utf-8'))
        self.assertEqual(response['gender'][demographic.text], 1)
               
    def test_GET_ajax_returns_error_invalid_abstract_id(self):
        data = {'abstracts[]': [self.abstract.id]}
        self.abstract.delete()
        request = self.create_request('get',
            path=self.path, data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.user
        response = json.loads(self.view(request).content.decode('utf-8'))
        self.assertIn('error', response)


class TestDownloadViews(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.ConferenceChairFactory()
        self.abstract = AbstractFactory()
        self.submitter = self.abstract.submitter
        self.profile = self.submitter.profile

        self.profile.gender = GenderFactory()
        self.profile.career_stage = CareerStageFactory()
        self.profile.state = StateFactory()
        self.profile.aboriginal_or_torres = AboriginalOrTorresFactory()
        self.profile.affiliation = 'django'
        self.profile.save()

        self.scholarship = factories.ScholarshipApplicationFactory(
            submitter=self.submitter
        )

        self.path = '/profile/'

    def test_403_not_a_reviewer_profile(self):
        request = self.factory.get('/profile/download/abstracts')
        request.user = factories.SubmitterFactory()
        request.user.profile.set_profile_as_complete()
        with self.assertRaises(PermissionDenied):
            views.chair.DownloadAbstracts.as_view()(request)
        with self.assertRaises(PermissionDenied):
            views.chair.DownloadScholarshipApplications.as_view()(request)

    def test_download_abstract_tsv(self):
        request = self.factory.get('/profile/download/abstracts')
        request.user = self.user
        response = views.chair.DownloadAbstracts.as_view()(request)

        string = response.content.decode('utf-8').decode('utf-8')
        handle = io.StringIO(string)
        reader = csv.DictReader(
            handle, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        dict_ = list(reader)[0]
        self.assertEqual(dict_['title'], self.abstract.title.replace('\n', ' '))
        self.assertEqual(dict_['content'], self.abstract.text.replace('\n', ' '))
        self.assertEqual(dict_['contribution'], self.abstract.contribution.replace('\n', ' '))
        self.assertEqual(dict_['authors'], self.abstract.authors)
        self.assertEqual(dict_['affiliations'], self.abstract.author_affiliations)
        self.assertEqual(dict_['keywords'], ','.join([x.text for x in self.abstract.keywords.all()]))
        self.assertEqual(dict_['categories'], ','.join([x.text for x in self.abstract.categories.all()]))
        self.assertEqual(dict_['submitter'], self.profile.display_name)
        self.assertEqual(dict_['affiliation'], self.profile.affiliation)
        self.assertEqual(dict_['career_stage'], self.profile.career_stage.text)
        self.assertEqual(dict_['gender'], self.profile.gender.text)
        self.assertEqual(dict_['state'], self.profile.state.text)
        self.assertEqual(dict_['aboriginal/torres'], self.profile.aboriginal_or_torres.text)
        self.assertEqual(dict_['accepted'], str(self.abstract.accepted))
        self.assertEqual(dict_['score'], '')

    def test_download_scholarship_tsv(self):
        request = self.factory.get('/profile/download/scholarships')
        request.user = self.user
        response = views.chair.DownloadScholarshipApplications.as_view()(request)

        string = response.content.decode('utf-8').decode('utf-8')
        handle = io.StringIO(string)
        reader = csv.DictReader(
            handle, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        dict_ = list(reader)[0]

        self.assertEqual(dict_['applicant'], self.profile.display_name)
        self.assertEqual(dict_['reason'], self.scholarship.text)
        self.assertEqual(dict_['other_funding'], self.scholarship.other_funding)
        self.assertEqual(dict_['email'], self.profile.email)
        self.assertEqual(dict_['career_stage'], self.profile.career_stage.text)


class TestScholarshipListView(TestCase, TestMessageMixin):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = factories.ConferenceChairFactory()
        self.view = views.chair.ScholarshipListView.as_view()
        self.app = factories.ScholarshipApplicationFactory()
        self.path = '/profile/scholarships'

    def test_does_not_require_compelete_profile(self):
        request = self.factory.get(self.path)
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
        request = self.factory.get(self.path)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.app.text[0:10])