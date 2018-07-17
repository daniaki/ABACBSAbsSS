from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.mixins import UserKwargsMixin, SetUserOnSaveMixin
from abstract.fields import FlexibleModelMultipleChoiceField
from abstract.models import Keyword

from . import models


User = get_user_model()


class SubmitterProfileForm(forms.ModelForm):
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


class ReviewerProfileForm(forms.ModelForm):
    """Profile form for reviewers"""
    class Meta:
        model = models.Profile
        fields = (
            'email', 'affiliation', 'state', 'career_stage',
            'keywords',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keywords'] = FlexibleModelMultipleChoiceField(
            klass=Keyword,
            to_field_name='text',
            label='Keywords',
            required=True,
            queryset=Keyword.objects.all(),
            widget=forms.SelectMultiple(
                attrs={"class": "select2 select2-token-select"}
            ),
            help_text=self.fields['keywords'].help_text,
        )

    def _save_m2m(self):
        for kw in self.cleaned_data.get('keywords', []):
            kw.save()
        return super()._save_m2m()


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
    
    
class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        required=True, label='Email',
        help_text='Please enter the email address associated with your account.'
    )
    
    def clean_email(self):
        self.profile = None
        email = self.cleaned_data.get('email', None)
        profile = [
            p for p in models.Profile.objects.filter(email=email)
            if models.UserGroups.get_group(models.UserGroups.SUBMITTER)
               not in p.user.groups.all()
        ]
        
        if not len(profile):
            raise ValidationError(
                "There are no accounts associated with this email address.")
        self.profile = profile[0]
        return email
