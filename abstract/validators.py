import re
from functools import partial

from django.core.exceptions import ValidationError


# Unintended feature: this splits words at apostrophes and slashes inflating the word count.
# A quick fix below is to include small margins in the string length validation.
words_re = re.compile(r"\w+(?:-\w+)+|\w+|\d+")


def validate_n_word_or_less(value, n):
    n_words = len(words_re.findall(value))
    if n_words > n:
        raise ValidationError(
            "This field is limited to {} words or less.".format(n))


#validate_30_words_or_less = partial(validate_n_word_or_less, **{'n': 30})
#validate_100_words_or_less = partial(validate_n_word_or_less, **{'n': 100})
#validate_200_words_or_less = partial(validate_n_word_or_less, **{'n': 200})
#validate_250_words_or_less = partial(validate_n_word_or_less, **{'n': 250})

# Updated word length threshholds with margins
validate_30_words_or_less = partial(validate_n_word_or_less, **{'n': 35})
validate_100_words_or_less = partial(validate_n_word_or_less, **{'n': 130})
validate_200_words_or_less = partial(validate_n_word_or_less, **{'n': 220})
validate_250_words_or_less = partial(validate_n_word_or_less, **{'n': 300})
