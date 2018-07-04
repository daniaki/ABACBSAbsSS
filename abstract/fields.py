from django.core.exceptions import ValidationError
from django.forms import ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _


class FlexibleModelMultipleChoiceField(ModelMultipleChoiceField):
    """
    Custom Field to handle Keyword creation.
    """
    default_error_messages = {
        'list': _('Enter a list of values.'),
        'invalid_choice': _(
            'Select a valid choice. "%(value)s" is not one of the'
            ' available choices.'
        ),
        'invalid_pk_value': _(
            '"%(pk)s" is not a valid option value.'
        )
    }

    def __init__(self, klass, queryset, **kwargs):
        super().__init__(queryset, **kwargs)
        self.klass = klass
        self.queryset = queryset

    def to_python(self, value):
        values = []
        if not value:
            return values
        if not isinstance(value, (set, list, tuple)):
            value = [value]
        for v in value:
            if not v.strip():
                continue
            try:
                values.append(
                    self.klass.objects.get(**{self.to_field_name: v}))
            except self.queryset.model.DoesNotExist:
                values.append(self.klass(**{self.to_field_name: v}))
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice'
                    )
        return values

    def clean(self, value):
        value = self.prepare_value(value)
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'], code='required')
        elif not self.required and not value:
            return self.queryset.none()
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'], code='list')
        qs = self.to_python(value)
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return qs