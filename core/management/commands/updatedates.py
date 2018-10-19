import sys
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from abstract import models as abstract_models

BASE_DIR = Path(str(Path(__file__))).parents[3]
DATA_DIR = BASE_DIR / 'data'
server_tz = timezone.get_current_timezone()


class Command(BaseCommand):
    """Populates the gender, state and career stage tables."""
    def handle(self, *args, **options):
        with open(str(DATA_DIR / 'categories.txt')) as fp:
            categories = [
                x.split('\t') for x in
                [x.strip() for x in fp.readlines() if x.strip()]
            ]
            for category, datetime in categories:
                dt = parse_datetime(datetime).astimezone(tz=server_tz)
                model = abstract_models.\
                    PresentationCategory.objects.get(text=category)
                model.closing_date = dt
                model.save()
                sys.stdout.write(
                    "Updated cateogry {} with date {}\n".format(category, dt))