from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        # We need to ensure the correct name of the token url
        self.login_url = "/api/auth/login/"
        self.change_password_url = "/api/users/change_password/"

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strong_password_123",
            "first_name": "Test",
            "last_name": "User",
            "role": "STUDENT",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_student_user(self):
        data = {
            "username": "newstudent",
            "email": "student@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Doe",
            "role": "STUDENT",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)
        self.assertEqual(User.objects.count(), 2)

    def test_login_user_with_username(self):
        data = {
            "username": "testuser",
            "password": "strong_password_123",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_user_with_email(self):
        # Dual Auth Test
        data = {
            "username": "test@example.com",  # Send email in username field
            "password": "strong_password_123",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_invalid_credentials(self):
        data = {
            "username": "testuser",
            "password": "wrong_password",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_force_student_role(self):
        """Ensure registration always creates a STUDENT, ignoring input role"""
        data = {
            "username": "hacker_trying_admin",
            "email": "hacker@example.com",
            "password": "password123",
            "first_name": "Bad",
            "last_name": "Actor",
            "role": "INSTRUCTOR",  # Trying to be instructor
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="hacker@example.com")
        self.assertEqual(user.role, "STUDENT")
        self.assertFalse(user.is_active)

    def test_password_reset_flow(self):
        """Test the full password reset flow"""
        # 1. Request Reset
        reset_url = "/api/auth/password-reset/"
        response = self.client.post(reset_url, {"email": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Confirm Reset (Need to manually generate token/uid as we can't easily intercept email in this test seamlessly without mocking,
        # but we can simulate the token generation logic which is what the view does)
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        confirm_url = f"/api/auth/password-reset-confirm/{uid}/{token}/"
        new_pass_data = {"new_password": "new_secure_password"}
        response = self.client.post(confirm_url, new_pass_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verify Login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_secure_password"))

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "strong_password_123",
            "new_password": "new_strong_password_456",
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.client.logout()
        login_data = {"username": "testuser", "password": "new_strong_password_456"}
        new_login_resp = self.client.post(self.login_url, login_data)
        self.assertEqual(new_login_resp.status_code, status.HTTP_200_OK)

    def test_social_login_placeholder(self):
        """
        Test that the SocialLoginView (extending ConvertTokenView) returns 400 for invalid requests.
        Real integration tests for Social Auth would require mocking OAuth2 provider responses.
        """
        url = "/api/auth/social-login/"
        data = {"access_token": "fake_token", "provider": "google"}
        response = self.client.post(url, data)
        # ConvertTokenView returns 400 for invalid/incomplete OAuth requests
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_me_endpoint(self):
        """Test that authenticated users can access /users/me/ to get their profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertIn("profile", response.data)

    def test_user_me_endpoint_unauthenticated(self):
        """Test that unauthenticated users cannot access /users/me/"""
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
