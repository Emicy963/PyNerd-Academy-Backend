from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import StudentProgressView, CourseViewSet, ProgressViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"progress", ProgressViewSet, basename="progress")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "students/<int:id>/progress/",
        StudentProgressView.as_view(),
        name="student-progress",
    ),
]
