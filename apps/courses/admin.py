from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)
from .models import (
    Course,
    Module,
    Lesson,
    Enrollment,
    Progress,
    Quiz,
    Question,
    Option,
    Note,
    Resource,
    Bookmark,
)


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "category",
        "price",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "category", "level", "created_at")
    search_fields = ("title", "description", "instructor__email")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    inlines = [LessonInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "duration_seconds")
    list_filter = ("module__course",)
    search_fields = ("title", "module__title")


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "completed_at")
    list_filter = ("enrolled_at", "completed_at")
    search_fields = ("student__email", "course__title")


class ProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "is_completed", "completed_at")
    list_filter = ("is_completed", "completed_at")


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ("question", "quiz", "type", "points")
    list_filter = ("type",)


class QuizAdmin(admin.ModelAdmin):
    list_display = ("lesson", "time_limit", "passing_score")


admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(Note)
admin.site.register(Resource)
admin.site.register(Bookmark)
