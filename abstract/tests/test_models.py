from core.test import TestCase

from account.factories import ReviewerFactory

from .. import models, factories


class TestAbstractModel(TestCase):
    
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()  # type: models.Abstract
        reviewers = [ReviewerFactory(), ReviewerFactory()]
        self.abstract.reviewers.add(reviewers[0])
        self.abstract.reviewers.add(reviewers[1])
    
    def test_score_content_adds_comment_scores(self):
        factories.AbstractFactory.assign_comments(self.abstract)
        self.assertEqual(
            self.abstract.score_content,
            sum([c.score_content for c in self.abstract.comments.all()])
        )

    def test_score_interest_adds_comment_scores(self):
        factories.AbstractFactory.assign_comments(self.abstract)
        self.assertEqual(
            self.abstract.score_interest,
            sum([c.score_interest for c in self.abstract.comments.all()])
        )

    def test_score_contribution_adds_comment_scores(self):
        factories.AbstractFactory.assign_comments(self.abstract)
        self.assertEqual(
            self.abstract.score_contribution,
            sum([c.score_contribution for c in self.abstract.comments.all()])
        )
        
    def test_score_averages_over_each_category(self):
        factories.AbstractFactory.assign_comments(self.abstract)
        score = (
                self.abstract.score_content +
                self.abstract.score_contribution +
                self.abstract.score_interest
        )
        score /= 3
        self.assertEqual(self.abstract.score, score)
    
    def test_has_comments(self):
        factories.AbstractFactory.assign_comments(self.abstract)
        self.assertTrue(self.abstract.has_comments)
        self.abstract.comments.all().delete()
        self.assertFalse(self.abstract.has_comments)
    
    def test_is_assigned(self):
        self.assertTrue(self.abstract.is_assigned)
        
        self.abstract.reviewers.all().delete()
        self.assertFalse(self.abstract.is_assigned)