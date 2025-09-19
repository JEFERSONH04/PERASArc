from django.urls import path
from .views import RegisterView, RefreshView, PasswordResetConfirmView, PasswordResetRequestView, LoginWithSessionView, LogoutView

app_name = 'accounts' 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginWithSessionView.as_view(),    name='login'),
    path('logout/', LogoutView.as_view(),       name='logout'),
    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),
    path(
        'password-reset/',
        PasswordResetRequestView.as_view(),
        name='password_reset'
    ),
    path(
        'password-reset-confirm/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
]