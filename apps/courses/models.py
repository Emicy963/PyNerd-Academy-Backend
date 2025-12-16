from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from polymorphic.models import PolymorphicModel


class Course(models.Model):
    """
    Model representing a course.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        "accounts.CustomUser",
        limit_choices_to={"role": "INSTRUCTOR"},
        on_delete=models.CASCADE,
        related_name="courses",
    )
    slug = models.SlugField(unique=True)
    thumbnail = models.URLField(blank=True)
    full_description = models.TextField(blank=True)
    level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
    )
    category = models.CharField(max_length=50, default="General")
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Campos calculados
    @property
    def rating(self):
        # Calcular rating médio das avaliações
        pass

    @property
    def students_count(self):
        return self.enrollments.count()

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.title)
    #     super().save(*args, **kwargs)

    def clean(self):
        """Ensure only instructors can create courses."""
        if self.instructor.role != "INSTRUCTOR":
            raise ValidationError("Only instructor can create courses.")

    def __str__(self):
        return self.title


class Module(models.Model):
    """
    Model representing a module within a course.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(PolymorphicModel):
    """
    Model representing a lesson within a module.
    """

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    video_url = models.URLField(validators=[URLValidator()])
    duration_seconds = models.PositiveIntegerField()

    ALLOWED_DOMAINS = ["youtube.com", "vimeo.com"]

    def clean(self):
        """Validate video URL domain."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(self.video_url)
            domain = parsed.netloc.lower()
            if domain not in self.ALLOWED_DOMAINS:
                raise ValidationError("Video URL must be from allowed domains.")
        except Exception:
            raise ValidationError("Invalid URL format.")

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """
    Model representing a student's enrollment in a course.
    """

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


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="quiz")
    time_limit = models.PositiveIntegerField(help_text="Time limit in seconds")
    passing_score = models.PositiveIntegerField(default=70)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=[
            ("multiple_choice", "Multiple Choice"),
            ("true_false", "True/False"),
            ("essay", "Essay"),
        ],
    )
    points = models.PositiveIntegerField(default=1)


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Note(models.Model):
    student = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="notes"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    timestamp = models.PositiveIntegerField(help_text="Position in video (seconds)")
    created_at = models.DateTimeField(auto_now_add=True)


class Resource(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="resources"
    )
    title = models.CharField(max_length=200)
    type = models.CharField(
        max_length=20, choices=[("pdf", "PDF"), ("zip", "ZIP"), ("link", "Link")]
    )
    file_url = models.URLField()
    size = models.PositiveIntegerField(help_text="File size in bytes")


class Bookmark(models.Model):
    student = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="bookmarks"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="bookmarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")
