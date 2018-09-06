import re
from functools import partial

from django.core.exceptions import ValidationError


words_re = re.compile(r"\w+(?:-\w+)+|\w+|\d+")


def validate_n_word_or_less(value, n):
    n_words = len(words_re.findall(value))
    if n_words > n:
        raise ValidationError(
            "This field is limited to {} words or less.".format(n))


validate_30_words_or_less = partial(validate_n_word_or_less, **{'n': 30})
validate_100_words_or_less = partial(validate_n_word_or_less, **{'n': 100})
validate_200_words_or_less = partial(validate_n_word_or_less, **{'n': 200})
validate_250_words_or_less = partial(validate_n_word_or_less, **{'n': 250})