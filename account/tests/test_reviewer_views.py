import json
import uuid

import mock
from django.test import RequestFactory

from abstract import factories as abstract_factories
from abstract import models as abstract_models
from core.test import TestCase

from .. import factories, views


class TestProfileViewReviewerAjax(TestCase):
    def setUp(self):
        super().setUp()
        self.assignment = abstract_factories.AssignmnetFactory()
        self.reviewer = self.assignment.reviewer
        self.abstract = self.assignment.abstract
        self.factory = RequestFactory()

    def mock_reject_form_data(self):
        return {
            'id': self.assignment.id,
            'reject': True,
            'rejection_comment': "I said no."
        }

    def mock_accept_form_data(self):
        return {
            'id': self.assignment.id,
            'accept': True,
            'score_content': 5,
            'score_contribution': 6,
            'score_interest': 7,
            'text': "You're gonna carry that weight.",
        }
    
    @mock.patch('account.views.reviewer.ProfileView.post_ajax')
    def test_post_ajax_called_AJAX_post_request(self, patch):
        request = self.factory.post(
            '/profile/', data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.reviewer
        views.reviewer.ProfileView.as_view()(request)
        patch.assert_called()

    def test_error_invalid_assignment_id(self):
        request = self.factory.post(
            '/profile/', data={'id': uuid.uuid4()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn('Invalid assignment id', data['error'])

    def test_error_missing_assignment_id(self):
        request = self.factory.post(
            '/profile/', data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn('Invalid assignment id', data['error'])

    def test_error_missing_reject_or_accept(self):
        data = self.mock_reject_form_data()
        data.pop('reject')
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            "Data is missing 'reject' or 'accept' keys",
            data['error']
        )

    # Reject
    # --------------------------------------------------------------------- #
    def test_error_invalid_reject_form_no_comment(self):
        data = self.mock_reject_form_data()
        data['rejection_comment'] = ''
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            'This field is required',
            data['error']['rejection_comment'][0]['message']
        )

    def test_reject_form_valid_sets_assignment_status_and_comment(self):
        data = self.mock_reject_form_data()
        comment = data['rejection_comment']
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_PENDING)
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            'This review request has been declined.',
            data['success']
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_REJECTED)
        self.assertEqual(self.assignment.rejection_comment, comment)

    def test_reject_deletes_existing_review(self):
        data = self.mock_reject_form_data()
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        review = abstract_factories.ReviewFactory(
            reviewer=self.reviewer, abstract=self.abstract
        )
        self.assignment.review = review
        self.assignment.save()
        self.assertEqual(abstract_models.Review.objects.count(), 1)
        request.user = self.reviewer
        views.reviewer.ProfileView.as_view()(request)
        self.assertEqual(abstract_models.Review.objects.count(), 0)

    # Accept
    # --------------------------------------------------------------------- #
    def test_error_invalid_accept_missing_text_and_score(self):
        data = self.mock_accept_form_data()
        data.pop('text')
        data.pop('score_content')
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            'This field is required',
            data['error']['text'][0]['message']
        )
        self.assertIn(
            'This field is required',
            data['error']['score_content'][0]['message']
        )

    def test_error_invalid_accept_number_greater_than_max(self):
        data = self.mock_accept_form_data()
        max_ = abstract_models.Review.MAX_SCORE
        data['score_content'] = max_ + 1
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            'Ensure this value is less than or equal to {}'.format(max_),
            data['error']['score_content'][0]['message']
        )

    def test_error_invalid_accept_number_less_than_min(self):
        data = self.mock_accept_form_data()
        min_ = abstract_models.Review.MIN_SCORE
        data['score_content'] = min_ - 1
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        data = json.loads(response.content)
        self.assertIn(
            'Ensure this value is greater than or equal to {}'.format(min_),
            data['error']['score_content'][0]['message']
        )

    def test_accept_form_valid_sets_assignment_status_and_review(self):
        data = self.mock_accept_form_data()
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_PENDING)
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        r_data = json.loads(response.content)
        self.assertIn(
            'Your review has been saved.',
            r_data['success']
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_ACCEPTED)
        review = self.assignment.review
        self.assertEqual(review.text, data['text'])
        self.assertEqual(review.score_content, data['score_content'])
        self.assertEqual(review.score_contribution, data['score_contribution'])
        self.assertEqual(review.score_interest, data['score_interest'])

    def test_can_edit_existing_review(self):
        data = self.mock_accept_form_data()
        review = abstract_factories.ReviewFactory(
            abstract=self.abstract,
            reviewer=self.reviewer,
            score_content=0,
            score_contribution=0,
            score_interest=0,
        )
        self.assignment.review = review
        self.assignment.save()
        self.assertIsNotNone(self.assignment.review)
        self.assertNotEqual(review.text, data['text'])
        self.assertNotEqual(review.score_content, data['score_content'])
        self.assertNotEqual(
            review.score_contribution, data['score_contribution'])
        self.assertNotEqual(review.score_interest, data['score_interest'])

        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_PENDING)
        request.user = self.reviewer
        response = views.reviewer.ProfileView.as_view()(request)
        r_data = json.loads(response.content)
        self.assertIn(
            'Your review has been saved.',
            r_data['success']
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status,
                         abstract_models.Assignment.STATUS_ACCEPTED)
        self.assignment.refresh_from_db()
        self.assignment.review.refresh_from_db()
        self.assertEqual(
            self.assignment.review.text, data['text'])
        self.assertEqual(
            self.assignment.review.score_content, data['score_content'])
        self.assertEqual(
            self.assignment.review.score_contribution,
            data['score_contribution'])
        self.assertEqual(
            self.assignment.review.score_interest, data['score_interest'])

    def test_sets_existing_reject_comment_as_none(self):
        data = self.mock_accept_form_data()
        request = self.factory.post(
            '/profile/', data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        request.user = self.reviewer
        self.assignment.rejection_comment = "Hello"
        self.assignment.save()
        response = views.reviewer.ProfileView.as_view()(request)
        self.assignment.refresh_from_db()
        self.assertIsNone(self.assignment.rejection_comment)
