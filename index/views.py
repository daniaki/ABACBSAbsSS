from django.shortcuts import render
from django.http import JsonResponse

from abstract.models import Abstract
from demographic.utilities import compute_statistics


def index(request):
    if request.is_ajax():
        abstracts = Abstract.objects.all()
        data = compute_statistics(abstracts)
        return JsonResponse(data=data)
    return render(request, "index/index.html", {})


def plots(request):
    if request.is_ajax():
        abstracts = Abstract.objects.all()
        data = compute_statistics(abstracts)
        return JsonResponse(data=data)

    return render(request, "index/plots.html", {})


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
