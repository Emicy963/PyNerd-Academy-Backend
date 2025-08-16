from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import CustomUser, UserProfile
from .serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    """API Views for Register New User"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get("role")
        is_approved = role != "INSTRUCTOR" # Instructors need approval

        user = CustomUser.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            role=role,
            is_approved=is_approved
        )

        # Create profile
        UserProfile.objects.create(user=user)

        return Response(UserSerializer(user).data, status=status.HHTP_201_CREATED)
