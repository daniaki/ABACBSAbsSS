import factory.fuzzy
from factory.django import DjangoModelFactory

from account import factories as user_factories

from . import models

MAX_SCORE = models.Comment.MAX_SCORE
MIN_SCORE = models.Comment.MIN_SCORE


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
        django_get_or_create = ('name',)
    
    name = factory.fuzzy.FuzzyChoice(['poster', 'oral', 'student'])
    

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

    @factory.post_generation
    def assign_reviewers(self, created, extracted, *args, **kwargs):
        if not created:
            return
        self.reviewers.add(user_factories.ReviewerFactory())
        return self
    
    @classmethod
    def assign_comments(cls, abstract):
        comments = []
        for reviewer in abstract.reviewers.all():
            comments.append(
                CommentFactory(reviewer=reviewer, abstract=abstract)
            )
        return comments
        
    
class CommentFactory(DjangoModelFactory):
    """Creates a dummy comment with an assigned user and abstract"""
    class Meta:
        model = models.Comment
        django_get_or_create = ('reviewer', 'abstract',)
        
    text = factory.faker.Faker('text', max_nb_chars=1275)
    score_content = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    score_contribution = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    score_interest = factory.fuzzy.FuzzyInteger(low=MIN_SCORE, high=MAX_SCORE)
    abstract = factory.SubFactory(AbstractFactory)
    reviewer = factory.SelfAttribute('abstract.first_reviewer')
