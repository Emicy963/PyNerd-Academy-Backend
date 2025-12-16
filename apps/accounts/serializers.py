from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Certificate, CustomUser, UserProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):
        # Multi-Auth Logic: Check if "username" is an email
        login_input = attrs.get(self.username_field)
        if login_input and "@" in login_input:
            try:
                user = CustomUser.objects.get(email=login_input)
                # Swap email for the actual username expected by authenticate()
                attrs[self.username_field] = user.username
            except CustomUser.DoesNotExist:
                # If not found, let standard validation handle the failure
                pass

        data = super().validate(attrs)
        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                    "name": self.user.get_full_name(),
                    "email": self.user.email,
                    "avatar": self.user.avatar,
                    "plan": self.user.plan,
                    "studyStreak": self.user.study_streak,
                    "totalStudyTime": self.user.total_study_time,
                }
            }
        )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "is_approved",
            "date_joined",
        ]
        read_only_fields = ["id", "is_approved", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}


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
            "certificate_urls",
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
    provider = serializers.ChoiceField(
        choices=[("google", "Google"), ("github", "GitHub")]
    )
