import logging

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from abstract import forms as abstract_forms
from abstract import models as abstract_models
from abstract.models import Review, Assignment

from .. import models, mixins

logger = logging.getLogger('django')


class ProfileView(LoginRequiredMixin, mixins.GroupRestrictedView,
                  mixins.AjaxView, TemplateView):
    """
    Profile view for assigners to assign abstracts to reviewers. Supports
    post AJAX.
    """
    template_name = 'account/assigner_profile.html'
    group_names = (models.UserGroups.ASSIGNER,)
    http_method_names = ('get', 'post',)

