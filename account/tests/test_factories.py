from core.test import TestCase

from ..models import UserGroups
from .. import factories


class TestFactories(TestCase):
    
    def test_gets_if_exists(self):
        user_a = factories.UserFactory(username='spike')
        user_b = factories.UserFactory(username='spike')
        self.assertEqual(user_a.id, user_b.id)
        
    def test_user_factory(self):
        user = factories.UserFactory(first_name='a', last_name='b')
        self.assertEqual(user.first_name, 'a')
        self.assertEqual(user.last_name, 'b')
        self.assertFalse(user.groups.count())
    
    def test_submitter_factory_assigns_group(self):
        user = factories.SubmitterFactory()
        self.assertListEqual(
            list(user.groups.all()),
            [UserGroups.get_group(UserGroups.SUBMITTER)]
        )
        
    def test_reviewer_factory_assigns_group(self):
        user = factories.ReviewerFactory()
        self.assertListEqual(
            list(user.groups.all()),
            [UserGroups.get_group(UserGroups.REVIEWER)]
        )
        
    def test_assigner_factory_assigns_group(self):
        user = factories.AssignerFactory()
        self.assertListEqual(
            list(user.groups.all()),
            [UserGroups.get_group(UserGroups.ASSIGNER)]
        )
        
    def test_confchair_factory_assigns_group(self):
        user = factories.ConferenceChairFactory()
        self.assertListEqual(
            list(user.groups.all()),
            [UserGroups.get_group(UserGroups.CONFERENCE_CHAIR)]
        )