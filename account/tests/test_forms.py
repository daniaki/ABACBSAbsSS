from core.test import TestCase


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
