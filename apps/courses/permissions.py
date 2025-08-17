from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsInstructor(BasePermission):
    """
    Allows access only to instructors.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "INSTRUCTOR"


class IsCourseStudent(BasePermission):
    """
    Allows access only to students enrolled in the course.
    """

    def has_object_permission(self, request, view, obj):
        # obj is expected to be a Lesson or reated to a Course
        course = getattr(obj, "course", None) or getattr(obj, "module", None).course
        return (
            request.user.role == "STUDENT"
            and Enrollment.objects.filter(student=request.user, course=course).exists()
        )
