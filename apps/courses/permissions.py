from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    """
    Allows access only to instructors.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'INSTRUCTOR'

