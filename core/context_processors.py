from account.models import UserGroups

def user_groups(request):
    """Adds the user group names into the request context."""
    context = dict()
    context['SUBMITTER_GROUP'] = UserGroups.SUBMITTER.value
    context['REVIEWER_GROUP'] = UserGroups.REVIEWER.value
    context['ASSIGNER_GROUP'] = UserGroups.ASSIGNER.value
    context['CHAIR_GROUP'] = UserGroups.CONFERENCE_CHAIR.value
    return context