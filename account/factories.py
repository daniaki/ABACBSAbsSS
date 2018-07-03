import random
import factory.fuzzy
import factory.faker

from django.contrib.auth.models import User


def UserFactory(username=None, password=None, first_name=None,
                last_name=None, email=None, **kwargs):
    """
    Test fixture factory for the user class which sets username,
    first_name, last_name and password.
    """
    names = list(zip(
        ['Spike', 'Jet', 'Faye', 'Ed', 'Ein'],
        ['Spiegel', 'Black', 'Valentine', 'Ed', 'Ein']
    ))
    if email is None:
        email = factory.faker.Faker('email').generate({})
    if username is None:
        username = factory.fuzzy.FuzzyText(length=8).fuzz()
    if password is None:
        password = factory.fuzzy.FuzzyText(length=16).fuzz()

    if User.objects.filter(username=username).count():
        return User.objects.filter(username=username).first()

    first, last = random.choice(names)
    if first_name is None:
        first_name = first
    if last_name is None:
        last_name = last

    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        **kwargs
    )
    user.set_password(password)
    return user