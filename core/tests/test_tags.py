from django import forms
from django.test import TestCase

from ..templatetags import form_tags


class MockForm(forms.Form):
    test = forms.CharField(label='test', required=False)
    bool_field = forms.BooleanField(label='bool_field', required=False)


class TestFormTags(TestCase):
    
    def setUp(self):
        form = MockForm(data={'test': 'test-input'})
        self.field = form.visible_fields()[0]
        self.bool_field = form.visible_fields()[1]
    
    def test_adds_css_class(self):
        widget = form_tags.add_css_class(self.field, 'form-control')
        self.assertIn('class', widget)
        self.assertIn('form-control', widget)
        
    def test_is_checkbox(self):
        self.assertTrue(form_tags.is_checkbox(self.bool_field))
        self.assertFalse(form_tags.is_checkbox(self.field))
