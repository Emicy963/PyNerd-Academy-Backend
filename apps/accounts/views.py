from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from drf_social_oauth2.views import ConvertTokenView
from .models import CustomUser, UserProfile
from .serializers import (
    UserDetailSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    RequestPasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsSelfOrAdmin


class RegisterView(generics.CreateAPIView):
    """API Views for Register New User"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Force role to STUDENT for public registration
        role = "STUDENT"
        is_approved = True

        user = CustomUser.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            role=role,
            is_approved=is_approved,
            is_active=False,
        )

        # Create profile
        UserProfile.objects.create(user=user)

        # Send Activation Email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://localhost:8000/api/auth/activate/{uid}/{token}/"
        subject = "Activate your PyNerd Account"
        message = f"Please click the link to activate: {activation_link}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
        except Exception as ex:
            user.delete()  # Rollback user creation on email failure
            return Response(
                {"detail": "Failed to send activation email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"detail": "User created. Please check email for activation."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    parameters=[
        OpenApiParameter("uidb64", OpenApiTypes.STR, location=OpenApiParameter.PATH),
        OpenApiParameter("token", OpenApiTypes.STR, location=OpenApiParameter.PATH),
    ],
    responses={200: None},
)
class ActivateAccountView(generics.GenericAPIView):
    """
    View to activate a user account via email link.
    """

    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request, uidb64, token):
        """
        Activate user account if token is valid.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"detail": "Account activated successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user instances.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == "create":
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request, pk=None):
        """
        Retrieve the profile of the current user.
        """
        user = self.get_object()
        if request.user != user and not request.user.is_superuser:
            return Response(
                {"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change the password for the current user.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response(
                {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Return the authenticated user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RequestPasswordResetView(generics.GenericAPIView):
    """
    View to request a password reset email.
    """

    serializer_class = RequestPasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = (
                f"http://localhost:8000/api/auth/password-reset-confirm/{uid}/{token}/"
            )

            send_mail(
                subject="Reset your PyNerd Password",
                message=f"Click the link to reset your password: {reset_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except CustomUser.DoesNotExist:
            # We do not want to reveal if a user exists or not
            pass

        return Response(
            {"detail": "Password reset email sent if account exists."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    View to confirm password reset with token.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"detail": "Password reset successfully."}, status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid token or link."}, status=status.HTTP_400_BAD_REQUEST
        )


class SocialLoginView(ConvertTokenView):
    """
    View to handle social login using drf-social-oauth2.
    """

    pass


@api_view(["GET"])
@permission_classes([AllowAny])
def social_auth_success(request):
    """
    View para redirecionamento após login social bem-sucedido.
    """
    return Response({"detail": "Authentication successful"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def social_auth_error(request):
    """
    View para redirecionamento após erro no login social.
    """
    return Response(
        {"detail": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST
    )
