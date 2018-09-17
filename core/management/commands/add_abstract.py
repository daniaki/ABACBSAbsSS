from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from abstract.models import PresentationCategory, Abstract, Keyword

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.get(username='0000-0002-6842-1229')

        title = "EndoVir: A Pipeline for Discovery of Novel Endogenous Viruses"
        text = "Endogenous Viral Elements (EVEs) are part of the host genome and allowhorizontal transmission within a host, but the underlying evolutionarymechanisms are still unclear. Metagenomic sequencing data sets contain a wealthof information, including sequences from viruses. Such datasets present anopportunity to analyze known EVEs and discover new ones.We introduce a new method for extending viral contiguous sequences or contigsthrough the Building Up Domains (BUD) algorithm  that identifies virus DNA fromsequencing experiments. This methodology differs from current virus discoverytools by iteratively building upon sequences that are known to contain a viralprotein domains, and searching for surrounding non-viral protein domains.We designed EndoVir to implement BUD in Python3. To reduce the use of temporaryfiles, data is streamed between processes where possible, e.g. we useMagicBLAST to screen the metagenomic datasets as it can read NCBI’s SRA formatdirectly. Our implementation analyzes the results from each individual pipelinestep and allows real-time parameter adjustment. This approach allows us toadjust for the diversity present in metagenomic data sets."

        contribution = "I wrote the implementation of Endovir"

        authors = """Jan P Buchmann
Karina Zile
Mitchell A. Ellison II
Jacob Waldman
Kristyna Kupkova
Cody Glickman
Andrew Clugston
Paul G. Cantalupo
Vineet Raghu
Ben Busby"""

        author_affiliations = """The University of Sydney, Charles Perkins Centre D17, Sydney, NSW 2006, Australia
NCBI, NLM, NIH, 8600 Rockville Pike MSC 3830, Bethesda, MD 20894, USA
University of Pittsburgh, Biological Sciences Department,Pittsburgh, PA 15224, USA
University of Pittsburgh, Department of Biomedical Informatics, Pittsburgh, PA 15224, USA
Brno University of Technology, Department of Biomedical Engineering, Technicka 12, Brno, 612 00, Czech Republic
University of Colorado Anschutz Medical Campus, Department of Computational Bioscience, Aurora, Colorado 80045
University of Pittsburgh Rangos Research Center, Integrative Systems Biology, Pittsburgh, PA 15224, USA
University of Pittsburgh, Department of Biological Sciences, Pittsburgh, PA 15260, USA
University of Pittsburgh, Department of Computer Science, Pittsburgh, PA 15260, USA
NCBI, NLM, NIH, 8600 Rockville Pike MSC 3830, Bethesda, MD 20894, USA"""

        with transaction.atomic():
            kw1, _ = Keyword.objects.get_or_create(text='bioinformatic pipeline')
            kw2, _ = Keyword.objects.get_or_create(text='endogenous viruses')
            abstract = Abstract.objects.create(
                title=title,
                text=text,
                contribution=contribution,
                authors=authors,
                author_affiliations=author_affiliations,
            )
            abstract.categories.add(
                PresentationCategory.objects.get(
                    text='ABACBS Conference Poster')
            )
            abstract.categories.add(
                PresentationCategory.objects.get(
                    text='ABACBS Conference Talk')
            )
            abstract.keywords.add(kw1)
            abstract.keywords.add(kw2)
            abstract.submitter = user
            abstract.save()
            user.save()
