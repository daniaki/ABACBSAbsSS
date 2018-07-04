from django.db import models
from core.models import TimeStampedModel


class Gender(TimeStampedModel):
    """Gender selections associated with a user"""
    type = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.type


class State(TimeStampedModel):
    """States that a user may have residence in."""
    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.name


class CareerStage(TimeStampedModel):
    """Career stages that are selectable by a user."""
    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    STUDENT = 'student'
    
    def __str__(self):
        return self.name


class AboriginalOrTorres(TimeStampedModel):
    """Custom options indicating Aboriginal or Torres."""
    type = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.type


