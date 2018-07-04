from django import forms
from django.core.exceptions import ValidationError

from core import mixins
from demographic.models import CareerStage

from . import models, fields


class AbstractForm(mixins.UserKwargsForm, forms.ModelForm):
    """Basic form for an abstract submission."""
    class Meta:
        model = models.Abstract
        fields = ('text', 'title', 'contribution', 'authors',
                  'author_affiliations', 'categories', 'keywords',)
        
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
        self.fields['categories'] = fields.FlexibleModelMultipleChoiceField(
            klass=models.PresentationCategory,
            to_field_name='name',
            label='Presentation category',
            required=True,
            queryset=models.PresentationCategory.objects.all(),
            widget=forms.SelectMultiple(
                attrs={"class": "select2 select2-token-select"}
            ),
            help_text=self.fields['categories'].help_text,
        )
        
    def clean_categories(self):
        categories = self.cleaned_data.get('categories', [])
        is_student = self.user.profile.career_stage.name.lower() == \
                     CareerStage.STUDENT.lower()
        applied_as_student = models.PresentationCategory.STUDENT_CATEGORY in \
                             categories
        if not is_student and applied_as_student:
            raise ValidationError(
                "You must be a student to apply to for a student presentation."
            )
        return self.cleaned_data.get('categories')
           
    def clean(self):
        cleaned_data = super().clean()
        authors = cleaned_data.get('authors', '')
        author_affiliations = cleaned_data.get('author_affiliations', '')
        if len(authors.split(',')) != len(author_affiliations.split(',')):
            self.add_error(
                'authors',
                ('The number of authors must be the same as the number of '
                'author affiliations. Please separate entries with commas.')
            )
            self.add_error(
                'authors',
                ('The number of authors affiliations must be the same as '
                'the number of authors. Please separate entries with commas.')
            )
        return cleaned_data
        
    def save(self, commit=True):
        if not self.user and self.instance.submitter is None:
            raise ValueError("A submitting user must be specified through"
                             "the `user` kwarg at form instantiation.")
        else:
            if self.instance.submitter is not None:
                self.instance.submitter = self.user
        return super().save(commit=commit)
