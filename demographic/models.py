from django.db import models
from core.models import TimeStampedModel


class Gender(TimeStampedModel):
    """Gender selections associated with a user"""
    text = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.text


class State(TimeStampedModel):
    """States that a user may have residence in."""
    text = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.text


class CareerStage(TimeStampedModel):
    """Career stages that are selectable by a user."""
    text = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.text


class AboriginalOrTorres(TimeStampedModel):
    """Custom options indicating Aboriginal or Torres."""
    text = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )
    
    def __str__(self):
        return self.text


