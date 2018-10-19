from pathlib import Path

from django.core.management.base import BaseCommand

from abstract.models import Abstract
from account.views.chair import format_text

BASE_DIR = Path(str(Path(__file__))).parents[3]
DATA_DIR = BASE_DIR / 'data'


class Command(BaseCommand):
    """Populates the gender, state and career stage tables."""
    def handle(self, *args, **options):
        with open(str(DATA_DIR / 'emails.tsv'), 'wt') as fp:
            fp.write("title\temail\tname\n")
            for abstract in Abstract.objects.all():
                title = format_text(abstract.title)
                email = abstract.submitter.profile.email
                name = abstract.submitter.profile.display_name
                fp.write('{}\t{}\t{}\n'.format(title, email, name))
