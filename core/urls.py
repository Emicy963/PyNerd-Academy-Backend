from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshSlidingView
from apps.accounts.serializers import CustomTokenObtainPairSerializer
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Social Auth
    path("api/auth/", include("drf_social_oauth2.urls", namespace="drf")),
    # Apps
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.courses.urls")),
    # JWT
    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
        name="token_obtain_pair",
    ),
    path("api/auth/refresh/", TokenRefreshSlidingView.as_view(), name="token_refresh"),
    # Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
