from django import test
from django.contrib.messages.storage.fallback import FallbackStorage

from account.models import UserGroups


class TestCase(test.TestCase):
    """Sets up the test environment by creating user groups."""
    def setUp(self):
        UserGroups.create_groups()
        

class TestMessageMixin:
    """
    Tests will fail on views that user messages. Use this mixin to prevent
    these tests failing. Assumes the caller has a `django.test.RequestFactory`
    attribute `self.factory`.
    """
    def create_request(self, method='get', **kwargs):
        request = getattr(self.factory, method)(**kwargs)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request