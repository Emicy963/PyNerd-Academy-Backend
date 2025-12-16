from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class CustomUserManagerTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="normal@user.com", password="foo", role="STUDENT")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)  # Assuming default is active or handled in manager
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo", role="STUDENT")


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = reverse("token_obtain_pair")
        
        # Create an active user for login tests
        self.user = User.objects.create_user(
            email="test@example.com", 
            password="testpassword123", 
            role="STUDENT",
            is_active=True
        )

    def test_register_student_user(self):
        data = {
            "email": "newstudent@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "Student",
            "role": "STUDENT"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2) 
        
        new_user = User.objects.get(email="newstudent@example.com")
        self.assertFalse(new_user.is_active) # Should be inactive until email verification

    def test_login_user(self):
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password(self):
        # First login to get token
        login_resp = self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "testpassword123"
        })
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Try to change password
        data = {
            "old_password": "testpassword123",
            "new_password": "newpassword456"
        }
        url = "/api/users/change_password/"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify old password no longer works
        logout_resp = self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "testpassword123"
        })
        self.assertEqual(logout_resp.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify new password works
        new_login_resp = self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "newpassword456"
        })
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

