from rest_framework import pagination, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course, Enrollment
from .permissions import IsInstructor
from .serializers import CourseSerializer, EnrollmentSerializer

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

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if course.instructor != request.user:
            return Response(
                {
                    "detail": "You can only edit your own courses."
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if request.user.role != "STUDENT":
            return Response(
                {
                    "detail": "Only students can enroll."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        if not created:
            return Response(
                {
                    "detail": "Already enrolled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
        
