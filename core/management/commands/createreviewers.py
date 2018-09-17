import sys
import random
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from account.factories import ReviewerFactory

User = get_user_model()


BASE_DIR = Path(str(Path(__file__))).parents[3]
DATA_DIR = BASE_DIR / 'data'

accounts = []
with open(DATA_DIR / 'reviewers.csv') as fp:
    for line in fp:
        print(line.split(','))
        name, email = [x.strip() for x in line.strip().split(',')]
        accounts.append((name, email))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for name, email in accounts:
                account = ReviewerFactory(
                    username=name.replace(' ', '-').lower(),
                    email=email,
                    first_name=name,
                    last_name='',
                )
                password = User.objects.make_random_password()
                account.set_password(password)
                sys.stdout.write("Created account {},{},{},{}\n".format(
                    account.username, account.first_name, account.email,
                    password
                ))
                account.delete()