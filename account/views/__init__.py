import logging

import django.contrib.auth.views as auth_views
from django.conf import settings
from django.contrib import auth
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from . import submitter, reviewer, assigner, chair
from .. import models

logger = logging.getLogger('django')

__all__ = [
    'submitter',
    'reviewer',
    'assigner',
    'chair',
    'login_with_orcid',
    'staff_login',
    'logout',
    'orcid_login_error',
    'reset_password',
    'ProfileView',
]


# Authentication views
# --------------------------------------------------------------------------- #
def login_with_orcid(request):
    if not settings.DEBUG:
        return redirect("account:social:begin", "orcid")
    else:
        return redirect('account:staff_login')


def staff_login(request):
    return auth_views.LoginView.as_view()(request)


def logout(request):
    auth.logout(request)
    return redirect("account:profile")


def orcid_login_error(request):
    return render(request, "account/orcid_error.html")


def reset_password(request):
    return auth_views.LoginView.as_view()(request)


# Profile views
# -------------------------------------------------------------------------- #
class ProfileView(TemplateView):
    """
    Profile view. Delegates to the correct function based on the user's group.
    """
    template_name = 'account/profile.html'
    http_method_names = ('get', 'post',)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account:orcid_login")

        reviewer_group = models.UserGroups.get_group(
            models.UserGroups.REVIEWER)
        assigner_group = models.UserGroups.get_group(
            models.UserGroups.ASSIGNER)
        chair_group = models.UserGroups.get_group(
            models.UserGroups.CONFERENCE_CHAIR)
        submitter_group = models.UserGroups.get_group(
            models.UserGroups.SUBMITTER)

        if submitter_group in self.request.user.groups.all():
            return submitter.ProfileView.as_view()(request)
        elif reviewer_group in self.request.user.groups.all():
            return reviewer.ProfileView.as_view()(request)
        elif assigner_group in self.request.user.groups.all():
            return assigner.ProfileView.as_view()(request)
        elif chair_group in self.request.user.groups.all():
            return chair.ProfileView.as_view()(request)
        else:
            raise Http404()


class EditProfileView(TemplateView):
    """
    Edit Profile view. Delegates to the correct function based on the
    user's group.
    """
    template_name = 'account/profile.html'
    http_method_names = ('get', 'post',)

    def dispatch(self, request, *args, **kwargs):
        reviewer_group = models.UserGroups.get_group(
            models.UserGroups.REVIEWER)
        submitter_group = models.UserGroups.get_group(
            models.UserGroups.SUBMITTER)

        if submitter_group in self.request.user.groups.all():
            return submitter.EditProfileView.as_view()(request)
        elif reviewer_group in self.request.user.groups.all():
            return reviewer.EditProfileView.as_view()(request)
        else:
            raise Http404()
