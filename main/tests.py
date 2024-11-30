from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import login, home, register
from main.forms import RegistrationForm, LoginForm, ForgetForm
from unittest.mock import patch
from django.contrib.auth.hashers import make_password
from main.backends import AuthModelBackend

User = get_user_model()  # Get the custom user model

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="password123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.username, "testuser")

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(username="admin", password="password123")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_str_method(self):
        user = User(username="testuser")
        self.assertEqual(str(user), "testuser")  # Assuming __str__ is correct

    def test_unique_username(self):
        User.objects.create_user(username="uniqueuser", password="password123")
        with self.assertRaises(Exception):
            User.objects.create_user(username="uniqueuser", password="password456")

    def test_get_username(self):
        user = User(username="testuser")
        self.assertEqual(user.get_username(), "testuser")

    def test_default_values(self):
        """Test default values for new users."""
        user = User.objects.create_user(username="defaultuser", password="password123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertIsNone(user.spotify_access_token)
        self.assertIsNone(user.spotify_refresh_token)

    def test_spotify_tokens(self):
        """Test setting and retrieving Spotify tokens."""
        user = User.objects.create_user(
            username="spotifyuser",
            password="password123",
            spotify_access_token="access_token_123",
            spotify_refresh_token="refresh_token_123"
        )
        self.assertEqual(user.spotify_access_token, "access_token_123")
        self.assertEqual(user.spotify_refresh_token, "refresh_token_123")

    def test_create_user_without_username(self):
        """Test creating a user without a username raises ValueError."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(username=None, password="password123")
        self.assertEqual(str(context.exception), "You have not provided a valid username.")

    def test_create_superuser_with_missing_fields(self):
        """Test that creating a superuser with missing is_staff or is_superuser fields works correctly."""
        admin_user = User.objects.create_superuser(username="adminuser", password="password123")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_date_joined_default(self):
        """Test that date_joined is set to the current time by default."""
        user = User.objects.create_user(username="dateuser", password="password123")
        self.assertIsNotNone(user.date_joined)

    def test_user_permissions(self):
        """Test that PermissionsMixin methods and attributes are functional."""
        user = User.objects.create_user(username="permissionuser", password="password123")
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_invalid_username(self):
        """Test creating a user with an invalid username."""
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="password123")

class RegistrationFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'birthday': '1990-01-01'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'password1': 'securepassword',
            'password2': 'wrongpassword',
            'birthday': '1990-01-01'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Passwords do not match.'])

    def test_missing_birthday(self):
        form_data = {
            'username': 'testuser',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'birthday': ''
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birthday', form.errors)

    def test_empty_form(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
        self.assertIn('birthday', form.errors)


class LoginFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_username(self):
        form_data = {
            'username': '',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        form_data = {
            'username': 'testuser',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_empty_form(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class ForgetFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'security_answer': '1990-01-01',
            'new_password1': 'securepassword',
            'new_password2': 'securepassword'
        }
        form = ForgetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_security_answer(self):
        form_data = {
            'username': 'testuser',
            'security_answer': '',
            'new_password1': 'securepassword',
            'new_password2': 'securepassword'
        }
        form = ForgetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('security_answer', form.errors)

    def test_missing_password(self):
        form_data = {
            'username': 'testuser',
            'security_answer': '1990-01-01',
            'new_password1': '',
            'new_password2': ''
        }
        form = ForgetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertIn('new_password2', form.errors)

    def test_empty_form(self):
        form = ForgetForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('security_answer', form.errors)
        self.assertIn('new_password1', form.errors)
        self.assertIn('new_password2', form.errors)

class AuthModelBackendTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='testuser',
            password='securepassword'
        )
        self.backend = AuthModelBackend()

    def test_authenticate_with_correct_credentials(self):
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='securepassword'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_incorrect_username(self):
        user = self.backend.authenticate(
            request=None,
            username='wronguser',
            password='securepassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_incorrect_password(self):
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='wrongpassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_user(self):
        user = self.backend.authenticate(
            request=None,
            username='nonexistentuser',
            password='securepassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_no_username(self):
        user = self.backend.authenticate(
            request=None,
            password='securepassword'
        )
        self.assertIsNone(user)

    @patch('main.backends.AuthModelBackend.user_can_authenticate', return_value=False)  # Mock user_can_authenticate
    def test_authenticate_with_unauthenticatable_user(self, mock_user_can_authenticate):
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='securepassword'
        )
        self.assertIsNone(user)
        mock_user_can_authenticate.assert_called_once_with(self.user)

class LoginFormTest(TestCase):

    def test_valid_login_form(self):
        form_data = {
            'username': 'testuser',
            'password': 'password123',
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')

    def test_missing_username(self):
        form_data = {
            'username': '',
            'password': 'password123',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        form_data = {
            'username': 'testuser',
            'password': '',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)














