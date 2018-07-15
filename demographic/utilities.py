from abstract.models import Abstract

from .models import Gender, CareerStage, AboriginalOrTorres, State


def compute_statistics(abstracts=None):
    if abstracts is None:
        abstracts = Abstract.objects.all()
    data = {'gender': {}, 'stage': {}, 'aot': {}, 'state': {}}
    for gender in Gender.objects.all():
        count = abstracts.filter(
            submitter__profile__gender__text=gender.text).count()
        data['gender'][gender.text] = count

    for cs in CareerStage.objects.all():
        count = abstracts.filter(
            submitter__profile__career_stage__text=cs.text).count()
        data['stage'][cs.text] = count

    for aot in AboriginalOrTorres.objects.all():
        count = abstracts.filter(
            submitter__profile__aboriginal_or_torres__text=aot.text).count()
        data['aot'][aot.text] = count

    for state in State.objects.all():
        count = abstracts.filter(
            submitter__profile__state__text=state.text).count()
        data['state'][state.text] = count
    return data
