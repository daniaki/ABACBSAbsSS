from django.urls import path, include

from . import views

app_name = 'account'

urlpatterns = [
    # ------ Login and Logout
    path('orcid/error/', views.orcid_login_error, name="orcid_login_error"),
    path('oauth/', include('social_django.urls', namespace='social'), name="social"),
    path('logout/', views.logout, name='logout'),
    path('login/orcid/', views.login_with_orcid, name='orcid_login'),
    path('login/staff/', views.staff_login, name='staff_login'),
    path('login/reset/', views.reset_password, name="reset_password"),

    # ------ Profile
    path('profile/', views.ProfileView.as_view(), name="profile"),
    path('profile/settings/', views.submitter.EditProfileView.as_view(), name="edit_profile"),
    path('profile/scholarship/', views.submitter.ScholarshipApplicationView.as_view(), name="scholarship_application"),
]
