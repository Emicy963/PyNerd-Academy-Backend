from django.db import models
from django.core.exceptions import ValidationError


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        "accounts.CustomUser",
        limit_choices_to={"role": "INSTRUCTOR"},
        on_delete=models.CASCADE,
        related_name="courses"
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
