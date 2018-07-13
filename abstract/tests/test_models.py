from core.test import TestCase

from account.factories import ReviewerFactory

from .. import models, factories


class TestAbstractModel(TestCase):
    
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()  # type: models.Abstract
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
        
    def test_pending_assignments_reviewers_returns_pending_only(self):
        assignment1 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment2 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment3 = factories.AssignmnetFactory(abstract=self.abstract)
        
        assignment1.status = models.Assignment.STATUS_PENDING
        assignment2.status = models.Assignment.STATUS_ACCEPTED
        assignment3.status = models.Assignment.STATUS_REJECTED
        
        assignment1.save()
        assignment2.save()
        assignment3.save()
        
        self.assertIn(assignment1, self.abstract.pending_assignments)
        self.assertNotIn(assignment2, self.abstract.pending_assignments)
        self.assertNotIn(assignment3, self.abstract.pending_assignments)
        
        self.assertIn(assignment1.reviewer, self.abstract.pending_reviewers)
        self.assertNotIn(assignment2.reviewer, self.abstract.pending_reviewers)
        self.assertNotIn(assignment3.reviewer, self.abstract.pending_reviewers)

    def test_declined_assignments_reviewers_returns_declined_only(self):
        assignment1 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment2 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment3 = factories.AssignmnetFactory(abstract=self.abstract)
    
        assignment1.status = models.Assignment.STATUS_PENDING
        assignment2.status = models.Assignment.STATUS_ACCEPTED
        assignment3.status = models.Assignment.STATUS_REJECTED
    
        assignment1.save()
        assignment2.save()
        assignment3.save()
    
        self.assertNotIn(assignment1, self.abstract.declined_assignments)
        self.assertNotIn(assignment2, self.abstract.declined_assignments)
        self.assertIn(assignment3, self.abstract.declined_assignments)
        
        self.assertNotIn(assignment1.reviewer, self.abstract.declined_reviewers)
        self.assertNotIn(assignment2.reviewer, self.abstract.declined_reviewers)
        self.assertIn(assignment3.reviewer, self.abstract.declined_reviewers)

    def test_accepted_assignments_reviewers_returns_accepted_only(self):
        assignment1 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment2 = factories.AssignmnetFactory(abstract=self.abstract)
        assignment3 = factories.AssignmnetFactory(abstract=self.abstract)
    
        assignment1.status = models.Assignment.STATUS_PENDING
        assignment2.status = models.Assignment.STATUS_ACCEPTED
        assignment3.status = models.Assignment.STATUS_REJECTED
    
        assignment1.save()
        assignment2.save()
        assignment3.save()
    
        self.assertNotIn(assignment1, self.abstract.accepted_assignments)
        self.assertIn(assignment2, self.abstract.accepted_assignments)
        self.assertNotIn(assignment3, self.abstract.accepted_assignments)
        
        self.assertNotIn(assignment1.reviewer, self.abstract.accepted_reviewers)
        self.assertIn(assignment2.reviewer, self.abstract.accepted_reviewers)
        self.assertNotIn(assignment3.reviewer, self.abstract.accepted_reviewers)
        
    def test_deleted_if_submitter_is_deleted(self):
        self.abstract.submitter.delete()
        self.assertEqual(models.Abstract.objects.count(), 0)


class TestAssignment(TestCase):
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()  # type: models.Abstract
        self.assignment = factories.AssignmnetFactory(
            abstract=self.abstract) # type: models.Assignment
        self.review = factories.ReviewFactory(
            abstract=self.abstract,
            reviewer=self.assignment.reviewer
        )
        self.assignment.review = self.review
        self.assignment.save()
        
    def test_deleted_if_reviewer_deleted(self):
        self.assignment.reviewer.delete()
        self.assertEqual(models.Assignment.objects.count(), 0)
        
    def test_deleted_if_abstract_deleted(self):
        self.assignment.abstract.delete()
        self.assertEqual(models.Assignment.objects.count(), 0)
        
    def test_review_set_null_if_review_deleted(self):
        self.assertIsNotNone(self.assignment.review)
        self.assignment.review.delete()
        self.assignment.refresh_from_db()
        self.assertIsNone(self.assignment.review)


class TestReview(TestCase):
    def setUp(self):
        super().setUp()
        self.abstract = factories.AbstractFactory()  # type: models.Abstract
        self.assignment = factories.AssignmnetFactory(
            abstract=self.abstract)  # type: models.Assignment
        self.review = factories.ReviewFactory(
            abstract=self.abstract,
            reviewer=self.assignment.reviewer
        )
        self.assignment.review = self.review
        self.assignment.save()
    
    def test_deleted_if_reviewer_deleted(self):
        self.review.reviewer.delete()
        self.assertEqual(models.Review.objects.count(), 0)
    
    def test_deleted_if_abstract_deleted(self):
        self.assignment.abstract.delete()
        self.assertEqual(models.Review.objects.count(), 0)
