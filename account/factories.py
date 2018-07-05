import random
import factory.fuzzy
import factory.faker
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model

from .models import UserGroups


User = get_user_model()

first_names = ['Spike', 'Jet', 'Faye', 'Ed', 'Ein']
last_names = ['Spiegel', 'Black', 'Valentine', 'Wong Hau Pepelu Tivrusky IV', '']
names = list(zip(first_names, last_names))


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.fuzzy.FuzzyText(length=8)
    email = factory.faker.Faker('email')
    first_name = ''
    last_name = ''
    password = factory.PostGenerationMethodCall('set_password', '1234qwerty')
    
    is_staff = False
    is_superuser = False
    is_active = True
    
    @factory.post_generation
    def set_name(self, create, extracted, **kwargs):
        if not create:
            return
        if not self.first_name and not self.last_name:
            first, last = random.choice(names)
            self.first_name = first
            self.last_name = last
        return self


class SubmitterFactory(UserFactory):
    """Submitter user object creation."""
    @factory.post_generation
    def set_group(self, create, extracted, **kwargs):
        if not create:
            return
        group = UserGroups.get_group(UserGroups.SUBMITTER)
        group.user_set.add(self)
        return self


class ReviewerFactory(UserFactory):
    """Reviewer user object creation."""
    @factory.post_generation
    def set_group(self, create, extracted, **kwargs):
        if not create:
            return
        group = UserGroups.get_group(UserGroups.REVIEWER)
        group.user_set.add(self)
        return self
    
    
class AssignerFactory(UserFactory):
    """Assigner user object creation."""
    @factory.post_generation
    def set_group(self, create, extracted, **kwargs):
        if not create:
            return
        group = UserGroups.get_group(UserGroups.ASSIGNER)
        group.user_set.add(self)
        return self


class ConferenceChairFactory(UserFactory):
    """Conference chair user object creation."""
    @factory.post_generation
    def set_group(self, create, extracted, **kwargs):
        if not create:
            return
        group = UserGroups.get_group(UserGroups.CONFERENCE_CHAIR)
        group.user_set.add(self)
        return self
