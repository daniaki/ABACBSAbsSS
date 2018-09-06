from django.test import TestCase
from django.core.exceptions import ValidationError

from .. import validators


class TestValidators(TestCase):
    
    def test_removes_empty(self):
        validators.validate_n_word_or_less('    '.join(['a'] * 10), 10)
        
    def test_ignores_punctuation(self):
        s = """
        This is the story of the
        
        
        
        ~~~~~!#!#@ Hurricane &*(~~~~~~
        
        
        
        (Drum beats)
        """
        validators.validate_n_word_or_less(s, 9)
        with self.assertRaises(ValidationError):
            validators.validate_n_word_or_less(s, 8)
        
    def test_hyphenated_counts_as_one(self):
        with self.assertRaises(ValidationError):
            validators.validate_n_word_or_less('hello hello-world', 1)
        
    def test_numbers_count_as_word(self):
        with self.assertRaises(ValidationError):
            validators.validate_n_word_or_less('999 999', 1)
            
    def test_mixed_counts_as_word(self):
        with self.assertRaises(ValidationError):
            validators.validate_n_word_or_less('999hello 999', 1)
    
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