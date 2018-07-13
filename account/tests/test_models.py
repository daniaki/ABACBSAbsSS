from django.core import mail
from django.contrib.auth.models import Group

from core.test import TestCase

from abstract.factories import AbstractFactory

from .. import factories, models


class TestProfileModel(TestCase):
    def setUp(self):
        super().setUp()
        self.submitter = factories.SubmitterFactory()
        self.reviewer = factories.ReviewerFactory()
        self.abstract = AbstractFactory(submitter=self.submitter)

    def test_send_email_uses_profile_by_email_by_default(self):
        profile = self.submitter.profile
        profile.email = "email@email.com"
        profile.save()
        profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [profile.email])

    def test_send_email_uses_user_email_as_backup(self):
        profile = self.submitter.profile
        profile.email = None
        profile.save()
        profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [profile.user.email])

    def test_email_user_sends_no_email_if_no_email_present(self):
        self.submitter.email = ""
        self.submitter.save()
        profile = self.submitter.profile
        profile.email = None
        profile.save()
        profile.email_user(message="hello", subject="None")
        self.assertEqual(len(mail.outbox), 0)
        
    def test_sets_profile_as_complete(self):
        self.assertFalse(self.submitter.profile.completed_intial_login)
        self.submitter.profile.set_profile_as_complete()
        self.assertTrue(self.submitter.profile.completed_intial_login)
    
    def test_sets_profile_as_inclomplete(self):
        self.submitter.profile.set_profile_as_complete()
        self.assertTrue(self.submitter.profile.completed_intial_login)
        self.submitter.profile.set_profile_as_incomplete()
        self.assertFalse(self.submitter.profile.completed_intial_login)
        
    def test_groups_names_returns_text_names_of_all_groups(self):
        self.assertListEqual(
            list(self.submitter.profile.group_names),
            [models.UserGroups.SUBMITTER.value]
        )
    
    def test_is_complete_returns_true_complete_profile(self):
        self.submitter.profile.set_profile_as_complete()
        self.assertTrue(self.submitter.profile.is_complete)

    def test_is_complete_returns_false_incomplete_profile(self):
        self.submitter.profile.set_profile_as_incomplete()
        self.assertFalse(self.submitter.profile.is_complete)

    
class TestUserGroupsEnum(TestCase):
    def test_get_submitter_group(self):
        g = Group.objects.get(name=models.UserGroups.SUBMITTER.value)
        self.assertEqual(
            g, models.UserGroups.get_group(models.UserGroups.SUBMITTER))
    
    def test_get_reviewer_group(self):
        g = Group.objects.get(name=models.UserGroups.REVIEWER.value)
        self.assertEqual(
            g, models.UserGroups.get_group(models.UserGroups.REVIEWER))
    
    def test_get_assinger_group(self):
        g = Group.objects.get(name=models.UserGroups.ASSIGNER.value)
        self.assertEqual(
            g, models.UserGroups.get_group(models.UserGroups.ASSIGNER))
    
    def test_get_conf_chair_group(self):
        g = Group.objects.get(name=models.UserGroups.CONFERENCE_CHAIR.value)
        self.assertEqual(
            g, models.UserGroups.get_group(models.UserGroups.CONFERENCE_CHAIR))