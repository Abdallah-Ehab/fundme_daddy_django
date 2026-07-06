from django.test import TestCase
from django.urls import reverse

from .models import User, egypt_phone_validator


class EgyptianPhoneValidatorTest(TestCase):
    def test_valid_numbers(self):
        valid = ["01012345678", "01112345678", "01212345678", "01512345678"]
        for num in valid:
            with self.subTest(num=num):
                self.assertIsNone(egypt_phone_validator(num))

    def test_invalid_numbers(self):
        invalid = [
            "0101234567",      # too short
            "010123456789",    # too long
            "01412345678",     # invalid prefix (014)
            "01612345678",     # invalid prefix (016)
            "0101234567a",     # non-digit
            "10012345678",     # doesn't start with 0
        ]
        for num in invalid:
            with self.subTest(num=num):
                with self.assertRaises(Exception):
                    egypt_phone_validator(num)


class RegistrationLoginTest(TestCase):
    def test_registration_creates_user(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone_number": "01012345678",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertRedirects(response, reverse("accounts:registration_done"))
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_login_active_user_succeeds(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone_number="01012345678",
            password="StrongPass123!",
            is_active=True,
        )
        response = self.client.post(reverse("accounts:login"), {
            "username": "test@example.com",
            "password": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("projects:list"))

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone_number="01012345678",
            password="StrongPass123!",
        )
        data = {
            "first_name": "Another",
            "last_name": "User",
            "email": "test@example.com",
            "phone_number": "01112345678",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertContains(response, "already exists")
