from django.urls import path
from django.contrib.auth import views as auth_views
from .views import update_freelancer_profile
from .views import apply_to_job
from .views import  update_company_profile

from .views import (
    FreelancerSignupView,
    CompanySignupView,
    my_profile,
    job_list,
    create_job,
    my_jobs,
    update_or_delete_job,
    my_job_applications,
)

urlpatterns = [
    # Auth
    path('signup/freelancer/', FreelancerSignupView.as_view(), name='signup-freelancer'),
    path('signup/company/', CompanySignupView.as_view(), name='signup-company'),
    path('me/', my_profile, name='my-profile'),

    # Jobs
    path('jobs/', job_list, name='job-list'),
    path('jobs/create/', create_job, name='job-create'),

    # Passwort zurücksetzen mit HTML-Formularen (klassisch)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('me/update/', update_freelancer_profile, name='update-freelancer'),
    path('me/company/update/', update_company_profile, name='update-company'),

     path('apply/', apply_to_job, name='apply-to-job'),
     path('my-jobs/', my_jobs, name='my-jobs'),
     path('my-jobs/<int:job_id>/', update_or_delete_job, name='update-or-delete-job'),
     path('my-job-applications/', my_job_applications, name='my-job-applications'),



]

