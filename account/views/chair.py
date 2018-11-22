import csv
import re
import logging

from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.contrib import messages

from abstract import models as abstract_models
from demographic.utilities import compute_statistics

from .. import models, mixins

logger = logging.getLogger('django')


def format_text(text, sep=' '):
    text = re.sub(r'\n+|\t+', ' ', text)
    return ' '.join([x.strip() for x in text.split(sep=sep) if x.strip()])


class ScholarshipListView(LoginRequiredMixin, mixins.GroupRestrictedView,
                          ListView):
    """
    Profile view for Chairs to assign abstracts to reviewers and select
    abstracts to accept.
    """
    model = models.ScholarshipApplication
    group_names = (models.UserGroups.CONFERENCE_CHAIR,)
    template_name = 'account/scholarships.html'
    http_method_names = ('get',)
    queryset = models.ScholarshipApplication.objects.all()


class ProfileView(LoginRequiredMixin, mixins.GroupRestrictedView,
                  mixins.AjaxView, ListView):
    """
    Profile view for Chairs to assign abstracts to reviewers and select
    abstracts to accept.
    """
    model = abstract_models.Abstract
    group_names = (models.UserGroups.CONFERENCE_CHAIR,)
    template_name = 'account/chair_profile.html'
    context_object_name = 'abstract_list'
    http_method_names = ('get', 'post',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if models.UserGroups.CONFERENCE_CHAIR.value \
                in self.request.user.profile.group_names:
            if self.request.GET.get("show_demographics", False):
                context['show_demographics'] = True
        return context
    
    def get_ajax(self):
        abstracts = self.request.GET.getlist('abstracts[]', [])
        for abstract_id in abstracts:
            if not abstract_models.Abstract.objects.filter(
                    id=abstract_id).count():
                return self.error('Could not find abstract id `{}`.'.format(
                    abstract_id
                ))
        abstracts = abstract_models.Abstract.objects.filter(pk__in=abstracts)
        if not abstracts.count():
            abstracts = None
        data = compute_statistics(abstracts)
        return JsonResponse(data=data)
    
    def post_ajax(self):
        abstracts = self.request.POST.getlist('abstracts[]', [])
        for abstract_id in abstracts:
            if not abstract_models.Abstract.objects\
                    .filter(id=abstract_id).count():
                return self.error('Could not find abstract id `{}`.'.format(
                    abstract_id
                ))
        abstracts = abstract_models.Abstract.objects.filter(pk__in=abstracts)

        with transaction.atomic():
            for abstract in abstracts.all():
                abstract.accepted = True
                abstract.save()
                
            for abstract in abstract_models.Abstract.objects.all():
                if abstract not in abstracts:
                    abstract.accepted = False
                    abstract.save()
            messages.success(self.request, "Selection updated.")

        return JsonResponse(data={'success': "Abstracts updated!"})


class DownloadAbstracts(LoginRequiredMixin, mixins.GroupRestrictedView,
                        TemplateView):
    """
    Download a tsv of all abstracts.
    """
    group_names = (models.UserGroups.CONFERENCE_CHAIR,)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/tsv')
        response['Content-Disposition'] = \
            'attachment; filename="abstracts.tsv"'
        columns = [
            'title',
            'content',
            'contribution',
            'authors',
            'affiliations',
            'keywords',
            'submitter',
            'affiliation',
            'career_stage',
            'gender',
            'state',
            'aboriginal/torres',
            'accepted',
            'applied_for_scholarship',
            'score',
            'email',
        ]
        for category in abstract_models.PresentationCategory.objects.all():
            columns.append(category.text.lower())
            
        abstracts = abstract_models.Abstract.objects.all()
        writer = csv.DictWriter(
            response, delimiter='\t', fieldnames=columns,
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        dict_rows = []
        for abstract in abstracts:
            abstract = abstract  # type: abstract_models.Abstract
            submitter = abstract.submitter
            profile = submitter.profile
            row = {
                'title': format_text(abstract.title),
                'content': format_text(abstract.text),
                'contribution': format_text(abstract.contribution),
                'authors': abstract.authors.replace('\n', '|||'),
                'affiliations': abstract.author_affiliations.replace('\n', '|||'),
                'keywords': ','.join([x.text for x in abstract.keywords.all()]),
                'submitter': profile.display_name,
                'affiliation': profile.affiliation,
                'career_stage': None if not profile.career_stage else profile.career_stage.text,
                'gender': None if not profile.gender else profile.gender.text,
                'state': None if not profile.state else profile.state.text,
                'aboriginal/torres': None if not profile.aboriginal_or_torres else profile.aboriginal_or_torres.text,
                'applied_for_scholarship': getattr(abstract.submitter, 'scholarship_application', None) is not None,
                'accepted': abstract.accepted,
                'score': abstract.score,
                'email': format_text(profile.email),
            }
            for category in abstract_models.PresentationCategory.objects.all():
                row[category.text.lower()] = category in abstract.categories.all()
            
            dict_rows.append(row)

        writer.writerows(dict_rows)
        return response
    
    
class DownloadScholarshipApplications(LoginRequiredMixin,
                                      mixins.GroupRestrictedView, TemplateView):
    """
    Profile view for Chairs to assign abstracts to reviewers and select
    abstracts to accept.
    """
    group_names = (models.UserGroups.CONFERENCE_CHAIR,)
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="scholarship_applications.tsv"'

        columns = [
            'applicant',
            'email',
            'career_stage',
            'reason',
            'other_funding',
        ]
        applications = models.ScholarshipApplication.objects.all()
        writer = csv.DictWriter(
            response, delimiter='\t', fieldnames=columns,
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()

        dict_rows = []
        for application in applications:
            application = application  # type: models.ScholarshipApplication
            submitter = application.submitter
            profile = submitter.profile
            row = {
                'applicant': profile.display_name,
                'email': profile.email,
                'career_stage': profile.career_stage.text,
                'reason': format_text(application.text),
                'other_funding': format_text(application.other_funding)
            }
            dict_rows.append(row)
        writer.writerows(dict_rows)
        return response
