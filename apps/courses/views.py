from django.db.models import Count
from rest_framework import pagination, viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Enrollment, Progress, Lesson
from .permissions import IsInstructor
from .serializers import CourseSerializer, EnrollmentSerializer, ProgressSerializer


class StandardResultSetPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 50


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing course instances.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["instructor", "is_published"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        elif self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsInstructor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts the returned courses to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        user = self.request.user
        queryset = Course.objects.select_related("instructor").prefetch_related(
            "modules__lessons"
        )
        if user.is_authenticated and user.role == "INSTRUCTOR":
            return queryset.filter(instructor=user)
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        """
        Associate the current user as instructor when creating a course.
        """
        serializer.save(instructor=self.request.user)

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if course.instructor != request.user:
            return Response(
                {"detail": "You can only edit your own courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    @extend_schema(request=None, responses={201: EnrollmentSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """
        Enroll the current user (if student) in the course.
        """
        course = self.get_object()
        if request.user.role != "STUDENT":
            return Response(
                {"detail": "Only students can enroll."},
                status=status.HTTP_403_FORBIDDEN,
            )
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course
        )
        if not created:
            return Response(
                {"detail": "Already enrolled."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED
        )


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and updating student progress.
    """

    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        if self.request.user.role == "STUDENT":
            return Progress.objects.filter(student=self.request.user)
        return Progress.objects.none()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        lesson = instance.lesson
        course = lesson.module.course
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "Not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


@extend_schema(responses={200: OpenApiTypes.OBJECT})
class StudentProgressView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None  # No serializer needed for this custom response

    def retrieve(self, request, *args, **kwargs):
        student_id = self.kwargs["id"]
        if request.user.id != int(student_id) and not request.user.is_superuser:
            return Response(
                {"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN
            )

        progress_data = (
            Progress.objects.filter(student_id=student_id, is_completed=True)
            .select_related("lesson__module__course")
            .values("lesson__module__course")
            .annotate(completed=Count("id"))
        )

        total_data = (
            Lesson.objects.filter(module__course__enrollments__student_id=student_id)
            .values("module__course")
            .annotate(total=Count("id"))
        )

        course_progress = {}
        for item in progress_data:
            course_id = item["lesson__module__course"]
            course_progress[course_id] = {"completed": item["completed"]}

        for item in total_data:
            course_id = item["module__course"]
            if course_id in course_progress:
                course_progress[course_id]["total"] = item["total"]
            else:
                course_progress[course_id] = {"completed": 0, "total": item["total"]}

        result = [
            {
                "course_id": course_id,
                "completed_lessons": data["completed"],
                "total_lessons": data["total"],
            }
            for course_id, data in course_progress.items()
        ]

        return Response(result)
