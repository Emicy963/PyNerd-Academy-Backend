from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("STUDENT", "Student"),
        ("INSTRUCTOR", "Instructor"),
        ("ADMIN", "Admin"),
    )

    PLAN_CHOICES = (
        ("free", "Free"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="STUDENT")
    avatar = models.URLField(blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    study_streak = models.PositiveIntegerField(default=0)
    total_study_time = models.PositiveIntegerField(default=0)  # in seconds
    is_approved = models.BooleanField(default=False)

    # Using default is_active, is_staff, date_joined from AbstractUser

    # Preference in JSON
    preferences = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def clean(self):
        """Ensure instructors are approved before activation."""
        if self.role == "INSTRUCTOR" and not self.is_approved:
            raise ValidationError("Instructors must be approved before activation.")

    def __str__(self):
        """Return email as string representation."""
        return self.email


class UserProfile(models.Model):
    """
    Profile model for additional user information.
    """

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
    """
    Model representing a certificate issued to a student upon course completion.
    """

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
