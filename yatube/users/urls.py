from django.contrib.auth import views as AuthView

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SingUp.as_view(), name='signup'),
    path(
        'logout/',
        AuthView.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        AuthView.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        AuthView.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        AuthView.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        AuthView.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        AuthView.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<slug:uidb64>/<slug:token>/',
        AuthView.PasswordResetConfirmView.as_view(
            success_url='password_reset_complete/',
            template_name='users/password_reset_confirm.html',
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        AuthView.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_compeite.html'
        ),
        name='password_reset_complete'
    ),
]
