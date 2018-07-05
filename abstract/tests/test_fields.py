from django.test import TestCase

from ..factories import KeywordFactory
from ..fields import FlexibleModelMultipleChoiceField
from ..models import Keyword


class TestFlexibleModelMultipleChoiceField(TestCase):
    """
    Tests the :class:`FlexibleModelMultipleChoiceField` which handles being able
    to select existing M2M relationships or create new ones, for example
    if a user wishes to create a new keyword not in the database.
    """
    def tearDown(self):
        Keyword.objects.all().delete()

    def test_check_values_filters_out_null_values(self):
        field = FlexibleModelMultipleChoiceField(
            klass=Keyword, to_field_name='text', required=False,
            queryset=Keyword.objects.none()
        )
        existing = field.clean([' ', ''])
        self.assertEqual(len(existing), 0)

    def test_new_values_detected(self):
        field = FlexibleModelMultipleChoiceField(
            klass=Keyword, to_field_name='text',
            queryset=Keyword.objects.none()
        )
        values = ['hello', 'world']
        qs = field.clean(values)
        self.assertEqual(len(qs), 2)
        self.assertIsNone(qs[0].pk)
        self.assertIsNone(qs[1].pk)

    def test_new_value_not_created_if_exists(self):
        field = FlexibleModelMultipleChoiceField(
            klass=Keyword, to_field_name='text',
            queryset=Keyword.objects.none()
        )
        kw = KeywordFactory()
        qs = field.clean([kw.text])
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], kw)