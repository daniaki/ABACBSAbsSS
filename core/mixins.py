from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages

from core.utilities import get_local_closing_date


User = get_user_model()
server_tz = timezone.get_current_timezone()


class CheckClosingDateMixin:
    def dispatch(self, request, *args, **kwargs):
        if server_tz.normalize(timezone.now()) >= get_local_closing_date():
            messages.info(
                request, "Sorry, abstract submissions have now been closed!")
            return redirect("account:profile")
        return super().dispatch(request, *args, **kwargs)


class UserKwargsMixin:
    """
    Pops 'user' from kwargs and sets it as instance variable 'user' if it
    exists.
    """
    user_kwarg = None
    
    def __init__(self, *args, **kwargs):
        if self.user_kwarg in kwargs:
            user = kwargs.pop(self.user_kwarg)
            if user is not None and not isinstance(user, User):
                raise TypeError("`user` must be an instance "
                                "of '{}'. Found '{}'.".format(
                    type(User).__name__, type(user).__name__,
                ))
            setattr(self, self.user_kwarg, user)
        else:
            setattr(self, self.user_kwarg, None)
        super().__init__(*args, **kwargs)
        
        
class SetUserOnSaveMixin:
    """
    A common pattern where a form will have a disabled foreign key
    field that must be set before saving.
    For example the owner of a scholarship in a `ModelForm`
    """
    user_field = None
    user_kwarg = None
    
    def save(self, commit=True):
        this_user = getattr(self, self.user_kwarg, None)
        setattr(self.instance, self.user_field, this_user)
        return super().save(commit=commit)


class ExtraKwargsMixin:
    """
    Pops any kwarg in `extra_kwargs` and sets them as instance variables. If not
    passed in via kwargs, they are set to `None`.
    """
    extra_kwargs = None
    
    def __init__(self, *args, **kwargs):
        for kwarg in self.extra_kwargs:
            if kwarg in kwargs:
                value = kwargs.pop(kwarg)
                setattr(self, kwarg, value)
            else:
                setattr(self, kwarg, None)
        super().__init__(*args, **kwargs)


class SetFieldsOnSaveMixin:
    """
    A common pattern where a form will have a disabled foreign key
    field that must be set before saving. Sets any fields in `extra_fields`
    by taking the value from `extra_kwargs`.
    
    Must be used with `ExtraKwargsMixin`.
    """
    extra_kwargs = None
    extra_fields = None
    
    def save(self, commit=True):
        for kwarg, field in zip(self.extra_kwargs, self.extra_fields):
            setattr(self.instance, field, getattr(self, kwarg, None))
        return super().save(commit=commit)
