from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshSlidingView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.courses.urls")),
    path("api/auth/login/", TokenBlacklistView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshSlidingView.as_view(), name="token_refresh"),
]
