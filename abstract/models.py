import uuid
import logging
from enum import Enum

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils.text import mark_safe

from core.models import TimeStampedModel

from . import validators

User = get_user_model()
logger = logging.getLogger('django')


class ScoreCategories(Enum):
    CONTENT = 'content'
    CONTRIBUTION = 'contribution'
    INTEREST = 'interest'
    
    
class Keyword(TimeStampedModel):
    """Keywords that can be associated with abstract submissions."""
    class Meta:
        ordering = ('text',)
    
    text = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.text
    
    
class PresentationCategory(TimeStampedModel):
    """
    Model representing a text of presentation (poster, oral etc...)
    
    Attributes
    ----------
    text: `models.CharField`
        The text name of the text.
    """
    class Meta:
        ordering = ('text',)
     
    text = models.CharField(
        null=False, default=None, blank=False, max_length=128, unique=True
    )
    
    def __str__(self):
        return self.text
    

class Abstract(TimeStampedModel):
    """
    Model representing an abstract.
    
    Attributes
    ----------
    text: `models.TextField`
        The text content of the abstract
        
    title: `models.TextField`
        Title of the abstract
        
    contribution: `models.TextField`
        User's contribution to the work
        
    authors: `models.TextField`
        List of all authors
        
    author_contributions: `models.TextField`
        List of all author affiliations
        
    categories: `models.ManyToManyField`
        The categories of this abstract.
        
    keywords: `models.ManyToManyField`
        The `core.Keywords` associated with this abstract.
        
    submitter: `models.ForeignKey`
        User submitting the abstract.
        
    reviewers: `models.ManyToManyField`
        Reviewers assigned to this abstract.
        
    reviews: `models.RelatedField`
        The related field returning `Review` instances associated with this
        abstract.
    """
    LIST_SEP = ','

    class Meta:
        ordering = ('-creation_date',)
        
    def __str__(self):
        return self.title
    
    # Text Fields
    # ----------------------------------------------------------------------- #
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False, unique=True)
    
    text = models.TextField(
        null=False, default=None, blank=False,
        verbose_name='Abstract',
        help_text='Please describe your abstract using 250 words or less.',
        validators=[validators.validate_250_words_or_less, ]
    )
    title = models.TextField(
        null=False, default=None, blank=False,
        verbose_name='Abstract title',
        help_text='Please title your abstract using 30 words or less.',
        validators=[validators.validate_30_words_or_less, ]
    )
    contribution = models.TextField(
        null=False, default=None, blank=False,
        verbose_name='Your contribution',
        help_text='Please describe your contribution to the research '
                  'detailed in your abstract using 100 words or less.',
        validators = [validators.validate_100_words_or_less, ]
    )
    authors = models.TextField(
        null=False, default=None, blank=True,
        verbose_name='Contributing authors',
        help_text='Please list all contributing authors '
                  'including yourself (new line separated).'
    )
    author_affiliations = models.TextField(
        null=False, default=None, blank=True,
        verbose_name='Contributing author affiliations',
        help_text='Please list the primary affiliations '
                  'of all contributing authors including yourself '
                  '(new line separated).'
    )
    accepted = models.BooleanField(
        null=False, default=False, blank=True, verbose_name='Approve?'
    )
    
    # Linked Fields
    # ----------------------------------------------------------------------- #
    categories = models.ManyToManyField(
        to='abstract.PresentationCategory', related_name='%(class)ss',
        verbose_name='Categories',
        help_text='Please select one or more categories for your abstract. '
                  'You must be registered for the conference and sessions that '
                  'you apply to.',
        related_query_name='%(class)s', blank=False,
    )
    keywords = models.ManyToManyField(
        to='abstract.Keyword', related_name='%(class)ss',
        related_query_name='%(class)s', verbose_name='Keywords',
        help_text='Please assign a few keywords to your abstract. You may '
                  'enter keywords that do not appear in this list by '
                  'pressing Return/Enter on your keyboard.',
        blank=False,
    )
    submitter = models.ForeignKey(
        to=User, related_name='%(class)ss', on_delete=models.CASCADE,
        related_query_name='%(class)s', verbose_name='Submitter',
        null=True, default=None,
    )

    # Properties
    # ----------------------------------------------------------------------- #
    @property
    def has_reviews(self):
        if hasattr(self, 'reviews'):
            return self.reviews.count() > 0
        return False
    
    @property
    def is_assigned(self):
        return self.reviewers.count() > 0

    @property
    def score(self):
        if self.has_reviews:
            return (self.score_content +
                    self.score_contribution +
                    self.score_interest) / 3
        return None
    
    @property
    def score_content(self):
        if self.has_reviews:
            score = 0
            for review in self.reviews.all():
                score += review.score_content
            return score
        return None
    
    @property
    def score_contribution(self):
        if self.has_reviews:
            score = 0
            for review in self.reviews.all():
                score += review.score_contribution
            return score
        return None
    
    @property
    def score_interest(self):
        if self.has_reviews:
            score = 0
            for review in self.reviews.all():
                score += review.score_interest
            return score
        return None
       
    @property
    def reviewers(self):
        """Returns the reviewers who have left a review for this abstract."""
        return User.objects.filter(
            pk__in=[r.reviewer.pk for r in self.reviews.all()]
        )
    
    @property
    def assigned_reviewers(self):
        """
        Returns all reviewers assigned to this abstract including those
        which are pending or have declined review.
        """
        return User.objects.filter(
            pk__in=[a.reviewer.pk for a in self.assignments.all()]
        )
    
    @property
    def pending_assignments(self):
        return self.assignments.filter(status=Assignment.STATUS_PENDING)

    @property
    def declined_assignments(self):
        return self.assignments.filter(status=Assignment.STATUS_REJECTED)

    @property
    def accepted_assignments(self):
        return self.assignments.filter(status=Assignment.STATUS_ACCEPTED)

    @property
    def pending_reviewers(self):
        return User.objects.filter(
            pk__in=[a.reviewer.pk for a in self.pending_assignments]
        ).order_by('first_name')

    @property
    def declined_reviewers(self):
        return User.objects.filter(
            pk__in=[a.reviewer.pk for a in self.declined_assignments]
        ).order_by('first_name')

    @property
    def accepted_reviewers(self):
        return User.objects.filter(
            pk__in=[a.reviewer.pk for a in self.accepted_assignments]
        ).order_by('first_name')
    
    def get_authors(self):
        return self.authors.split('\n')
    
    def get_affiliations(self):
        return self.author_affiliations.split('\n')


