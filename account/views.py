import logging

import django.contrib.auth.views as auth_views
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect

from . import forms
from .mixins import CompleteProfileRequired


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
class EditProfileView(LoginRequiredMixin, FormView):
    form_class = forms.ProfileForm
    success_url = '/profile/'
    template_name = 'account/edit_profile.html'
    
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
    template_name = 'account/profile.html'

