import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from account.factories import SubmitterFactory, ReviewerFactory, \
    AssignerFactory, ConferenceChairFactory
from abstract.factories import AbstractFactory
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
                "Created user with username 'student' "
                "and password '{}'.\n".format(password))
            usera = SubmitterFactory(username="student")
            
            profile = usera.profile
            profile.completed_intial_login = True
            profile.career_stage = CareerStageFactory(
                text=settings.STUDENT_STAGE)
            profile.save()
            AbstractFactory(submitter=usera)
            AbstractFactory(submitter=usera)
            AbstractFactory(submitter=usera)
            
            sys.stdout.write(
                "Created user with username 'reviewer' "
                "and password '{}'.\n".format(password))
            userb = ReviewerFactory(username="reviewer")
            
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