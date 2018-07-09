from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import PermissionDenied

from . import models


class CompleteProfileRequired:
    """
    Verify that the current user has completed their profile. Must
    be preceded by django's `LoginRequiredMixin`.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()
        
        is_submitter = models.UserGroups.get_group(
            models.UserGroups.SUBMITTER) in request.user.groups.all()
        if not is_submitter:
            return super().dispatch(request, *args, **kwargs)
        
        if not request.user.profile.is_complete:
            return redirect('account:edit_profile')
        return super().dispatch(request, *args, **kwargs)

        
class GroupRestrictedView:
    """Returns `HttpResponseForbidden` if the user is not in the
    specified group. Must be preceded by django's `LoginRequiredMixin`."""
    group_name = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()
        if self.group_name is None:
            return super().dispatch(request, *args, **kwargs)
        group = models.UserGroups.get_group(self.group_name)
        if group not in request.user.groups.all():
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class AjaxView:
    """
    Use this mixin in any view which supports an AJAX entry point.
    """
    @staticmethod
    def error(payload, status_code=None):
        response = JsonResponse(data={'error': payload})
        if status_code:
            response.status_code = status_code
        return response

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.get_ajax()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.post_ajax()
        return super().post(request, *args, **kwargs)

    def get_ajax(self):
        raise NotImplementedError()

    def post_ajax(self):
        raise NotImplementedError()
