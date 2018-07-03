from django import template
from django import forms

register = template.Library()


@register.simple_tag
def add_css_class(field, css):
    return field.as_widget(attrs={'class': css})


@register.simple_tag
def is_checkbox(field):
    if isinstance(field.field, forms.BooleanField):
        return True
    return False
