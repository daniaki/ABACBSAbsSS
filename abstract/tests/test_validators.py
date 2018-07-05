from django.test import TestCase
from django.core.exceptions import ValidationError

from .. import validators


class TestValidators(TestCase):
    
    def test_word_len_validators(self):
        validators.validate_30_words_or_less(' '.join(['a'] * 30))
        with self.assertRaises(ValidationError):
            validators.validate_30_words_or_less(' '.join(['a'] * 31))

        validators.validate_100_words_or_less(' '.join(['a'] * 100))
        with self.assertRaises(ValidationError):
            validators.validate_100_words_or_less(' '.join(['a'] * 101))
        
        validators.validate_200_words_or_less(' '.join(['a'] * 200))
        with self.assertRaises(ValidationError):
            validators.validate_200_words_or_less(' '.join(['a'] * 201))
            
        validators.validate_250_words_or_less(' '.join(['a'] * 250))
        with self.assertRaises(ValidationError):
            validators.validate_250_words_or_less(' '.join(['a'] * 251))