from django.conf import settings

from core.test import TestCase

from account.factories import UserFactory

from demographic.factories import CareerStageFactory

from .. import factories, models, forms


class TestAbstractForm(TestCase):
    
    @staticmethod
    def mock_data():
        factories.PresentationCategoryFactory(
            text=settings.STUDENT_CATEGORY)
        category = factories.PresentationCategoryFactory(
            text='poster')
        kw = factories.KeywordFactory()
        return {
            "keywords": [kw.text,],
            "categories": [category,],
            "text": 'Hello, world!',
            "title": 'A test abstract',
            "contribution": "I don't feel so good...",
            "authors": 'Tony Stark,Spider-man',
            "author_affiliations": 'The Avengers,The Avengers',
        }
    
    def setUp(self):
        stage = CareerStageFactory()
        user = UserFactory()
        profile = user.profile
        profile.career_stage = stage
        profile.save()
        self.user = user
        
    def test_error_text_more_than_250_words(self):
        data = self.mock_data()
        data['text'] = ' '.join(['a'] * 251)
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('limited to', str(form.errors))
        
    def test_error_tittle_more_than_30_words(self):
        data = self.mock_data()
        data['title'] = ' '.join(['a'] * 31)
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('limited to', str(form.errors))
        
    def test_error_contri_more_than_100_words(self):
        data = self.mock_data()
        data['contribution'] = ' '.join(['a'] * 101)
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('limited to', str(form.errors))
        
    def test_new_save_requires_user(self):
        data = self.mock_data()
        form = forms.AbstractForm(user=self.user, data=data)
        
        self.assertTrue(form.is_valid())
        abstract = form.save()
        self.assertEqual(abstract.submitter, self.user)
        
    def test_creates_new_keywords(self):
        data = self.mock_data()
        data['keywords'] = ['bioinformatics',]
        form = forms.AbstractForm(user=self.user, data=data)
        
        self.assertTrue(form.is_valid())
        abstract = form.save()
        self.assertEqual(models.Keyword.objects.count(), 2)
        self.assertEqual(data['keywords'], [
            str(kw) for kw in abstract.keywords.all()])
        
    def test_links_existing_keywords(self):
        data = self.mock_data()
        form = forms.AbstractForm(user=self.user, data=data)
        
        self.assertTrue(form.is_valid())
        abstract = form.save()
        self.assertEqual(models.Keyword.objects.count(), 1)
        self.assertEqual(data['keywords'], [
            str(kw) for kw in abstract.keywords.all()])
        
    def test_cannot_select_student_if_not_student(self):
        stage = CareerStageFactory(text='Postdoc')
        profile = self.user.profile
        profile.career_stage = stage
        profile.save()
    
        data = self.mock_data()
        data['categories'] = [factories.PresentationCategoryFactory(
            text=settings.STUDENT_CATEGORY),]
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("must be a student", str(form.errors))
    
    def test_author_and_affiliations_not_same_legnth(self):
        data = self.mock_data()
        data['authors'] = "A,B"
        data['author_affiliations'] = "A"
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("same as the number of", str(form.errors))
        
    def test_clean_authors_and_affiliations_removes_whitespace(self):
        data = self.mock_data()
        data['authors'] = "A, B "
        data['author_affiliations'] = "A , A"
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        abstract = form.save()
        
        authors = 'A, B'
        self.assertEqual(abstract.authors, authors)
        affil = 'A, A'
        self.assertEqual(abstract.author_affiliations, affil)
        
    def test_clean_authors_and_affiliations_removes_blanks(self):
        data = self.mock_data()
        data['authors'] = "A, B,, , "
        data['author_affiliations'] = "A , A,, , "
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        abstract = form.save()
    
        authors = 'A, B'
        self.assertEqual(abstract.authors, authors)
        affil = 'A, A'
        self.assertEqual(abstract.author_affiliations, affil)