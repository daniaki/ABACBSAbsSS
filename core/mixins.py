from django.contrib.auth import get_user_model

User = get_user_model()


class UserKwargsForm:
    """
    Pops 'user' from kwargs and sets it as instance variable 'user' if it
    exists.
    """
    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
            if not isinstance(self.user, User):
                raise TypeError("`user` must be an instance "
                                "of '{}'. Found '{}'.".format(
                    type(User).__name__, type(self.user).__name__,
                ))
        else:
            self.user = None
        super().__init__(*args, **kwargs)