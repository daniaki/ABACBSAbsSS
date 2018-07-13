import logging

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction

from abstract import models as abstract_models
from demographic.models import Gender, CareerStage, State, AboriginalOrTorres

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
        if 'abstracts' not in self.request.GET:
            return self.error("Missing `abstracts` key from GET data.")
    
        abstracts = self.request.GET.getList('abstracts', [])
        for abstract_id in abstracts:
            if not abstract_models.Abstract.objects.filter(
                    id=abstract_id).count():
                return self.error('Could not find abstract id `{}`.'.format(
                    abstract_id
                ))
    
        abstracts = abstract_models.Abstract.objects.filter(pk__in=abstracts)
        data = {'gender': {}, 'stage': {}, 'aot': {}, 'state': {}}
        for gender in Gender.objects.all():
            count = abstracts.filter(
                submitter__profile__gender__text=gender.text).count()
            data['gender'][gender.text] = count
    
        for cs in CareerStage.objects.all():
            count = abstracts.filter(
                submitter__profile__career_stage__text=cs.text).count()
            data['stage'][cs.text] = count
    
        for aot in AboriginalOrTorres.objects.all():
            count = abstracts.filter(
                submitter__profile__aboriginal_or_torres__text=aot.text).count()
            data['aot'][aot.text] = count
    
        for state in State.objects.all():
            count = abstracts.filter(
                submitter__profile__state__text=state.text).count()
            data['state'][state.text] = count
    
        return JsonResponse(data=data)
    
    def post_ajax(self):
        if 'abstracts' not in self.request.POST:
            return self.error("Missing `abstracts` key from POST data.")
        
        abstracts = self.request.POST.getList('abstracts', [])
        for abstract_id in abstracts:
            if not abstract_models.Abstract.objects.filter(id=abstract_id).count():
                return self.error('Could not find abstract id `{}`.'.format(
                    abstract_id
                ))
        abstracts = abstract_models.Abstract.objects.filter(pk__in=abstracts)
        
        with transaction.atomic():
            for abstract in abstracts.all():
                abstract.approved = True
                abstract.save()
                
            for abstract in abstract_models.Abstract.objects.all():
                if abstract not in abstracts:
                    abstract.approved = False
                    abstract.save()

        return JsonResponse(data={'success': "Abstracts updated!"})
