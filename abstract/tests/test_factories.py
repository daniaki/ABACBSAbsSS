from django.contrib.auth import get_user_model

from core.test import TestCase

from account.models import UserGroups

from .. import factories

User = get_user_model()


class TestAbstractFactory(TestCase):
    def test_assigns_keyword(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(abstract.keywords.count(), 1)
    
    def test_assigns_submitter(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertListEqual(list(abstract.submitter.groups.all()),
                             [UserGroups.get_group(UserGroups.SUBMITTER)])
    
    def test_assigns_reviewer(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(abstract.reviewers.count(), 1)
        self.assertListEqual(list(abstract.reviewers.first().groups.all()),
                             [UserGroups.get_group(UserGroups.REVIEWER)])
        
    def test_assigns_comment_for_each_reviewer(self):
        abstract = factories.AbstractFactory()
        comments = factories.AbstractFactory.assign_reviews(abstract)
        self.assertEqual(User.objects.count(), 2)  # No extra users created
        self.assertEqual(len(comments), 1)
        
    def test_assigns_category(self):
        abstract = factories.AbstractFactory()
        self.assertEqual(abstract.categories.count(), 1)


class TestCommentFactory(TestCase):
    def test_assigns_first_reviewer(self):
        comment = factories.ReviewFactory()
        self.assertEqual(User.objects.count(), 2)  # one submitter, one reviewer
        self.assertEqual(comment.reviewer, comment.abstract.reviewers.first())
        
    def test_assigns_scores(self):
        comment = factories.ReviewFactory()
        self.assertGreaterEqual(comment.score_content, factories.MIN_SCORE)
        self.assertGreaterEqual(comment.score_interest, factories.MIN_SCORE)
        self.assertGreaterEqual(comment.score_contribution, factories.MIN_SCORE)
        
        self.assertLessEqual(comment.score_content, factories.MAX_SCORE)
        self.assertLessEqual(comment.score_interest, factories.MAX_SCORE)
        self.assertLessEqual(comment.score_contribution, factories.MAX_SCORE)
    
    def test_gets_on_reviewer_and_abstract(self):
        comment_a = factories.ReviewFactory()
        comment_b = factories.ReviewFactory(abstract=comment_a.abstract,
                                            reviewer=comment_a.reviewer)
        self.assertEqual(comment_a.id, comment_b.id)
        