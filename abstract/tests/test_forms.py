from django.core import mail
from django.utils import timezone
from django.utils.datetime_safe import datetime

from core.test import TestCase

from account.factories import UserFactory, ReviewerFactory, AssignerFactory

from demographic.factories import CareerStageFactory

from .. import factories, models, forms

server_tz = timezone.get_current_timezone()


class TestAbstractForm(TestCase):
    @staticmethod
    def mock_data():
        factories.PresentationCategoryFactory()
        category = factories.PresentationCategoryFactory()
        kw = factories.KeywordFactory()
        return {
            "keywords": [kw.text, ],
            "categories": [category, ],
            "text": 'Hello, world!',
            "title": 'A test abstract',
            "contribution": "I don't feel so good...",
            "authors": 'Tony Stark\nSpider-man',
            "author_affiliations": 'The Avengers\nThe, Avengers',
        }
    
    def setUp(self):
        stage = CareerStageFactory()
        user = UserFactory()
        profile = user.profile
        profile.career_stage = stage
        profile.save()
        self.user = user

    def test_disabled_categories_set(self):
        c1 = factories.PresentationCategoryFactory(text='1')
        c2 = factories.PresentationCategoryFactory(text='2')
        c1.closing_date = datetime(2012, 1, 1, 1, tzinfo=server_tz)
        c1.save()
        c2.closing_date = datetime(3000, 1, 1, 1, tzinfo=server_tz)
        c2.save()
        form = forms.AbstractForm(user=self.user, data={})
        self.assertNotIn(
            c2.pk, form.fields['categories'].widget.disabled_choices)
        self.assertIn(
            c1.pk, form.fields['categories'].widget.disabled_choices)

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

    def test_author_and_affiliations_not_same_legnth(self):
        data = self.mock_data()
        data['authors'] = "A\nB"
        data['author_affiliations'] = "A"
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("same as the number of", str(form.errors))
        
    def test_clean_authors_and_affiliations_removes_whitespace(self):
        data = self.mock_data()
        data['authors'] = "A\n B "
        data['author_affiliations'] = "A \n A;C"
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        abstract = form.save()
        
        authors = 'A\nB'
        self.assertEqual(abstract.authors, authors)
        affil = 'A\nA;C'
        self.assertEqual(abstract.author_affiliations, affil)
        
    def test_clean_authors_and_affiliations_removes_blanks(self):
        data = self.mock_data()
        data['authors'] = "A\n B\n\n \n "
        data['author_affiliations'] = "A \n A\n\n \n "
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        abstract = form.save()
    
        authors = 'A\nB'
        self.assertEqual(abstract.authors, authors)
        affil = 'A\nA'
        self.assertEqual(abstract.author_affiliations, affil)
        
    def test_sets_user(self):
        data = self.mock_data()
        form = forms.AbstractForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        abstract = form.save(commit=True)
        self.assertIn(abstract, self.user.abstracts.all())


