from functools import partial

from django.core.exceptions import ValidationError


def validate_n_word_or_less(value, n):
    words = value.split(' ')
    if len(words) > n:
        raise ValidationError(
            "This field is limited to {} words or less.".format(n))
    

validate_100_word_or_less = partial(validate_n_word_or_less, **{'n': 100})
validate_200_word_or_less = partial(validate_n_word_or_less, **{'n': 200})
validate_250_word_or_less = partial(validate_n_word_or_less, **{'n': 250})
