import logging

from django.views.generic import ListView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from abstract import forms as abstract_forms
from abstract.models import Abstract

from .. import models, mixins

logger = logging.getLogger('django')


class ProfileView(LoginRequiredMixin, mixins.GroupRestrictedView,
                  mixins.AjaxView, ListView):
    """
    Profile view for assigners to assign abstracts to reviewers. Supports
    post AJAX.
    """
    template_name = 'account/assigner_profile.html'
    group_names = (models.UserGroups.ASSIGNER,)
    queryset = Abstract.objects.all()
    model = Abstract
    http_method_names = ('get', 'post',)
    

class AssignView(LoginRequiredMixin, mixins.GroupRestrictedView,
                 mixins.AjaxView, DeleteView):
    template_name = 'account/assign.html'
    group_names = (models.UserGroups.ASSIGNER,)
    http_method_names = ('get', 'post',)
    form_class = abstract_forms.AssingmentForm
    success_url = '/profile/'
    
    