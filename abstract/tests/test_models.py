from core.test import TestCase

from account.factories import ReviewerFactory

from .. import models, factories


class TestAbstractModel(TestCase):
    
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()  # type: models.Abstract
        reviewers = [ReviewerFactory(), ReviewerFactory()]
        factories.AbstractFactory.assign_reviews(self.abstract, n=3)
    
    def test_score_content_adds_review_scores(self):
        self.assertEqual(
            self.abstract.score_content,
            sum([c.score_content for c in self.abstract.reviews.all()])
        )

    def test_score_interest_adds_review_scores(self):
        self.assertEqual(
            self.abstract.score_interest,
            sum([c.score_interest for c in self.abstract.reviews.all()])
        )

    def test_score_contribution_adds_review_scores(self):
        self.assertEqual(
            self.abstract.score_contribution,
            sum([c.score_contribution for c in self.abstract.reviews.all()])
        )
        
    def test_score_averages_over_each_category(self):
        score = (
                self.abstract.score_content +
                self.abstract.score_contribution +
                self.abstract.score_interest
        )
        score /= 3
        self.assertEqual(self.abstract.score, score)
    
    def test_has_reviews(self):
        self.assertTrue(self.abstract.has_reviews)
        self.abstract.reviews.all().delete()
        self.assertFalse(self.abstract.has_reviews)
    
    def test_is_assigned(self):
        self.assertTrue(self.abstract.is_assigned)
        self.abstract.reviewers.all().delete()
        self.assertFalse(self.abstract.is_assigned)
    
    def test_assigned_reviewers_returns_all_reviewers(self):
        self.assertEqual(self.abstract.reviewers.count(), 3)
        self.abstract.reviews.first().delete()
        self.assertEqual(self.abstract.reviewers.count(), 2)
    
    def test_reviewers_returns_only_those_who_have_left_a_review(self):
        self.assertEqual(self.abstract.assigned_reviewers.count(), 3)
        self.abstract.reviews.first().delete()
        self.assertEqual(self.abstract.assigned_reviewers.count(), 3)
        