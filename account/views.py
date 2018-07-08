import logging

import django.contrib.auth.views as auth_views
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse

from abstract import forms as abstract_forms
from abstract import models as abstract_models
from abstract.models import Review, Assignment

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
    users_group = None
    http_method_names = ('get', 'post',)

    @staticmethod
    def ajax_error(msg):
        return JsonResponse(data={'error': msg})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = {
            'text_label': Review._meta.get_field('text').verbose_name,
            'text_help': Review._meta.get_field('text').help_text,

            'score_content_label': Review._meta.get_field(
                'score_content').verbose_name,
            'score_content_help': Review._meta.get_field(
                'score_content').help_text,

            'score_contribution_label': Review._meta.get_field(
                'score_contribution').verbose_name,
            'score_contribution_help': Review._meta.get_field(
                'score_contribution').help_text,

            'score_interest_label': Review._meta.get_field(
                'score_interest').verbose_name,
            'score_interest_help': Review._meta.get_field(
                'score_interest').help_text,

            'rejection_comment_label': Assignment._meta.get_field(
                'rejection_comment').verbose_name,
            'rejection_comment_help': Assignment._meta.get_field(
                'rejection_comment').help_text,

            'max_score': Review.MAX_SCORE,
            'min_score': Review.MIN_SCORE,
        }
        context.update(**extra_context)
        return context

    def dispatch(self, request, *args, **kwargs):
        reviewer_group = models.UserGroups.get_group(
            models.UserGroups.REVIEWER)
        assigner_group = models.UserGroups.get_group(
            models.UserGroups.ASSIGNER)
        chair_group = models.UserGroups.get_group(
            models.UserGroups.CONFERENCE_CHAIR)
        submitter_group = models.UserGroups.get_group(
            models.UserGroups.SUBMITTER)

        if reviewer_group in self.request.user.groups.all():
            self.template_name = 'account/reviewer_profile.html'
            self.users_group = reviewer_group
        elif assigner_group in self.request.user.groups.all():
            self.template_name = 'account/assigner_profile.html'
            self.users_group = assigner_group
        elif chair_group in self.request.user.groups.all():
            self.template_name = 'account/chair_profile.html'
            self.users_group = chair_group
        else:
            self.template_name = 'account/profile.html'
            self.users_group = submitter_group

        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_ajax()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.post_ajax()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_ajax(self):
        reviewer_group = models.UserGroups.get_group(
            models.UserGroups.REVIEWER)
        assigner_group = models.UserGroups.get_group(
            models.UserGroups.ASSIGNER)
        chair_group = models.UserGroups.get_group(
            models.UserGroups.CONFERENCE_CHAIR)

        if self.users_group == reviewer_group:
            return self.get_ajax_reviewer()
        elif self.users_group == assigner_group:
            return self.get_ajax_assigner()
        elif self.users_group == chair_group:
            return self.get_ajax_chair()
        return self.ajax_error('Unknow group {}'.format(self.users_group))

    def post_ajax(self):
        reviewer_group = models.UserGroups.get_group(
            models.UserGroups.REVIEWER)
        assigner_group = models.UserGroups.get_group(
            models.UserGroups.ASSIGNER)
        chair_group = models.UserGroups.get_group(
            models.UserGroups.CONFERENCE_CHAIR)

        if self.users_group == reviewer_group:
            return self.post_ajax_reviewer()
        elif self.users_group == assigner_group:
            return self.post_ajax_assigner()
        elif self.users_group == chair_group:
            return self.post_ajax_chair()
        return self.ajax_error('Unknow group {}'.format(self.users_group))

    # GET methods
    # ---------------------------------------------------------------------- #
    def get_ajax_reviewer(self):
        return self.ajax_error('not implemented')

    def get_ajax_assigner(self):
        return self.ajax_error('not implemented')

    def get_ajax_chair(self):
        return self.ajax_error('not implemented')

    @staticmethod
    def validate_assignment_id(assignment_id):
        if not assignment_id:
            return None
        if not abstract_models.Assignment.objects.filter(
                id=assignment_id).count():
            return None
        return abstract_models.Assignment.objects.get(id=assignment_id)

    # POST
    # ---------------------------------------------------------------------- #
    def post_ajax_reviewer(self):
        assignment_id = self.request.POST.get('id', None)
        assignment = self.validate_assignment_id(assignment_id)
        if not assignment:
            return self.ajax_error("Invalid assigment id {}".format(
                assignment_id))

        if self.request.POST.get('reject', False):
            form = abstract_forms.RejectAssignmentForm(
                instance=assignment,
                data=self.request.POST
            )
            if not form.is_valid():
                return JsonResponse(
                    data={'error': form.errors.get_json_data(escape_html=True)}
                )
            else:
                review = assignment.review
                assignment.status = abstract_models.Assignment.STATUS_REJECTED
                assignment.save()
                assignment.review = None
                if review:
                    review.delete()
                return JsonResponse(
                    {'success': 'Your rejection has been lodged.'})

        elif self.request.POST.get('accept', False):
            existing_review = getattr(assignment, 'review', None)
            form = abstract_forms.ReviewForm(
                data=self.request.POST,
                reviewer=assignment.reviewer,
                abstract=assignment.abstract,
                instance=existing_review,
            )
            if not form.is_valid():
                return JsonResponse(
                    data={'error': form.errors.get_json_data(escape_html=True)}
                )
            else:
                review = form.save()
                if not existing_review:
                    assignment.review = review
                assignment.rejection_comment = None
                assignment.status = abstract_models.Assignment.STATUS_ACCEPTED
                assignment.save()
                return JsonResponse(
                    {'success': 'Your review has been saved.'})

        else:
            return self.ajax_error(
                "Data is missing 'reject' or 'accept' keys.".format(
                    self.request.method))

    def post_ajax_assigner(self):
        return self.ajax_error('not implemented')

    def post_ajax_chair(self):
        return self.ajax_error('not implemented')
    
    
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
