import factory.fuzzy
from factory.django import DjangoModelFactory

from . import models


class GenderFactory(DjangoModelFactory):
    class Meta:
        model = models.Gender
        django_get_or_create = ('text',)
    
    text = factory.fuzzy.FuzzyChoice(['Female', 'Male', 'Transgender',])


class StateFactory(DjangoModelFactory):
    class Meta:
        model = models.State
        django_get_or_create = ('text',)
    
    text = factory.fuzzy.FuzzyChoice(['Victoria', 'Sydney', 'South Australia',])


class CareerStageFactory(DjangoModelFactory):
    class Meta:
        model = models.CareerStage
        django_get_or_create = ('text',)
    
    text = factory.fuzzy.FuzzyChoice(['Student', 'Postdoc', 'Lab Head',])


class AboriginalOrTorresFactory(DjangoModelFactory):
    class Meta:
        model = models.AboriginalOrTorres
        django_get_or_create = ('text',)
    
    text = factory.fuzzy.FuzzyChoice(['No', 'Yes', 'Prefer not say',])