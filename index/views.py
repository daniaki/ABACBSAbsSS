from django.shortcuts import render
from django.http import JsonResponse

from demographic.models import Gender, CareerStage, AboriginalOrTorres, State
from abstract.models import Abstract


def index(request):
    if request.is_ajax():
        data = {'gender': {}, 'stage': {}, 'aot': {}, 'state': {}}
        abstracts = Abstract.objects.all()
        
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
            
        return JsonResponse(data=data)

    return render(request, "index/index.html", {})


def handler403(request, exception=None, template_name='core/403.html'):
    response = render(
        request, template_name, context={})
    response.status_code = 403
    return response


def handler404(request, exception=None, template_name='core/404.html'):
    response = render(
        request, template_name, context={})
    response.status_code = 404
    return response


def handler500(request, exception=None, template_name='core/500.html'):
    response = render(
        request, template_name, context={})
    response.status_code = 500
    return response