import json

from django.test import RequestFactory

from core.test import TestCase
from demographic import factories as demographics_factories
from abstract.factories import AbstractFactory

from .. import views


class TestIndexGETAjax(TestCase):
    
    def setUp(self):
        super().setUp()
        self.abstract = AbstractFactory()
        self.factory = RequestFactory()
        
    def test_counts_gender(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        profile = self.abstract.submitter.profile
        
        demographic = demographics_factories.GenderFactory()
        profile.gender = demographic
        profile.save()
        
        response = views.index(request)
        data = json.loads(response.content)
        self.assertEqual(data['gender'][demographic.text], 1)

    def test_counts_stage(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        profile = self.abstract.submitter.profile
    
        demographic = demographics_factories.CareerStageFactory()
        profile.career_stage = demographic
        profile.save()
    
        response = views.index(request)
        data = json.loads(response.content)
        self.assertEqual(data['stage'][demographic.text], 1)

    def test_counts_state(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        profile = self.abstract.submitter.profile
    
        demographic = demographics_factories.StateFactory()
        profile.state = demographic
        profile.save()
    
        response = views.index(request)
        data = json.loads(response.content)
        self.assertEqual(data['state'][demographic.text], 1)

    def test_counts_aot(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        profile = self.abstract.submitter.profile
    
        demographic = demographics_factories.AboriginalOrTorresFactory()
        profile.aboriginal_or_torres = demographic
        profile.save()
    
        response = views.index(request)
        data = json.loads(response.content)
        self.assertEqual(data['aot'][demographic.text], 1)
