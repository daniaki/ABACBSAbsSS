import factory.fuzzy
from factory.django import DjangoModelFactory

from account import factories as user_factories

from . import models

MAX_SCORE = models.Review.MAX_SCORE
MIN_SCORE = models.Review.MIN_SCORE


class KeywordFactory(DjangoModelFactory):
    """Create dummy keywords. Unique on text attribute."""
    
    class Meta:
        model = models.Keyword
        django_get_or_create = ('text',)
    
    text = factory.faker.Faker('text', max_nb_chars=10)


class PresentationCategoryFactory(DjangoModelFactory):
    """"""
    class Meta:
        model = models.PresentationCategory
        django_get_or_create = ('text',)
    
    text = factory.fuzzy.FuzzyChoice(['Poster', 'Selected oral',])
    

class AbstractFactory(DjangoModelFactory):
    """Populates an abstract with dummy data"""
    class Meta:
        model = models.Abstract
        
    text = factory.faker.Faker('text', max_nb_chars=1280)
    submitter = factory.SubFactory(user_factories.SubmitterFactory)
    authors = factory.faker.Faker('name')
    author_affiliations = factory.faker.Faker('company')
    title = factory.faker.Faker('text', max_nb_chars=100)
    contribution = factory.faker.Faker('text', max_nb_chars=640)

    @factory.post_generation
    def assign_type(self, created, extracted, *args, **kwargs):
        if not created:
            return
        self.categories.add(PresentationCategoryFactory())
        return self
    
    @factory.post_generation
    def assign_keywords(self, created, extracted, *args, **kwargs):
        if not created:
            return
        self.keywords.add(KeywordFactory())
        return self
   
    @classmethod
    def assign_reviews(cls, abstract, n=3):
        reviews = []
        assigner = user_factories.AssignerFactory()
        for _ in range(n):
            reviewer = user_factories.ReviewerFactory()
            r = ReviewFactory(abstract=abstract, reviewer=reviewer)
            a = AssignmnetFactory(abstract=abstract,
                                  reviewer=reviewer, created_by=assigner)
            a.review = r
            a.save()
            reviews.append(r)
        return reviews
        
    
class ReviewFactory(DjangoModelFactory):
    """Creates a dummy comment with an assigned user and abstract"""
    class Meta:
        model = models.Review
        django_get_or_create = ('reviewer', 'abstract',)
        
    text = factory.faker.Faker('text', max_nb_chars=1275)
    score_content = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    score_contribution = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    score_interest = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    abstract = factory.SubFactory(AbstractFactory)
    reviewer = factory.SubFactory(user_factories.ReviewerFactory)


class AssignmnetFactory(DjangoModelFactory):
    """Creates a dummy review assignment"""
    class Meta:
        model = models.Assignment
        django_get_or_create = ('reviewer', 'abstract')

    abstract = factory.SubFactory(AbstractFactory)
    reviewer = factory.SubFactory(user_factories.ReviewerFactory)
    created_by = factory.SubFactory(user_factories.AssignerFactory)