class TestAssignmentForm(TestCase):
    
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()
        self.assigner = AssignerFactory()
        
    def test_creates_assignments_and_mails_user(self):
        reviewer = ReviewerFactory()
        data = {'reviewers': [reviewer.id]}
        form = forms.AssingmentForm(
            data=data, assigner=self.assigner, abstract=self.abstract)
        self.assertTrue(form.is_valid())
        self.assertEqual(models.Assignment.objects.count(), 0)
        form.save()
        self.assertEqual(models.Assignment.objects.count(), 1)
        self.assertEqual(self.abstract.assigned_reviewers.count(), 1)
        self.assertEqual(self.abstract.reviewers.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("You have been assigned", mail.outbox[0].body)
        
    def test_deletes_assignments_and_mails_user(self):
        reviewer = ReviewerFactory()
        data = {'reviewers': []}
        factories.AssignmnetFactory(
            reviewer=reviewer, created_by=self.assigner, abstract=self.abstract)
        form = forms.AssingmentForm(
            data=data, assigner=self.assigner, abstract=self.abstract)
        self.assertTrue(form.is_valid())
        self.assertEqual(models.Assignment.objects.count(), 1)
        form.save()
        self.assertEqual(models.Assignment.objects.count(), 0)
        self.assertEqual(self.abstract.assigned_reviewers.count(), 0)
        self.assertEqual(self.abstract.reviewers.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("has been rescinded.", mail.outbox[0].body)
    
    def test_invalid_choice_non_reviewer(self):
        data = {'reviewers': [AssignerFactory().id]}
        form = forms.AssingmentForm(
            data=data, assigner=self.assigner, abstract=self.abstract)
        self.assertFalse(form.is_valid())
        
    def test_deletes_review_when_deleting_assignment(self):
        reviewer = ReviewerFactory()
        data = {'reviewers': []}
        
        assignment = factories.AssignmnetFactory(
            reviewer=reviewer, created_by=self.assigner, abstract=self.abstract)
        review = factories.ReviewFactory(reviewer=reviewer, abstract=self.abstract)
        assignment.review = review
        assignment.save()
        
        form = forms.AssingmentForm(
            data=data, assigner=self.assigner, abstract=self.abstract)
        self.assertTrue(form.is_valid())
        self.assertEqual(models.Review.objects.count(), 1)
        form.save()
        self.assertEqual(models.Review.objects.count(), 0)
        
    def test_does_not_add_remove_existing(self):
        reviewer = ReviewerFactory()
        data = {'reviewers': [reviewer.id]}
    
        assignment = factories.AssignmnetFactory(
            reviewer=reviewer, created_by=self.assigner, abstract=self.abstract)
        review = factories.ReviewFactory(
            reviewer=reviewer, abstract=self.abstract)
        assignment.review = review
        assignment.save()
    
        form = forms.AssingmentForm(
            data=data, assigner=self.assigner, abstract=self.abstract)
        self.assertTrue(form.is_valid())
        self.assertEqual(models.Review.objects.count(), 1)
        self.assertEqual(models.Assignment.objects.count(), 1)
        form.save()
        self.assertEqual(models.Review.objects.count(), 1)
        self.assertEqual(models.Assignment.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)


class TestRejectAssignmentForm(TestCase):
    def test_invalid_no_comment(self):
        form = forms.RejectAssignmentForm(data={})
        self.assertFalse(form.is_valid())
        
        form = forms.RejectAssignmentForm(data={'rejection_comment': " "})
        self.assertFalse(form.is_valid())
    
    
class TestReviewForm(TestCase):
    @staticmethod
    def mock_data():
        return {
            'text': "Hello",
            'score_content': 1,
            'score_contribution': 1,
            'score_interest': 1,
        }
    
    def test_valid_no_text(self):
        data = self.mock_data()
        data.pop('text')
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())
        
        data['text'] = " "
        form = forms.ReviewForm(data=data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_score_content_less_than_min(self):
        data = self.mock_data()
        data['score_content'] = models.Review.MIN_SCORE - 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())
        
    def test_invalid_score_contribution_less_than_min(self):
        data = self.mock_data()
        data['score_contribution'] = models.Review.MIN_SCORE - 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())
        
    def test_invalid_score_interest_less_than_min(self):
        data = self.mock_data()
        data['score_interest'] = models.Review.MIN_SCORE - 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_score_content_greater_than_max(self):
        data = self.mock_data()
        data['score_content'] = models.Review.MAX_SCORE + 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_score_contribution_greater_than_max(self):
        data = self.mock_data()
        data['score_contribution'] = models.Review.MAX_SCORE + 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_score_interest_greater_than_max(self):
        data = self.mock_data()
        data['score_interest'] = models.Review.MAX_SCORE + 1
        form = forms.ReviewForm(data=data)
        self.assertFalse(form.is_valid())