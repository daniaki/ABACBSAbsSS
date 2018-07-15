from core.test import TestCase
from demographic import factories
from abstract.factories import AbstractFactory
from abstract.models import Abstract

from .. import utilities


class TestUtilities(TestCase):

    def setUp(self):
        super().setUp()
        self.abstract = AbstractFactory()
        self.abstract_2 = AbstractFactory()

    def test_counts_gender(self):
        profile = self.abstract.submitter.profile

        demographic = factories.GenderFactory()
        profile.gender = demographic
        profile.save()

        data = utilities.compute_statistics()
        self.assertEqual(data['gender'][demographic.text], 1)

    def test_counts_stage(self):
        profile = self.abstract.submitter.profile

        demographic = factories.CareerStageFactory()
        profile.career_stage = demographic
        profile.save()

        data = utilities.compute_statistics()
        self.assertEqual(data['stage'][demographic.text], 1)

    def test_counts_state(self):
        profile = self.abstract.submitter.profile

        demographic = factories.StateFactory()
        profile.state = demographic
        profile.save()

        data = utilities.compute_statistics()
        self.assertEqual(data['state'][demographic.text], 1)

    def test_counts_aot(self):
        profile = self.abstract.submitter.profile

        demographic = factories.AboriginalOrTorresFactory()
        profile.aboriginal_or_torres = demographic
        profile.save()

        data = utilities.compute_statistics()
        self.assertEqual(data['aot'][demographic.text], 1)

    def test_stats_computed_from_passed_abstracts(self):
        demographic1 = factories.GenderFactory(text='Male')
        demographic2 = factories.GenderFactory(text='Female')

        profile = self.abstract.submitter.profile
        profile.gender = demographic1
        profile.save()

        profile = self.abstract_2.submitter.profile
        profile.gender = demographic2
        profile.save()

        data = utilities.compute_statistics()
        self.assertEqual(data['gender'][demographic1.text], 1)
        self.assertEqual(data['gender'][demographic2.text], 1)

        data = utilities.compute_statistics(
            Abstract.objects.filter(id=self.abstract.id))
        self.assertEqual(data['gender'][demographic1.text], 1)
        self.assertEqual(data['gender'][demographic2.text], 0)
