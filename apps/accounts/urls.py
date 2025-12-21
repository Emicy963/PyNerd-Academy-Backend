from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    UserViewSet,
    ActivateAccountView,
    SocialLoginView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    github_callback,
    google_callback,
)


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path(
        "auth/activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("auth/social-login/", SocialLoginView.as_view(), name="social_login"),
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

    # OAuth Callbacks
    
    path("auth/github/callback/", github_callback, name="github_callback"),
    path("auth/google/callback/", google_callback, name="google_callback"),

    path("", include(router.urls)),
]
