from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Certificate, CustomUser, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_approved",
            "created_at",
        ]
        read_only_fields = ["id", "is_approved", "created_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["bio", "avatar", "website", "location", "birth_date"]
        read_only_fields = ["created_at", "updated_at"]


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    instructor_name = serializers.CharField(
        source="course.instructor.get_full_name", read_only=True
    )

    class Meta:
        model = Certificate
        fields = [
            "id",
            "course",
            "course_title",
            "instructor_name",
            "issued_at",
            "certificate_url",
            "description",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    certificates = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_approved",
            "created_at",
            "profile",
            "certificates",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        profile = instance.profile

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    provider = serializers.ChoiceField(choices=[("google", "Google"), ("github", "GitHub")])

