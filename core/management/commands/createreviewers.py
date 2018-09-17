import sys
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from account.factories import ReviewerFactory

User = get_user_model()


BASE_DIR = Path(str(Path(__file__))).parents[3]
DATA_DIR = BASE_DIR / 'data'

accounts = []
with open(str(DATA_DIR / 'reviewers.csv'), 'rt') as fp:
    for line in fp:
        name, email = [x.strip() for x in line.strip().split(',')]
        accounts.append((name, email))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for name, email in accounts:
                first, *last = name.split(' ')
                uname = '{}.{}'.format(
                    first.lower()[0],
                    '.'.join([x.strip().lower() for x in last])
                )
                account = ReviewerFactory(
                    username=uname,
                    email=email,
                    first_name=name,
                    last_name='',
                )
                password = User.objects.make_random_password()
                account.set_password(password)
                sys.stdout.write("{}\t{},{}\n".format(
                    account.email, account.username, password,
                ))