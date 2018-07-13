import logging

from django.views.generic import CreateView, UpdateView, DeleteView, \
    DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.contrib import messages

from account.models import UserGroups
from account.mixins import CompleteProfileRequired, GroupRestrictedView

from . import forms, models


logger = logging.getLogger('django')


class SubmissionView(LoginRequiredMixin,
                     GroupRestrictedView,
                     CompleteProfileRequired,
                     CreateView):
    template_name = 'abstract/submit.html'
    form_class = forms.AbstractForm
    success_url = '/profile/'
    context_object_name = 'instance'
    model = models.Abstract
    group_names = UserGroups.SUBMITTER

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        instance = self.object
        messages.success(
            self.request,
            "Submitted abstract with title <strong>'{}'</strong>.".format(
                instance.title
        ))
        return super().get_success_url()
    

class EditSubmissionView(LoginRequiredMixin,
                         GroupRestrictedView,
                         CompleteProfileRequired,
                         UpdateView):
    template_name = 'abstract/edit.html'
    form_class = forms.AbstractForm
    success_url = '/profile/'
    slug_field = 'id'
    pk_url_kwarg = 'id'
    context_object_name = 'instance'
    model = models.Abstract
    group_names = UserGroups.SUBMITTER
    
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().submitter != request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        instance = self.get_object()
        messages.success(
            self.request,
            "Updated abstract with title <strong>'{}'</strong>.".format(
                instance.title
        ))
        return super().get_success_url()


class DeleteSubmissionView(LoginRequiredMixin,
                           GroupRestrictedView,
                           CompleteProfileRequired,
                           DeleteView):
    model = models.Abstract
    success_url = '/profile/'
    slug_field = 'id'
    pk_url_kwarg = 'id'
    context_object_name = 'instance'
    template_name = 'abstract/delete.html'
    group_names = UserGroups.SUBMITTER
    
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().submitter != request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)
        
    def get_success_url(self):
        instance = self.get_object()
        messages.success(
            self.request,
            "Deleted abstract with title <strong>'{}'</strong>.".format(
                instance.title
        ))
        return super().get_success_url()


class AbstractDetailView(LoginRequiredMixin, GroupRestrictedView, DetailView):
    model = models.Abstract
    group_names = (UserGroups.ASSIGNER,
                   UserGroups.CONFERENCE_CHAIR,)
    template_name = 'abstract/abstract_detail.html'
    slug_field = 'id'
    pk_url_kwarg = 'id'
    context_object_name = 'abstract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if UserGroups.CONFERENCE_CHAIR.value \
                in self.request.user.profile.group_names:
            if self.request.GET.get("show_demographics", False):
                context['show_demographics'] = True
        return context
