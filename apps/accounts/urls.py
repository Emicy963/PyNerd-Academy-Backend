from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, ActivateAccountView


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path(
        "auth/activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("", include(router.urls)),
]
