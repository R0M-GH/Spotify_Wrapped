from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import login, home, register
from main.forms import RegistrationForm, LoginForm, ForgetForm
from unittest.mock import patch
from django.contrib.auth.hashers import make_password
from main.backends import AuthModelBackend
from main.models import User, Wraps
from datetime import datetime
from django.core.exceptions import ValidationError

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


class CustomUserManagerTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('securepassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(username='adminuser', password='adminpassword')
        self.assertEqual(user.username, 'adminuser')
        self.assertTrue(user.check_password('adminpassword'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='securepassword')

    def test_create_superuser_without_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='', password='adminpassword')


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('securepassword'))

    def test_user_get_username(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.get_username(), 'testuser')

    def test_user_delete_with_wraps(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})

        # Ensure Wraps record is created
        self.assertEqual(Wraps.objects.count(), 1)

        user.delete_with_wraps()

        # Ensure Wraps record is deleted after user deletion
        self.assertEqual(Wraps.objects.count(), 0)

    def test_user_birthday_default(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertIsInstance(user.birthday, datetime)

    def test_user_is_active_default(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertTrue(user.is_active)


class WrapsModelTest(TestCase):
    def test_wrap_creation(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})
        self.assertEqual(wrap.username, 'testuser')
        self.assertEqual(wrap.term, '2024')
        self.assertEqual(wrap.spotify_display_name, 'Test Display')
        self.assertIsInstance(wrap.creation_date, datetime)
        self.assertEqual(Wraps.objects.count(), 1)

    def test_wrap_str_method(self):
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})
        self.assertEqual(str(wrap), 'testuser' + str(wrap.creation_date))

    def test_wrap_missing_username(self):
        with self.assertRaises(ValidationError):
            wrap = Wraps(username=None, spotify_display_name='Test Display', wrap_json={})
            wrap.full_clean()  # Will raise ValidationError if username is None


class UserManagerTests(TestCase):
    def test_user_creation_manager(self):
        user = User.objects.create_user('user1', 'password1')
        self.assertEqual(user.username, 'user1')
        self.assertTrue(user.check_password('password1'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_creation_manager(self):
        user = User.objects.create_superuser('admin1', 'adminpassword')
        self.assertEqual(user.username, 'admin1')
        self.assertTrue(user.check_password('adminpassword'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

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


class ViewsTestCase(TestCase):
    def setUp(self):
        # Set up a client to make requests to the application
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', birthday='2000-01-01')
        self.client.login(username='testuser', password='testpass')

    def test_index_view(self):
        response = self.client.get(reverse('index-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_welcome_view(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/welcome.html')

    # def test_accountpage_view(self):
    #     Wraps.objects.create(username=self.user.username, creation_date='2024-11-30')
    #     response = self.client.get(reverse('account-page'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'Spotify_Wrapper/accountpage.html')
    #     self.assertContains(response, self.user.username)

    def test_contact_view(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/contact.html')

    def test_library_view(self):
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/library.html')

    def test_register_view_get(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration.html')

    # def test_register_view_post_existing_user(self):
    #     self.client.logout()
    #     response = self.client.post(reverse('registration'), {
    #         'username': 'testuser',
    #         'password1': 'testpass',
    #         'password2': 'testpass',
    #         'birthday': '2000-01-01'
    #     })
    #     self.assertFormError(response, 'form', 'username', 'An account with this username already exists.')

    # def test_user_login_success(self):
    #     response = self.client.post(reverse('user_login'), {
    #         'username': 'testuser',
    #         'password': 'testpass'
    #     })
    #     self.assertRedirects(response, reverse('library'))

    def test_user_login_invalid(self):
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')  # This assumes the template shows an error when login fails

    def test_forgot_password_view_post_invalid(self):
        response = self.client.post(reverse('forgot-password'), {
            'username': 'nonexistentuser',
            'security_answer': '2000-01-01',
            'new_password1': 'newpass',
            'new_password2': 'newpass'
        })
        self.assertContains(response, 'error')

    # def test_delete_account_view(self):
    #     response = self.client.get(reverse('delete_account'))
    #     self.assertRedirects(response, reverse('user_login'))
    #     self.assertFalse(User.objects.filter(username='testuser').exists())

    def tearDown(self):
        self.client.logout()
        self.user.delete()  # Clean up the test user













