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
    PasswordResetConfirmView
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
    path("auth/password-reset/", RequestPasswordResetView.as_view(), name="password_reset"),
    path("auth/password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("", include(router.urls)),
]
