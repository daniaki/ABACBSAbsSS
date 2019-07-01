import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from account.models import UserGroups


class Command(BaseCommand):
    def handle(self, *args, **options):
        for group in UserGroups:
            group, created = Group.objects.get_or_create(name=group.value)
            if created:
                sys.stdout.write("Created group {}.\n".format(group))
            else:
                sys.stdout.write("Group {} already exists.\n".format(group))
