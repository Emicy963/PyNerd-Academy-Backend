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
        # Helper to get course from various object types
        def get_course_from_obj(obj):
            if hasattr(obj, "course"):
                return obj.course
            if hasattr(obj, "module") and hasattr(obj.module, "course"):
                return obj.module.course
            # FIX: Handle Quiz/Question relationships
            if hasattr(obj, "quiz") and hasattr(obj.quiz, "lesson"):
                return obj.quiz.lesson.module.course
            if hasattr(obj, "lesson") and hasattr(obj.lesson, "module"):
                return obj.lesson.module.course
            return None

        course = get_course_from_obj(obj)

        if not course:
            return False

        return (
            request.user.role == "STUDENT"
            and Enrollment.objects.filter(student=request.user, course=course).exists()
        )
