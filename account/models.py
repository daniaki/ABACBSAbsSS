import logging
from enum import Enum

from social_django.models import UserSocialAuth

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.dispatch import receiver
from django.core.mail import send_mail

from core.models import TimeStampedModel
from abstract.validators import validate_200_words_or_less

from .utilities import user_is_anonymous


User = get_user_model()
logger = logging.getLogger('django')


class UserGroups(Enum):
    SUBMITTER = 'submitter'
    REVIEWER = 'reviewer'
    ASSIGNER = 'assigner'
    CONFERENCE_CHAIR = 'conference_chair'
    
    def __iter__(self):
        return iter(
            [self.SUBMITTER, self.REVIEWER,
             self.ASSIGNER, self.CONFERENCE_CHAIR]
        )
    
    @classmethod
    def get_group(cls, item):
        if isinstance(item, Enum):
            return Group.objects.get(name=item.value)
        return Group.objects.get(name=item)
    
    @classmethod
    def create_groups(cls):
        for group in cls:
            Group.objects.get_or_create(name=group.value)
            
            
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

    gender : `models.ForeignKey
        The user's identified gender.
        
    state : `models.ForeignKey
        The user's state of residence.
        
    career_stage: `models.ForeignKey`
        The user's career stage.

    aboriginal_or_torres: `models.ForeignKey`
        Indicates if this user is  an Aboriginal or Torres Strait Islander.
        If None, then they have chosen to not disclose this information.

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completed_intial_login = models.BooleanField(null=False, default=False)
    
    # Basic Info
    # ----------------------------------------------------------------------- #
    email = models.EmailField(
        default=None, blank=False, null=True,
        verbose_name='Email address',
    )
    affiliation = models.CharField(
        max_length=64, null=True, blank=False,
        default=None, verbose_name="Primary Affliation",
    )
    
    # Demographic fields
    # ----------------------------------------------------------------------- #
    aboriginal_or_torres = models.ForeignKey(
        to='demographic.AboriginalOrTorres',
        null=True, blank=False,
        on_delete=models.PROTECT,
        verbose_name='Do you identify as an Aboriginal or Torres Strait Islander?',
        related_name='associated_%(class)ss'
    )
    gender = models.ForeignKey(
        to='demographic.Gender',
        null=True, blank=False,
        on_delete=models.PROTECT,
        verbose_name='Gender',
        related_name='associated_%(class)ss'
    )
    career_stage = models.ForeignKey(
        to='demographic.CareerStage',
        null=True, blank=False,
        on_delete=models.PROTECT,
        verbose_name='Career Stage',
        related_name='associated_%(class)ss'
    )
    state = models.ForeignKey(
        to='demographic.State',
        null=True, blank=False,
        on_delete=models.PROTECT,
        verbose_name='State',
        related_name='associated_%(class)ss'
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
    def user_group(self):
        return self.user.groups.first()
    
    @property
    def is_complete(self):
        return self.completed_intial_login
            
    @property
    def is_anon(self):
        """
        Checks if the user associated with this profile is anonymous.
        Returns
        -------
        `bool`
            True if the profile and user are anonymous.
        """
        return user_is_anonymous(self.user)
    
    @property
    def display_name(self):
        """
        Returns the users credit-name from ORCID if one exists for this user,
        otherwise calls `get_full_name`.
        """
        if self.is_anon:
            return None

        social_auth = UserSocialAuth.get_social_auth_for_user(
            self.user).first()
        if not isinstance(social_auth, UserSocialAuth):
            return self.full_name
        else:
            credit_name = social_auth.extra_data.get('credit-name', None)
            if not credit_name:
                return self.full_name
            return credit_name

    @property
    def full_name(self):
        """
        Returns the users full name formatted as "<first> <last>" If the user
        does not have a last name, the first name is returned. If the user has
        neither, then the username is returned.
        """
        if self.is_anon:
            return None
        if not self.user.last_name:
            if not self.user.first_name:
                return self.user.username
            else:
                # support for mononyms
                return self.user.first_name.capitalize()
        else:
            return '{} {}'.format(
                self.user.first_name.capitalize(),
                self.user.last_name.capitalize()
            )
        
        
class ScholarshipApplication(models.Model):
    """A scholarship application model with reference to the submitting user."""
    text = models.TextField(
        verbose_name='Reason', null=False, blank=False, default=None,
        help_text="Please explain why you are applying for this scholarship. "
                  "This field is limited to 200 words or less.",
        validators=[validate_200_words_or_less, ]
    )
    has_other_funding = models.BooleanField(
        null=False, default=False, blank=True,
        verbose_name="Do you have any other sources of funding?",
    )
    other_funding = models.TextField(
        verbose_name='List of other funding sources', null=True,
        blank=True, default=None,
        help_text="Please list any additional sources of funding if applicable.",
    )
    submitter = models.OneToOneField(
        to=User, on_delete=models.CASCADE, null=True, default=None,
        related_name='scholarship_application',
    )
    

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
