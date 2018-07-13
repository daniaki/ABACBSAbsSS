from django.urls import path, include

from . import views

app_name = 'abstract'

urlpatterns = [
    path('abstract/submit/', views.SubmissionView.as_view(), name='submit_abstract'),
    path('abstract/detail/<slug:id>/', views.AbstractDetailView.as_view(), name='abstract_summary'),
    path('abstract/edit/<slug:id>/', views.EditSubmissionView.as_view(), name='edit_abstract'),
    path('abstract/delete/<slug:id>/', views.DeleteSubmissionView.as_view(), name='delete_abstract'),
]
