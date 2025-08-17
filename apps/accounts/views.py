from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, UserProfile
from .serializers import UserDetailSerializer, UserSerializer
from .permissions import IsSelfOrAdmin


class RegisterView(generics.CreateAPIView):
    """API Views for Register New User"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get("role")
        is_approved = role != "INSTRUCTOR"  # Instructors need approval

        user = CustomUser.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            role=role,
            is_approved=is_approved,
        )

        # Create profile
        UserProfile.objects.create(user=user)

        return Response(UserSerializer(user).data, status=status.HHTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.is_superuser:
            return Response(
                {"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
