from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.text import mark_safe

from core import mixins

from account.models import UserGroups
from abstract.models import Assignment

from . import models, fields


User = get_user_model()


class AbstractForm(mixins.UserKwargsMixin,
                   mixins.SetUserOnSaveMixin,
                   forms.ModelForm):
    """Basic form for an abstract submission."""
    user_kwarg = 'user'
    user_field = 'submitter'
    
    class Meta:
        model = models.Abstract
        fields = ('title', 'text', 'contribution', 'authors',
                  'author_affiliations', 'keywords', 'categories')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keywords'] = fields.FlexibleModelMultipleChoiceField(
            klass=models.Keyword,
            to_field_name='text',
            label='Keywords',
            required=True,
            queryset=models.Keyword.objects.all(),
            widget=forms.SelectMultiple(
                attrs={"class": "select2 select2-token-select"}
            ),
            help_text=self.fields['keywords'].help_text,
        )
        self.fields['categories'] = forms.ModelMultipleChoiceField(
            label='Presentation category',
            required=True,
            queryset=models.PresentationCategory.objects.all(),
            widget=forms.CheckboxSelectMultiple(),
            help_text=self.fields['categories'].help_text,
        )
        
    def clean_authors(self):
        return '; '.join([
            x.strip() for x in
            self.cleaned_data.get('authors', '').split('\n')
            if x.strip()
        ])
    
    def clean_author_affiliations(self):
        return '; '.join([
            x.strip() for x in
            self.cleaned_data.get('author_affiliations', '').split('\n')
            if x.strip()
        ])

    def clean(self):
        cleaned_data = super().clean()
        authors = cleaned_data.get('authors', '')
        author_affiliations = cleaned_data.get('author_affiliations', '')
        if len(authors.split(';')) != len(author_affiliations.split(';')):
            self.add_error(
                'authors',
                (
                    'The number of authors must be the same as the number of '
                    'author affiliations. Each author must start on a new line.'
                )
            )
            self.add_error(
                'author_affiliations',
                (
                    'The number of authors affiliations must be the same as '
                    'the number of authors. Each affiliation must start on a '
                    'new line.'
                )
            )
        return cleaned_data
    
    def _save_m2m(self):
        for kw in self.cleaned_data.get('keywords', []):
            kw.save()
        return super()._save_m2m()


class ReviewForm(mixins.ExtraKwargsMixin,
                 mixins.SetFieldsOnSaveMixin,
                 forms.ModelForm):
    """Form filled out by a reviewer which rates an abstract."""
    extra_kwargs = ('reviewer', 'abstract',)
    extra_fields = ('reviewer', 'abstract',)
    
    class Meta:
        model = models.Review
        fields = ('text', 'score_content',
                  'score_contribution', 'score_interest',)


class RejectAssignmentForm(forms.ModelForm):
    """
    Form filled out by a reviewer which rejects an abstract. Requires
    instance to be passed in.
    """
    class Meta:
        model = models.Assignment
        fields = ('rejection_comment',)


class AssingmentForm(mixins.ExtraKwargsMixin, forms.Form):
    """Form to add/remove reviewers to an abstract."""
    extra_kwargs = ('abstract', 'assigner',)

    def label_from_instance(self, obj):
        state = obj.profile.state
        return '{uname} | {name} | {state} | {kws}'.format(
            uname=obj.username,
            name=obj.profile.full_name,
            state='Unknown state' if not state else state.text,
            kws=', '.join([kw.text for kw in obj.profile.keywords.all()]) \
                or 'No keywords',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reviewers = User.objects.filter(groups__name=UserGroups.REVIEWER.value)
        self.fields['reviewers'] = forms.ModelMultipleChoiceField(
            label='Reviewers',
            help_text="Assign reviewers to or remove from this abstract.",
            required=False,
            queryset=reviewers,
            widget=forms.SelectMultiple(
                attrs={"class": "select2 select2-token-select"},
            )
        )
        if not self.abstract:
            raise AttributeError("`abstract` cannot be None.")
        if not self.assigner:
            raise AttributeError("`reviewer` cannot be None.")

        self.fields['reviewers'].label_from_instance = self.label_from_instance

    def clean_reviewers(self):
        qs = self.cleaned_data.get('reviewers', [])
        reviewer_group = UserGroups.get_group(UserGroups.REVIEWER)
        qs = [u for u in list(qs) if reviewer_group in u.groups.all()]
        return qs
    
    def save(self):
        removed = []
        added = []
        for user in self.abstract.assigned_reviewers:
            if user not in self.cleaned_data.get('reviewers', []):
                removed.append(user)
        for user in self.cleaned_data.get('reviewers', []):
            if user not in self.abstract.assigned_reviewers:
                added.append(user)
                
        for user in removed:
            template_name = "account/assignment_removed.html"
            message = render_to_string(template_name, {
                'abstract': self.abstract,
                'reviewer': user
            })
            user.profile.email_user(
                subject='[ABACBSAbsSS] Assignment removed.',
                message=message,
            )
            if Assignment.objects.filter(
                    abstract=self.abstract, reviewer=user).count():
                assignment = Assignment.objects.get(
                    abstract=self.abstract, reviewer=user)
                if assignment.review:
                    assignment.review.delete()
                assignment.delete()
        
        for user in added:
            Assignment.objects.create(
                reviewer=user, abstract=self.abstract,
                created_by=self.assigner
            )
            template_name = "account/assignment_added.html"
            message = render_to_string(template_name, {
                'abstract': self.abstract,
                'reviewer': user
            })
            user.profile.email_user(
                subject='[ABACBSAbsSS] Assignment added.',
                message=message,
            )
        
        return self.abstract
