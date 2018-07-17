import string
import random

from django.template.loader import render_to_string

ANONYMOUS_USER_NAME = "AnonymousUser"


def user_is_anonymous(user):
    return str(user) == ANONYMOUS_USER_NAME


def reset_password(profile):
    template_name = "account/password_reset.html"
    password = ''.join(
        [random.choice(string.ascii_letters) for _ in range(8)]
    )
    message = render_to_string(template_name, {
        'profile': profile,
        'password': password
    })
    profile.email_user(
        subject='ABACBS - password reset',
        message=message
    )
    user = profile.user
    user.set_password(raw_password=password)
    user.save()
