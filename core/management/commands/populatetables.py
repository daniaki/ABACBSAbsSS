import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from demographic import models
from core import models as core_models

BASE_DIR = Path()
DATA_DIR = BASE_DIR / 'data'


class Command(BaseCommand):
    """Populates the gender, state and career stage tables."""
    def handle(self, *args, **options):
        sys.stdout.write("Creating states.\n")
        with open(DATA_DIR / 'states.txt') as fp:
            states = [
                x.strip().capitalize() for x in fp.readlines() if x.strip()]
            for state in states:
                model, created = models.State.objects.get_or_create(
                    name=state
                )
                if created:
                    sys.stdout.write("\tCreated state {}.\n".format(state))
                else:
                    sys.stdout.write("\t{} already exists.\n".format(state))

        sys.stdout.write("Creating genders.\n")
        with open(DATA_DIR / 'genders.txt') as fp:
            genders = [
                x.strip().capitalize() for x in fp.readlines() if x.strip()]
            for gender in genders:
                model, created = models.Gender.objects.get_or_create(
                    type=gender
                )
                if created:
                    sys.stdout.write("\tCreated gender {}.\n".format(gender))
                else:
                    sys.stdout.write("\t{} already exists.\n".format(gender))

        sys.stdout.write("Creating career stages.\n")
        with open(DATA_DIR / 'career_stages.txt') as fp:
            stages = [
                x.strip().capitalize() for x in fp.readlines() if x.strip()]
            for stage in stages:
                model, created = models.CareerStage.objects.get_or_create(
                    name=stage
                )
                if created:
                    sys.stdout.write("\tCreated stage {}.\n".format(stage))
                else:
                    sys.stdout.write("\t{} already exists.\n".format(stage))

        sys.stdout.write("Creating keywords.\n")
        with open(DATA_DIR / 'keywords.txt') as fp:
            keywords = [
                x.strip().capitalize() for x in fp.readlines() if x.strip()]
            for keyword in keywords:
                model, created = core_models.Keyword.objects.get_or_create(
                    text=keyword
                )
                if created:
                    sys.stdout.write("\tCreated keyword {}.\n".format(keyword))
                else:
                    sys.stdout.write("\t{} already exists.\n".format(keyword))
