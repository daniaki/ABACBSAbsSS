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


class State(TimeStampedModel):
    """States that a user may have residence in."""
    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )


class CareerStage(TimeStampedModel):
    """Career stages that are selectable by a user."""
    name = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        default=None,
        unique=True,
    )


