from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    UserViewSet,
    ActivateAccountView,
    SocialLoginView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    social_auth_success,
    social_auth_error,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Auth URLs
    path("auth/register/", RegisterView.as_view(), name="register"),
    path(
        "auth/activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path(
        "auth/password-reset/",
        RequestPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "auth/password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Social Login (placeholder)
    path("auth/social-login/", SocialLoginView.as_view(), name="social_login"),
    # OAuth2 Success
    path("auth/success/", social_auth_success, name="social_auth_success"),
    path("auth/error/", social_auth_error, name="social_auth_error"),
    # User URLs
    path("", include(router.urls)),
]