class Review(TimeStampedModel):
    """
    A reviewer's review associated with an `Abstract` containing a score
    and comment.

    Attributes
    ----------
    text: `models.TextField`
        The text content of the comment

    reviewer: `models.ForeignKey`
        The reviewer making the comment.

    abstract: `models.ForeignKey`
        The `Abstract` instance the comment was made on.
        
    score_content: `models.IntegerField`
        The integer score based on scientific content.
        
    score_contribution: `models.IntegerField`
        The integer score based on the speaker's contribution
        
    score_interest: `models.IntegerField`
        The integer score based on the reviewer's interest in the
        abstract content and topic.
    """
    MAX_SCORE = 7
    MIN_SCORE = 0
    
    class Meta:
        unique_together = ('reviewer', 'abstract')
        ordering = ('reviewer',)
    
    text = models.TextField(
        null=False, default=None, blank=False, verbose_name='Comments',
        help_text="Please provide a few short comments justifying why "
                  "you have given the scores above."
    )
    reviewer = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='%(class)ss',
        related_query_name='%(class)s', null=False, default=None,
    )
    abstract = models.ForeignKey(
        to=Abstract, on_delete=models.CASCADE, related_name='%(class)ss',
        related_query_name='%(class)s', null=False, blank=None,
    )
    score_content = models.IntegerField(
        null=False, blank=False, default=None, verbose_name="Content",
        help_text="Score based on the abstract's scientific content.",
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
    )
    score_contribution = models.IntegerField(
        null=False, blank=False, default=None, verbose_name="Contribution",
        help_text="Score based on the author's contribution to the work.",
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
    )
    score_interest = models.IntegerField(
        null=False, blank=False, default=None, verbose_name="Interest",
        help_text="Score based on the ability of the "
                  "abstract's contents to hold your interest.",
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
    )


class Assignment(models.Model):
    """Represents an assignment of an abstract to a reviewer"""
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    )

    class Meta:
        ordering = ('reviewer',)
        unique_together = ('reviewer', 'abstract',)
    
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='created_%(class)ss',
        related_query_name='created_%(class)s', null=False, default=None,
    )
    reviewer = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='%(class)ss',
        related_query_name='%(class)s', null=False, default=None,
    )
    abstract = models.ForeignKey(
        to=Abstract, on_delete=models.CASCADE, related_name='%(class)ss',
        related_query_name='%(class)s', null=False, blank=None,
    )
    status = models.CharField(
        null=False, default=STATUS_PENDING, blank=True, max_length=24,
        choices=STATUS_CHOICES, verbose_name='Status'
    )
    rejection_comment = models.TextField(
        blank=False, default=None, null=True,
        verbose_name="Reason",
        help_text="Please give a reason for declining this review assignment."
    )
    review = models.OneToOneField(
        to=Review, on_delete=models.SET_NULL, related_name='%(class)s',
        null=True, blank=None, default=None,
    )
    
    @property
    def get_comment(self):
        return self.rejection_comment