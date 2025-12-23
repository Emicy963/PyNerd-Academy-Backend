from rest_framework import serializers
from .models import (
    Course,
    Enrollment,
    Lesson,
    Module,
    Progress,
    Quiz,
    Question,
    Option,
    Category,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "color"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "duration_seconds"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "order", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source="category", read_only=True)
    instructor_name = serializers.CharField(
        source="instructor.get_full_name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor_name",
            "category",
            "category_detail",
            "level",
            "price",
            "duration",
            "thumbnail",
            "slug",
            "is_published",
            "is_featured",
            "created_at",
            "modules",
            "students_count",
            "is_free",
            "rating",  # Added rating to response
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at", "completed_at"]


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(
        source="lesson.module.course.title", read_only=True
    )

    class Meta:
        model = Progress
        fields = [
            "id",
            "student",
            "lesson",
            "lesson_title",
            "course_title",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = ["student"]


class StudentProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()


class OptionSerializer(serializers.ModelSerializer):
    # FIX: Removed 'is_correct' to prevent leaking answers in the API response
    class Meta:
        model = Option
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question", "type", "points", "options"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "lesson", "time_limit", "passing_score", "questions"]
