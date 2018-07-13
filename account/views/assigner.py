import logging

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from abstract import forms as abstract_forms
from abstract.models import Abstract

from .. import models, mixins

User = get_user_model()
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
    extra_context = {
        'reviewers':
            User.objects.filter(
                groups__name=models.UserGroups.REVIEWER.value
            ).order_by('first_name')
    }
    

@login_required
def assign_reviewers_view(request, id):
    allowed_groups = [
        models.UserGroups.get_group(g) for g in (models.UserGroups.ASSIGNER,)
    ]
    allowed = any([g in request.user.groups.all() for g in allowed_groups])
    if not allowed:
        raise PermissionDenied()

    abstract = get_object_or_404(Abstract, id=id)
    form = abstract_forms.AssingmentForm(
        abstract=abstract, assigner=request.user,
        initial={'reviewers': [r.id for r in abstract.assigned_reviewers]}
    )
    if request.method == 'POST':
        form = abstract_forms.AssingmentForm(
            data=request.POST, abstract=abstract, assigner=request.user,
            initial={'reviewers': [r.id for r in abstract.assigned_reviewers]}
        )
        if form.is_valid():
            form.save()
            return redirect('account:assign_reviewers', *(abstract.id,))

    context = {
        'abstract': abstract, 'form': form,
        'reviewers': User.objects.filter(
            groups__name=models.UserGroups.REVIEWER.value)
    }
    return render(request, template_name='account/assign.html', context=context)
