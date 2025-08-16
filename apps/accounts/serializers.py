from rest_framework import serializers
from .models import CustomUser, UserProfile



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "first_name", "last_name", "role", "is_approved", "created_at"
        ]
        read_only_fields = [
            "id", "is_approved", "created_at"
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "bio", "avatar", "website", "location", "birth_date"
        ]
        read_only_fields = [
            "created_at", "updated_at"
        ]
