from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Certificate

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "role", "is_approved", "is_staff")
    list_filter = ("role", "is_approved", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "avatar", "profile")}),
        ("Permissions", {"fields": ("role", "is_approved", "is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    readonly_fields = ("created_at",)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "birth_date")
    search_fields = ("user__email", "location")

class CertificateAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "issued_at")
    list_filter = ("issued_at", "course")
    search_fields = ("student__email", "course__title")

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Certificate, CertificateAdmin)
