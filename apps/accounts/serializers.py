from rest_framework import serializers
from .models import CustomUser



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "first_name", "last_name", "role", "is_approved", "created_at"
        ]
        read_only_fields = [
            "id", "is_approved", "created_at"
        ]
