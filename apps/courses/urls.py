from django.urls import path
from .views import StudentProgressView

urlpatterns = [
    path("students/<int:id>/progress/", StudentProgressView.as_view(), name="student-progress"),
]

