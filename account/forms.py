from django import forms
from django.contrib.auth import get_user_model

from core.mixins import UserKwargsMixin, SetUserOnSaveMixin

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
        self.field_order = (
            'email',
            'affiliation',
            'career_stage',
            'gender',
            'aboriginal_or_torres',
            'state',
        )
        super().__init__(*args, **kwargs)


class ScholarshipApplicationForm(UserKwargsMixin,
                                 SetUserOnSaveMixin,
                                 forms.ModelForm):
    """Form displayed to users requesting a travel scholarship."""
    user_field = 'submitter'
    user_kwarg = 'user'
    
    class Meta:
        model = models.ScholarshipApplication
        fields = ('text', 'has_other_funding', 'other_funding',)
        
    def clean_other_funding(self):
        return self.cleaned_data.get('other_funding', '').strip()
    
    def clean(self):
        cleaned_data = super().clean()
        other = cleaned_data.get('other_funding', '')
        if cleaned_data.get('has_other_funding', False) and not other:
            self.add_error(
                'other_funding',
                'Please list your additional sources of funding.'
            )
        return cleaned_data