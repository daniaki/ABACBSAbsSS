from django import template

register = template.Library()


@register.simple_tag
def users_full_name(users):
    if not users:
        return users
    return [user.profile.full_name for user in list(users)]

