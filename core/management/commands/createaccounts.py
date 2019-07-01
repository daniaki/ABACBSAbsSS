import sys
from pathlib import Path
from csv import DictReader

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from account import factories
from account.models import UserGroups


User = get_user_model()


BASE_DIR = Path(str(Path(__file__))).parents[3]
DATA_DIR = BASE_DIR / 'data'

columns = ["email", "name", "password", "group"]
group_factory = {
    UserGroups.REVIEWER.value: factories.ReviewerFactory,
    UserGroups.ASSIGNER.value: factories.AssignerFactory,
    UserGroups.CONFERENCE_CHAIR.value: factories.ConferenceChairFactory,
}
file_handle = open(str(DATA_DIR / 'accounts.csv'), 'rt')
file_handle.readline()
accounts = DictReader(file_handle, fieldnames=columns)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            sys.stdout.write("email,username,password,group\n")
            for account in accounts:
                print(account)
                email = account['email']
                name = account['name']
                password = account['password']
                group = account['group']
                factory = group_factory[group]

                # Generate a basic username
                first, *last = account['name'].split(' ')
                uname = '{}.{}'.format(
                    first.lower()[0],
                    '.'.join([x.strip().lower() for x in last])
                )

                account = User.objects.filter(username=uname)
                if not account.count():
                    account = factory(
                        username=uname,
                        email=email,
                        first_name=name,
                        last_name='',
                    )
                else:
                    account = account.first()

                account.set_password(password)
                account.save()
                account.profile.save()
                sys.stdout.write("{},{},{},{}\n".format(
                    account.email, account.username, password, group
                ))
