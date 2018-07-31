from django.urls import path

from . import views

app_name = 'index'

urlpatterns = [
    path('', views.index, name='index'),
    path('demographics/', views.plots, name='plots'),
]
