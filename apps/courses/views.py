from django.db.models import Count, Q
from rest_framework import pagination, viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Enrollment, Progress, Lesson, Quiz, Category
from apps.accounts.models import Certificate
from .permissions import IsInstructor
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    ProgressSerializer,
    QuizSerializer,
    CategorySerializer,
)


class StandardResultSetPagination(pagination.LimitOffsetPagination):
    default_limit = 20
    max_limit = 50


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing course instances.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "instructor",
        "is_published",
        "category",
        "level",
        "is_featured",
    ]
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

        # FIX: Allow Instructors to see all published courses OR their own courses
        if user.is_authenticated and user.role == "INSTRUCTOR":
            # Show my courses (draft or published) + All published courses from others
            return queryset.filter(Q(instructor=user) | Q(is_published=True)).distinct()

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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        """
        List courses the current user is enrolled in.
        """
        if request.user.role != "STUDENT":
            return Response(
                {"detail": "Only students can have enrollments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        enrolled_courses = Course.objects.filter(enrollments__student=request.user)
        page = self.paginate_queryset(enrolled_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(enrolled_courses, many=True)
        return Response(serializer.data)


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
        response = super().update(request, *args, **kwargs)

        # Certificate Generation Logic
        # Note: Timestamp handling is now inside models.Progress.save()
        if request.data.get("is_completed") is True:
            # Refresh to ensure we have the latest state
            instance.refresh_from_db()
            if instance.is_completed:
                # Count total lessons
                total_lessons = Lesson.objects.filter(module__course=course).count()

                # Count completed lessons
                completed_lessons = Progress.objects.filter(
                    student=request.user,
                    lesson__module__course=course,
                    is_completed=True,
                ).count()

                if total_lessons > 0 and total_lessons == completed_lessons:
                    # Create Certificate if not exists
                    Certificate.objects.get_or_create(
                        student=request.user,
                        course=course,
                        defaults={"description": f"Certificate for {course.title}"},
                    )

        return response


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


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for quizzes.
    """

    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter quizzes by lesson_id if provided.
        """
        lesson_id = self.request.query_params.get("lesson_id")
        if lesson_id:
            return self.queryset.filter(lesson_id=lesson_id)
        return self.queryset
