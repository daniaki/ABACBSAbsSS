from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView
from django.contrib import messages

from core.mixins import CheckClosingDateMixin
from abstract.models import PresentationCategory

from .. import models, forms
from ..mixins import CompleteProfileRequired, GroupRestrictedView


class ScholarshipApplicationView(LoginRequiredMixin,
                                 CompleteProfileRequired,
                                 GroupRestrictedView,
                                 CheckClosingDateMixin,
                                 FormView):
    """
    Basic view handling the Scholarship application creation, edit and
    deletion functionality. Links the scholarship to the user's instance
    model.
    """
    group_names = (models.UserGroups.SUBMITTER,)
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


class ProfileView(LoginRequiredMixin, CompleteProfileRequired,
                  GroupRestrictedView, TemplateView):
    """
    Renders the users abstract submissions
    """
    success_url = '/profile/'
    template_name = 'account/profile.html'
    group_names = (models.UserGroups.SUBMITTER,)
    http_method_names = ('get',)

    def dispatch(self, request, *args, **kwargs):
        closed = PresentationCategory.get_closed_categories()
        if closed.count() > 0:
            messages.info(
                request,
                "The following categories have now been closed: {}. "
                "Submissions under these categories can no longer be "
                "edited or withdrawn.".format(
                    ', '.join(['<b>{}</b>'.format(c.text) for c in closed])
                )
            )
        return super().dispatch(request, *args, **kwargs)


class EditProfileView(LoginRequiredMixin, GroupRestrictedView,
                      CheckClosingDateMixin, FormView):
    """
    Edit the profile settings of a user. Only viewable by a submitter.
    """
    form_class = forms.SubmitterProfileForm
    success_url = '/profile/'
    template_name = 'account/edit_profile.html'
    group_names = (models.UserGroups.SUBMITTER,)

    def form_valid(self, form):
        form.save(commit=True)
        self.request.user.profile.set_profile_as_complete()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.profile
        return kwargs
