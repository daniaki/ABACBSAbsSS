import logging

from social_django.models import UserSocialAuth

from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver
from django.core.mail import send_mail

from core.models import TimeStampedModel


User = get_user_model()
logger = logging.getLogger('django')


class Profile(TimeStampedModel):
    """
    A Profile is associated with a user.

    Attributes
    ----------
    user : `models.OnOneToOneField`
        The foreign key relationship associating a profile with a user.

    email : `models.EmailField`, default: None.
        Email address associated with the user's profile. Inherits from
        User instance.

    affiliation : `models.CharField`
        The primary affiliation of a user.

    funding_statement : `models.TextField
        A short description of why this application has applied for funding.

    aboriginal_or_torres: `models.NullBooleanField`
        Indicates if this user is  an Aboriginal or Torres Strait Islander.
        If None, then they have chosen to not disclose this information.

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(
        default=None, blank=True, null=True,
        verbose_name='Email address',
    )
    affiliation = models.CharField(
        max_length=64, null=False, blank=False,
        default=None, verbose_name="Primary Affliation",
    )
    funding_statement = models.TextField(
        null=True, blank=True, default=None,
        verbose_name="Statement",
    )
    aboriginal_or_torres = models.NullBooleanField(
        null=True,
        blank=False,
        default=False,
        verbose_name="Aboriginal or Torres Strait Islander",
        choices=(
            (True, 'Yes'), (False, 'No'),
            (None, 'Prefer not to say')
        ),
    )

    def email_user(self, subject, message, from_email=None, **kwargs):
        email = self.email or self.user.email
        if email:
            kwargs = dict(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email],
            )
            send_mail(**kwargs)
        else:
            logger.warning(
                "Tried email user {uname} from Profile but could not find an "
                "email address.".format(uname=self.user.username)
            )

    @property
    def applied_for_funding(self):
        return bool(self.funding_statement)


# Post Save signals
# -------------------------------------------------------------------------- #
@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Post-save signal invoked when a new user is saved/created. Creates a
    new profile for the user if this a first time call.
    """
    if created:
        Profile.objects.create(
            user=instance, email=None if not instance.email else instance.email
        )


@receiver(models.signals.post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Saves profile whenever associated user is saved.
    """
    instance.profile.save()
