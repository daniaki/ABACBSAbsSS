from django.core.management.base import BaseCommand
from django.db import transaction

from abstract.models import Abstract


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            for abstract in Abstract.objects.all():
                old_authors = abstract.authors
                old_author_affiliations = abstract.author_affiliations
                
                new_authors = '\n'.join(
                    [x.strip() for x in old_authors.split('; ')])
                new_author_affiliations = '\n'.join(
                    [x.strip() for x in old_author_affiliations.split('; ')])
                
                if len(new_authors.split('\n')) != len(new_author_affiliations.split('\n')):
                    raise ValueError(
                        "Lengths are not equal {} ({}) vs {} ({}).".format(
                            new_authors, len(new_authors.split('\n')),
                            new_author_affiliations, len(new_author_affiliations.split('\n'))
                        ))
                
                if len(new_authors.split('\n')) != len(old_authors.split('; ')):
                    raise ValueError(
                        "Author data is different after replace.".format(
                            old_authors.split('; '),
                            new_authors.split('\n'),
                        ))
                
                if len(new_author_affiliations.split('\n')) != len(old_author_affiliations.split('; ')):
                    raise ValueError(
                        "Affiliation data is different after replace.".format(
                            old_authors.split('; '),
                            new_authors.split('\n'),
                        ))

                abstract.authors = new_authors
                abstract.author_affiliations = new_author_affiliations
                abstract.save()
