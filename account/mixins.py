from django.shortcuts import redirect


class CompleteProfileRequired:
    """Verify that the current user has completed their profile."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account:orcid_login")
        else:
            #TODO: Check user group
            if request.user.profile.is_complete:
                return super().dispatch(request, *args, **kwargs)
            else:
                return redirect('account:edit_profile')