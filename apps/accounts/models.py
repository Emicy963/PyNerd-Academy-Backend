from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Model for Manager Custom User"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("STUDENT", "Student"),
        ("INSTRUCTOR", "Instructor"),
        ("ADMIN", "Admin"),
    )

    PLAN_CHOICES = (
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise')
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    avatar = models.URLField(blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    study_streak = models.PositiveIntegerField(default=0)
    total_study_time = models.PositiveIntegerField(default=0) # in seconds
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Preference in JSON
    preferences = models.JSONField(default=dict, blank=True)

    objects = CustomUserManager()

    # @property
    # def stats(self):
    #     """Calcula estatísticas do usuário"""
    #     return {
    #         'coursesCompleted': self.enrollments.filter(completed_at__isnull=False).count(),
    #         'lessonsCompleted': self.progress.filter(is_completed=True).count(),
    #         'averageScore': self.calculate_average_score(),
    #         # ... outros stats
    #     }

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def clean(self):
        if self.role == "INSTRUCTOR" and not self.is_approved:
            raise ValidationError("Instructors must be approved before activation.")

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"


class Certificate(models.Model):
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_urls = models.URLField()
    description = models.TextField()

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"Certificate for {self.student.email} - {self.course.title}"
