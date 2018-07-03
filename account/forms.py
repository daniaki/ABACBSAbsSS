from django import forms
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()


class ProfileForm(forms.ModelForm):
    """
    Subclasses `ProfileForm` asking for several additional fields that
    should not be editable post registration.
    """
    class Meta:
        model = models.Profile
        fields = (
            'email', 'affiliation', 'aboriginal_or_torres',
            'gender', 'career_stage', 'state',
        )
        
    def __init__(self, *args, **kwargs):
        #TODO: Fix error message for abo/torre
        self.field_order = (
            'email',
            'affiliation',
            'career_stage',
            'gender',
            'aboriginal_or_torres',
            'state',
        )
        super().__init__(*args, **kwargs)

