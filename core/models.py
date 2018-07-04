import datetime

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class TimeStampedModel(models.Model):
    """
    Represents a time stamped model updating the modification date everytime
    an instance is saved.
    """
    class Meta:
        abstract = True
        ordering = ['-creation_date']

    creation_date = models.DateField(
        default=datetime.date.today,
        verbose_name='Creation date',
    )
    modification_date = models.DateField(
        default=datetime.date.today,
        verbose_name='Modification date',
    )

    def save(self, *args, **kwargs):
        self.modification_date = datetime.date.today()
        return super().save(*args, **kwargs)
