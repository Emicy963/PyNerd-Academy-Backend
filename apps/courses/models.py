from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from polymorphic.models import PolymorphicModel


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        "accounts.CustomUser",
        limit_choices_to={"role": "INSTRUCTOR"},
        on_delete=models.CASCADE,
        related_name="courses",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.instructor.role != "INSTRUCTOR":
            raise ValidationError("Only instructor can create courses.")

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(PolymorphicModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    video_url = models.URLField(validators=[URLValidator()])
    duration_seconds = models.PositiveIntegerField()

    ALLOWED_DOMAINS = ["youtube.com", "vimeo.com"]

    def clean(self):
        domain = self.video_url.split("/")[2].lower()
        if domain not in self.ALLOWED_DOMAINS:
            raise ValidationError("Video URL must be from allowed domains.")

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        "accounts.CustomUser",
        limit_choices_to={"role": "STUDENT"},
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"


class Progress(models.Model):
    student = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="progress"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")

    def clean(self):
        if not Enrollment.objects.filter(
            student=self.student, course=self.lesson.module.course
        ).exists():
            raise ValidationError(
                "Student must be enrolled in the course to track progress."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.email} - {self.lesson.title}"
