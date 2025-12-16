from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

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
        Test that the custom SocialLoginView returns 501 as currently implemented.
        Real integration tests for Social Auth would require mocking OAuth2 provider responses.
        """
        url = "/api/auth/social-login/"
        data = {"access_token": "fake_token", "provider": "google"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
