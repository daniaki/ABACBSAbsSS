from django import template

register = template.Library()


@register.simple_tag
def users_full_name(users):
    if not users:
        return users
    return [user.profile.full_name for user in list(users)]


@register.simple_tag
def has_category(category, abstract):
    return category in abstract.categories.all()