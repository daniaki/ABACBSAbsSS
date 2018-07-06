from django.contrib.auth import get_user_model

User = get_user_model()


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
