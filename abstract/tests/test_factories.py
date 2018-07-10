from django.contrib.auth import get_user_model

from core.test import TestCase

from account.models import UserGroups

from .. import factories

User = get_user_model()


class TestAbstractFactory(TestCase):
    def test_assigns_keyword(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(abstract.keywords.count(), 1)
    
    def test_assigns_submitter(self):
        abstract = factories.AbstractFactory()
        self.assertListEqual(list(abstract.submitter.groups.all()),
                             [UserGroups.get_group(UserGroups.SUBMITTER)])
           
    def test_assigns_comment_for_each_reviewer(self):
        abstract = factories.AbstractFactory()
        comments = factories.AbstractFactory.assign_reviews(abstract)
        # One assigner, one submitter, 3 reviewers
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(len(comments), 3)
        
    def test_assigns_category(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(abstract.categories.count(), 1)


class TestReviewFactory(TestCase):
    def test_assigns_scores(self):
        review = factories.ReviewFactory()
        self.assertGreaterEqual(review.score_content, factories.MIN_SCORE)
        self.assertGreaterEqual(review.score_interest, factories.MIN_SCORE)
        self.assertGreaterEqual(review.score_contribution, factories.MIN_SCORE)
        
        self.assertLessEqual(review.score_content, factories.MAX_SCORE)
        self.assertLessEqual(review.score_interest, factories.MAX_SCORE)
        self.assertLessEqual(review.score_contribution, factories.MAX_SCORE)
    
    def test_gets_on_reviewer_and_abstract(self):
        review_a = factories.ReviewFactory()
        review_b = factories.ReviewFactory(abstract=review_a.abstract,
                                            reviewer=review_a.reviewer)
        self.assertEqual(review_a.id, review_b.id)
        