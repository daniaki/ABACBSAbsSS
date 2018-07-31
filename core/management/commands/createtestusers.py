import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from abstract.factories import AbstractFactory, AssignmnetFactory
from account.factories import SubmitterFactory, ReviewerFactory, \
    AssignerFactory, ConferenceChairFactory
from demographic.factories import CareerStageFactory

User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('clear', nargs='?', type=bool, default=False)

    def handle(self, *args, **kwargs):
        if kwargs.get('clear', False):
            if not settings.DEBUG:
                raise ValueError("Cannot clear user table when DEBUG is False")
            else:
                User.objects.all().delete()

        with transaction.atomic():
            password = "1234qwer"
            
            sys.stdout.write(
                "Created user with username 'submitter' "
                "and password '{}'.\n".format(password))
            usera = SubmitterFactory(username="submitter")
            
            profile = usera.profile
            profile.completed_intial_login = True
            profile.career_stage = CareerStageFactory()
            profile.save()
            AbstractFactory(submitter=usera)
            AbstractFactory(submitter=usera)
            AbstractFactory(submitter=usera)
            
            sys.stdout.write(
                "Created user with username 'reviewer' "
                "and password '{}'.\n".format(password))
            userb = ReviewerFactory(username="reviewer")
            assignment = AssignmnetFactory(
                reviewer=userb, abstract=AbstractFactory(submitter=usera)
            )

            sys.stdout.write(
                "Created user with username 'assigner' "
                "and password '{}'.\n".format(password))
            userc = AssignerFactory(username="assigner")
            
            sys.stdout.write(
                "Created user with username 'chair' "
                "and password '{}'.\n".format(password))
            userd = ConferenceChairFactory(username="chair")

            
            usera.set_password(password)
            usera.save()

            userb.set_password(password)
            userb.save()

            userc.set_password(password)
            userc.save()

            userd.set_password(password)
            userd.save()