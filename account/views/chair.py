import logging

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages

from abstract import models as abstract_models
from demographic.utilities import compute_statistics

from .. import models, mixins

logger = logging.getLogger('django')


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
