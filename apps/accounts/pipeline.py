"""
Custom social auth pipeline for PyNerd.

This module contains custom pipeline steps for Python Social Auth
that generate JWT tokens after successful social authentication.
"""

from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


def create_user_profile(backend, user, response, *args, **kwargs):
    """
    Pipeline step that creates a UserProfile if it doesn't exist.
    """
    UserProfile.objects.get_or_create(user=user)


def generate_jwt_and_redirect(backend, user, response, *args, **kwargs):
    """
    Pipeline step that generates JWT tokens and redirects to frontend.

    This is the final step in the pipeline that:
    1. Generates access and refresh JWT tokens for the user
    2. Redirects to the frontend callback URL with tokens as query params
    """
    if user:
        refresh = RefreshToken.for_user(user)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        # Get frontend callback URL from settings or use default
        frontend_url = getattr(
            settings,
            "SOCIAL_AUTH_LOGIN_REDIRECT_URL",
            "http://localhost:5173/auth/callback",
        )

        redirect_url = f"{frontend_url}?{urlencode(tokens)}"
        return redirect(redirect_url)
