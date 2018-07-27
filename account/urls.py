from django.urls import path, include
from django.contrib.auth.views import logout

from . import views

app_name = 'account'

urlpatterns = [
    # ------ Login and Logout
    path('orcid/error/', views.orcid_login_error, name="orcid_login_error"),
    path('oauth/', include('social_django.urls', namespace='social'), name="social"),
    path('logout/', logout, name='logout'),
    path('login/orcid/', views.login_with_orcid, name='orcid_login'),
    path('login/staff/', views.staff_login, name='staff_login'),
    path('login/reset/', views.ResetPassword.as_view(), name="reset_password"),

    # ------ Profile
    path('profile/', views.ProfileView.as_view(), name="profile"),
    path('profile/settings/', views.EditProfileView.as_view(), name="edit_profile"),
    path('profile/scholarship/', views.submitter.ScholarshipApplicationView.as_view(), name="scholarship_application"),
    path('profile/assign/<slug:id>/', views.assigner.assign_reviewers_view, name="assign_reviewers"),

    path('profile/download/abstracts/', views.chair.DownloadAbstracts.as_view(), name="download_abstracts"),
    path('profile/download/scholarships/', views.chair.DownloadScholarshipApplications.as_view(), name="download_scholarships"),
    path('profile/scholarships/', views.chair.ScholarshipListView.as_view(), name="scholarships"),
]
