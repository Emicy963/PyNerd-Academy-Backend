from rest_framework import serializers
from .models import Course, Lesson, Module



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
    instructor_name = serializers.CharField(source="instructor.get_full_name", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "student", "course", "enrolled_at", "completed_at"]
