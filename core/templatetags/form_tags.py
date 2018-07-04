from django import template
from django import forms

register = template.Library()


@register.simple_tag
def add_css_class(field, css):
    if 'class' in field.field.widget.attrs:
        field.field.widget.attrs['class'] += ' ' + css
    else:
        field.field.widget.attrs['class'] = css
    return field.as_widget()


@register.simple_tag
def is_checkbox(field):
    if isinstance(field.field, forms.BooleanField):
        return True
    return False
