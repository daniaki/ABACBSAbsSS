from django.shortcuts import render


def index(request):
    return render(request, "index/index.html", {})


def handler403(request, exception=None, template_name='core/403.html'):
    print('here')
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