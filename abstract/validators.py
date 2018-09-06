from functools import partial

from django.core.exceptions import ValidationError


def validate_n_word_or_less(value, n):
    words = [
        x.strip() for x in value.split(' ')
        if x.strip() not in ('', '\n', '\t', ' ')
    ]
    if len(words) > n:
        raise ValidationError(
            "This field is limited to {} words or less.".format(n))


validate_30_words_or_less = partial(validate_n_word_or_less, **{'n': 30})
validate_100_words_or_less = partial(validate_n_word_or_less, **{'n': 100})
validate_200_words_or_less = partial(validate_n_word_or_less, **{'n': 200})
validate_250_words_or_less = partial(validate_n_word_or_less, **{'n': 250})