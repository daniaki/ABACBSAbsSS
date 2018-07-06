from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError

from core import mixins

from . import models, fields


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
        return ', '.join([
            x.strip() for x in
            self.cleaned_data.get('authors', '').split(',')
            if x.strip()
        ])
    
    def clean_author_affiliations(self):
        return ', '.join([
            x.strip() for x in
            self.cleaned_data.get('author_affiliations', '').split(',')
            if x.strip()
        ])
        
    def clean_categories(self):
        if self.user is None:
            return self.cleaned_data.get('categories', None)
        
        categories = self.cleaned_data.get('categories', [])
        is_student = str(self.user.profile.career_stage).lower() == \
                     settings.STUDENT_STAGE.lower()
        student_category = models.PresentationCategory.objects.get(
            text=settings.STUDENT_CATEGORY)
        applied_as_student = student_category in categories
        
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
                'author_affiliations',
                ('The number of authors affiliations must be the same as '
                'the number of authors. Please separate entries with commas.')
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
    