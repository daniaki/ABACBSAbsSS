"""
Custom pipeline step for loading extra data within the ORCID pipeline.
"""

import logging
from social_core.pipeline.social_auth import load_extra_data
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
logger = logging.getLogger("django")


from account.models import UserGroups


def orcid_load_extra_data(backend, details, response, uid, user, *args, **kwargs):
    load_extra_data(backend, details, response, uid, user, *args, **kwargs)
    social = (
        kwargs.get('social') or
        backend.strategy.storage.user.get_social_auth(backend.name, uid)
    )
    if social:
        if 'person' in response:
            person = response.get('person', {})
            if person:
                name = person.get('name', {})
            else:
                social.set_extra_data({'credit-name': ""})
                return

            if name:
                credit_name = name.get('credit-name', {})
            else:
                social.set_extra_data({'credit-name': ""})
                return

            if credit_name:
                credit_name_value = credit_name.get('value', "")
            else:
                social.set_extra_data({'credit-name': ""})
                return

            if credit_name_value:
                social.set_extra_data({'credit-name': credit_name_value})
            else:
                social.set_extra_data({'credit-name': ""})
                return
        else:
            social.set_extra_data({'credit-name': ""})
        return


def assign_group(backend, details, response, uid, user, *args, **kwargs):
    if user:
        submitters = Group.objects.get(name=UserGroups.SUBMITTER.value)
        submitters.user_set.add(user)
        return
    else:
        raise TypeError(
            "`assign_group` called with NoneType user argument. "
            "Called with backend={}, details={}, response={}, "
            "uid={}, user={}, *args={}, **kwargs={}".format(
                backend, details, response, uid, user,
                args, kwargs
            )
        )
    