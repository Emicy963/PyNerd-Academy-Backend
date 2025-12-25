from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Certificate


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "role", "is_approved", "is_staff")
    list_filter = ("role", "is_approved", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "role",
                    "plan",
                    "avatar",
                    "is_approved",
                    "study_streak",
                    "total_study_time",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "role")}),)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(Certificate)
