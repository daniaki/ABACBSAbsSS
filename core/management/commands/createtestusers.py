import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from account.factories import UserFactory

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
                "Created user with username 'usera' "
                "and password '{}'.\n".format(password))
            usera = UserFactory(username="usera")

            sys.stdout.write(
                "Created user with username 'userb' "
                "and password '{}'.\n".format(password))
            userb = UserFactory(username="userb")
            
            sys.stdout.write(
                "Created user with username 'userc' "
                "and password '{}'.\n".format(password))
            userc = UserFactory(username="userc")

            usera.set_password(password)
            usera.save()

            userb.set_password(password)
            userb.save()

            userc.set_password(password)
            userc.save()