import csv
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
            'categories',
            'submitter',
            'affiliation',
            'career_stage',
            'gender',
            'state',
            'aboriginal/torres',
            'accepted',
            'score',
        ]
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
                'title': abstract.title.replace('\n', ' '),
                'content': abstract.text.replace('\n', ' '),
                'contribution': abstract.contribution.replace('\n', ' '),
                'authors': abstract.authors,
                'affiliations': abstract.author_affiliations,
                'keywords': ','.join([x.text for x in abstract.keywords.all()]),
                'categories': ','.join([x.text for x in abstract.categories.all()]),
                'submitter': profile.display_name,
                'affiliation': profile.affiliation,
                'career_stage': profile.career_stage.text,
                'gender': profile.gender.text,
                'state': profile.state.text,
                'aboriginal/torres': profile.aboriginal_or_torres.text,
                'accepted': abstract.accepted,
                'score': abstract.score,
            }
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
                'reason': application.text,
                'other_funding': application.other_funding
            }
            dict_rows.append(row)
        writer.writerows(dict_rows)
        return response
