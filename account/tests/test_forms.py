from core.test import TestCase

from abstract.factories import KeywordFactory
from abstract.models import Keyword
from demographic import factories as d_factories

from .. import factories, forms


class TestScholarshipAppForm(TestCase):
    
    @staticmethod
    def mock_data():
        return {
            "text": "Hello world",
            "has_other_funding": False,
            "other_funding": "",
        }
    
    def test_error_no_funding_indicated_but_checked(self):
        user = factories.SubmitterFactory()
        
        data = self.mock_data()
        data['has_other_funding'] = True
        form = forms.ScholarshipApplicationForm(user=user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Please list your additional sources of funding.",
            str(form.errors)
        )
        
    def test_allows_blank_funding_description_if_not_checked(self):
        user = factories.SubmitterFactory()
        data = self.mock_data()
        form = forms.ScholarshipApplicationForm(user=user, data=data)
        self.assertTrue(form.is_valid())
        
    def test_sets_user_on_save(self):
        user = factories.SubmitterFactory()
        data = self.mock_data()
        form = forms.ScholarshipApplicationForm(user=user, data=data)
        self.assertTrue(form.is_valid())
        application = form.save(commit=True)
        self.assertEqual(user.scholarship_application, application)
        
    def test_error_text_more_than_250_words(self):
        user = factories.SubmitterFactory()
        data = self.mock_data()
        data['text'] = ' '.join(['a'] * 201)
        form = forms.ScholarshipApplicationForm(user=user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('limited to', str(form.errors))
        
    def test_passes_exactly_200_words(self):
        user = factories.SubmitterFactory()
        data = self.mock_data()
        data['text'] = ' '.join(['a'] * 200)
        form = forms.ScholarshipApplicationForm(user=user, data=data)
        self.assertTrue(form.is_valid())


class TestReviewerProfileForm(TestCase):
    def mock_data(self):
        return {
            'affiliation': 'New Donk City',
            'state': self.state.id,
            'career_stage': self.stage.id,
            'keywords': [self.keyword.text,],
            'email': 'person@gmail.com'
        }
    
    def setUp(self):
        super().setUp()
        self.stage = d_factories.CareerStageFactory()
        self.gender = d_factories.GenderFactory()
        self.aot = d_factories.AboriginalOrTorresFactory()
        self.state = d_factories.StateFactory()
        self.keyword = KeywordFactory()
        self.reviewer = factories.ReviewerFactory()
        
    def test_invalid_no_affiliation(self):
        data = self.mock_data()
        data.pop('affiliation')
        form = forms.ReviewerProfileForm(data=data, instance=self.reviewer)
        self.assertFalse(form.is_valid())
        
    def test_invalid_no_state(self):
        data = self.mock_data()
        data.pop('state')
        form = forms.ReviewerProfileForm(data=data, instance=self.reviewer)
        self.assertFalse(form.is_valid())
        
    def test_invalid_no_stage(self):
        data = self.mock_data()
        data.pop('career_stage')
        form = forms.ReviewerProfileForm(data=data, instance=self.reviewer)
        self.assertFalse(form.is_valid())
        
    def test_invalid_no_keywords(self):
        data = self.mock_data()
        data.pop('keywords')
        form = forms.ReviewerProfileForm(data=data, instance=self.reviewer)
        self.assertFalse(form.is_valid())
        
    def test_created_new_kws(self):
        data = self.mock_data()
        kw = data['keywords'][0]
        data['keywords'] = [kw,]
        
        self.keyword.delete()
        form = forms.ReviewerProfileForm(data=data, instance=self.reviewer)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Keyword.objects.count(), 1)
        self.assertEqual(Keyword.objects.first().text, kw)


class TestSubmitterProfileForm(TestCase):
    def mock_data(self):
        return {
            'email': 'person@gmail.com',
            'affiliation': 'New Donk City',
            'state': self.state.id,
            'gender': self.gender.id,
            'career_stage': self.stage.id,
            'aboriginal_or_torres': self.aot.id
        }
    
    def setUp(self):
        super().setUp()
        self.stage = d_factories.CareerStageFactory()
        self.gender = d_factories.GenderFactory()
        self.aot = d_factories.AboriginalOrTorresFactory()
        self.state = d_factories.StateFactory()
        self.keyword = KeywordFactory()
        self.user = factories.SubmitterFactory()
    
    def test_invalid_no_affiliation(self):
        data = self.mock_data()
        data.pop('affiliation')
        form = forms.SubmitterProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
    
    def test_invalid_no_state(self):
        data = self.mock_data()
        data.pop('state')
        form = forms.SubmitterProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
    
    def test_invalid_no_stage(self):
        data = self.mock_data()
        data.pop('career_stage')
        form = forms.SubmitterProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
    
    def test_invalid_no_gender(self):
        data = self.mock_data()
        data.pop('gender')
        form = forms.SubmitterProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        
    def test_invalid_no_aot(self):
        data = self.mock_data()
        data.pop('aboriginal_or_torres')
        form = forms.ReviewerProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())


class TestPasswordResetForm(TestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.ReviewerFactory()
        
    def test_invalid_email(self):
        form = forms.PasswordResetForm(data={'email': "email@email.com"})
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.profile)
        
    def test_valid_email(self):
        form = forms.PasswordResetForm(data={'email': self.user.profile.email})
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.profile)
        
    def test_filters_out_submitters(self):
        user = factories.SubmitterFactory()
        form = forms.PasswordResetForm(data={'email': user.profile.email})
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.profile)