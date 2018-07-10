import logging

from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView

from abstract import forms as abstract_forms
from abstract import models as abstract_models
from abstract.models import Review, Assignment
from .. import models, mixins, forms

logger = logging.getLogger('django')


class ProfileView(LoginRequiredMixin, mixins.GroupRestrictedView,
                  mixins.CompleteProfileRequired, mixins.AjaxView,
                  TemplateView):
    """
    Profile view. Swaps out the template depending on the requesting user's
    group. Also handles any ajax requests, usually for getting abstract data.
    """
    template_name = 'account/reviewer_profile.html'
    group_names = (models.UserGroups.REVIEWER,)
    http_method_names = ('get', 'post',)

    @staticmethod
    def validate_assignment_id(assignment_id):
        if not assignment_id:
            return None
        if not abstract_models.Assignment.objects.filter(
                id=assignment_id).count():
            return None
        return abstract_models.Assignment.objects.get(id=assignment_id)

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

    def post_ajax(self):
        assignment_id = self.request.POST.get('id', None)
        assignment = self.validate_assignment_id(assignment_id)
        if not assignment:
            return self.error("Invalid assignment id {}".format(assignment_id))

        if self.request.POST.get('reject', False):
            form = abstract_forms.RejectAssignmentForm(
                instance=assignment,
                data=self.request.POST
            )
            if not form.is_valid():
                return self.error(form.errors.get_json_data(escape_html=True))
            else:
                review = assignment.review
                assignment.status = abstract_models.Assignment.STATUS_REJECTED
                assignment.save()
                assignment.review = None
                if review:
                    review.delete()
                    
                # Notifies the assigner of the decline.
                template_name = "account/assignment_declined_email.html"
                message = render_to_string(template_name, {
                    'assignment': assignment,
                })
                assignment.created_by.profile.email_user(
                    subject="[ABACBSAbsSS] Review assignment declined",
                    message=message,
                )

                return JsonResponse(
                    {'success': 'This review request has been declined.'})

        elif self.request.POST.get('accept', False):
            existing_review = getattr(assignment, 'review', None)
            form = abstract_forms.ReviewForm(
                data=self.request.POST,
                reviewer=assignment.reviewer,
                abstract=assignment.abstract,
                instance=existing_review,
            )
            if not form.is_valid():
                return self.error(form.errors.get_json_data(escape_html=True))
            else:
                review = form.save()
                if not existing_review:
                    assignment.review = review
                assignment.rejection_comment = None
                assignment.status = abstract_models.Assignment.STATUS_ACCEPTED
                assignment.save()
                
                # Notifies the assigner of the decline.
                template_name = "account/assignment_accepted_email.html"
                message = render_to_string(template_name, {
                    'assignment': assignment,
                })
                assignment.created_by.profile.email_user(
                    subject="[ABACBSAbsSS] Review assignment accepted",
                    message=message,
                )
                
                return JsonResponse({'success': 'Your review has been saved.'})

        else:
            return self.error(
                "Data is missing 'reject' or 'accept' keys.".format(
                    self.request.method))


class EditProfileView(LoginRequiredMixin, mixins.GroupRestrictedView,
                      FormView):
    """
    Edit the profile settings of a user. Only viewable by a submitter.
    """
    form_class = forms.ReviewerProfileForm
    success_url = '/profile/'
    template_name = 'account/edit_profile.html'
    group_names = (models.UserGroups.REVIEWER,)

    def form_valid(self, form):
        form.save(commit=True)
        self.request.user.profile.set_profile_as_complete()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.profile
        return kwargs
