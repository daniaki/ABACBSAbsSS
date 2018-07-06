import logging

import django.contrib.auth.views as auth_views
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse

from . import forms, models
from .mixins import CompleteProfileRequired, GroupRestrictedView


logger = logging.getLogger('django')


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
# --------------------------------------------------------------------------- #
class EditProfileView(LoginRequiredMixin, GroupRestrictedView, FormView):
    """
    Edit the profile settings of a user. Only viewable by a submitter.
    """
    form_class = forms.ProfileForm
    success_url = '/profile/'
    template_name = 'account/edit_profile.html'
    group_name = models.UserGroups.SUBMITTER
    
    def form_valid(self, form):
        form.save(commit=True)
        self.request.user.profile.completed_intial_login = True
        self.request.user.save()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.profile
        return kwargs


class ProfileView(LoginRequiredMixin, CompleteProfileRequired, TemplateView):
    """
    Profile view. Swaps out the template depending on the requesting user's
    group. Also handles any ajax requests, usually for getting abstract data.
    """
    template_name = 'account/profile.html'
    
    def get_ajax(self):
        return JsonResponse(data={})
    
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_ajax()
        
        user_groups = self.request.user.groups.all()
        if models.UserGroups.get_group(models.UserGroups.REVIEWER) \
                in user_groups:
            self.template_name = 'account/reviewer_profile.html'
        elif models.UserGroups.get_group(models.UserGroups.ASSIGNER) \
                in user_groups:
            self.template_name = 'account/assigner_profile.html'
        elif models.UserGroups.get_group(models.UserGroups.CONFERENCE_CHAIR) \
                in user_groups:
            self.template_name = 'account/chair_profile.html'
        else:
            self.template_name = 'account/profile.html'
        
        return super().get(request, *args, **kwargs)
    
    
class ScholarshipApplicationView(LoginRequiredMixin,
                                 CompleteProfileRequired,
                                 GroupRestrictedView,
                                 FormView):
    """
    Basic view handling the Scholarship application creation, edit and
    deletion functionality. Links the scholarship to the user's instance
    model.
    """
    group_name = models.UserGroups.SUBMITTER
    form_class = forms.ScholarshipApplicationForm
    success_url = '/profile/'
    template_name = 'account/scholarship_application.html'
    
    def get(self, request, *args, **kwargs):
        if self.request.GET.get('delete', False) == 'True':
            application = getattr(
                self.request.user, 'scholarship_application', None)
            if application:
                application.delete()
                messages.success(request, "Your travel scholarship "
                                 "application has been deleted.")
                return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save(commit=True)
        if self.kwargs.get('has_existing', False):
            msg = 'Your scholarship application has been updated.'
        else:
            msg = 'Your scholarship application has been lodged.'
        messages.success(self.request, msg)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        application = getattr(
            self.request.user, 'scholarship_application', None)
        if application:
            kwargs['instance'] = application
            self.kwargs['has_existing'] = True
        else:
            self.kwargs['has_existing'] = False
        return kwargs
