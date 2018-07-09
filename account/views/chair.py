import logging

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from abstract import forms as abstract_forms
from abstract import models as abstract_models
from abstract.models import Review, Assignment

from .. import models, mixins

logger = logging.getLogger('django')


class ProfileView(LoginRequiredMixin, mixins.CompleteProfileRequired,
                  mixins.GroupRestrictedView, mixins.AjaxView, TemplateView):
    """
    Profile view for Chairs to assign abstracts to reviewers and select
    abstracts to accept.
    """
    template_name = 'account/assigner_profile.html'
    users_group = (models.UserGroups.CONFERENCE_CHAIR,)
    http_method_names = ('get', 'post',)
