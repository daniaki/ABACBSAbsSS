from account.models import UserGroups
from abstract.models import Assignment, PresentationCategory


def user_groups(request):
    """Adds the user group names into the request context."""
    context = dict()
    context['SUBMITTER_GROUP'] = UserGroups.SUBMITTER.value
    context['REVIEWER_GROUP'] = UserGroups.REVIEWER.value
    context['ASSIGNER_GROUP'] = UserGroups.ASSIGNER.value
    context['CHAIR_GROUP'] = UserGroups.CONFERENCE_CHAIR.value
    return context


def assignment_status(request):
    """Adds the user group names into the request context."""
    context = dict()
    context['PENDING'] = Assignment.STATUS_PENDING
    context['ACCEPTED'] = Assignment.STATUS_ACCEPTED
    context['DECLINED'] = Assignment.STATUS_REJECTED
    return context


def categories(request):
    """Returns a dict of presentation categories and their lowercase values"""
    return {
        'CATEGORIES': PresentationCategory.objects.all()
    }
