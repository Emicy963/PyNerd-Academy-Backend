from rest_framework import pagination, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course
from .permissions import IsInstructor
from .serializers import CourseSerializer

class StandardResultSetPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 50

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultSetPagination

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        elif self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsInstructor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == "INSTRUCTOR":
            return Course.objects.filter(instructor=user)
        return Course.objects.filter(is_published=True)
