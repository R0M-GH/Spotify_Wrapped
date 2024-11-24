from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import login, home, register
from main.forms import RegistrationForm, LoginForm
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


class UrlTests(SimpleTestCase):

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login)

    def test_home_url_resolves(self):
        url = reverse('home-page')
        self.assertEqual(resolve(url).func, home)

    def test_registration_url_resolves(self):
        url = reverse('registration')
        self.assertEqual(resolve(url).func, register)


class RegistrationFormTest(TestCase):

    def test_valid_registration_form(self):
        form_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123',
            'securityAnswer': '01/01/2000'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')

    def test_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'differentpassword',
            'securityAnswer': '01/01/2000'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Check for the presence of non-field-specific error
        self.assertEqual(form.errors['__all__'], ['Passwords do not match.'])  # Check the specific error message

    def test_missing_username(self):
        form_data = {
            'username': '',
            'password1': 'password123',
            'password2': 'password123',
            'securityAnswer': '01/01/2000'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)  # Check for the specific field error

    def test_invalid_security_answer_format(self):
        form_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123',
            'securityAnswer': 'InvalidFormat'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())  # Assuming there's no specific validation
        self.assertEqual(form.cleaned_data['securityAnswer'], 'InvalidFormat')


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

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')  # Use User here

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_home_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_home_view_unauthenticated(self):
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 302)  # Expect redirect to login

    def test_registration_view(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration.html')

    # def test_registration_post(self):
    #     response = self.client.post(reverse('registration'), {
    #         'username': 'newuser',
    #         'password1': 'password123',
    #         'password2': 'password123'
    #     })
    #
    #     self.assertRedirects(response, reverse('login'))  # Expect redirect to login
    #     self.assertTrue(User.objects.filter(username='newuser').exists())  # Ensure the user is created

    @patch('os.getenv')  # Patch os.getenv before calling the view
    def test_spotify_callback_no_code(self, mock_getenv):
        # Mock the environment variables for the test
        mock_getenv.side_effect = lambda key: {
            'SPOTIFY_CLIENT_ID': 'mock_client_id',
            'SPOTIFY_CLIENT_SECRET': 'mock_client_secret',
        }.get(key)

        response = self.client.get(reverse('spotify_callback'))

        # Since you are testing for a case with no code, expecting 400
        self.assertEqual(response.status_code, 400)  # Expect bad request due to missing code

    # def test_spotify_data_authenticated(self):
    #     self.client.login(username='testuser', password='12345')
    #     response = self.client.get(reverse('spotify_data', kwargs={'time_range': 'medium_term'}))
    #     self.assertEqual(response.status_code, 200)  # Adjust according to actual behavior

    # @patch('requests.get')
    # def test_spotify_data_api_call(self, mock_get):
    #     mock_response = {
    #         "top_tracks": {"items": []},
    #         "top_artists": {"items": []},
    #     }
    #     mock_get.return_value.status_code = 200
    #     mock_get.return_value.json.return_value = mock_response
    #
    #     self.client.login(username='testuser', password='12345')
    #     response = self.client.get(reverse('spotify_data', kwargs={'time_range': 'medium_term'}))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertJSONEqual(response.content, mock_response)

class AuthModelBackendTests(TestCase):
    def setUp(self):
        self.backend = AuthModelBackend()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create(
            username="testuser",
            password=make_password("securepassword"),  # Ensure password is hashed
            is_active=True
        )

    def test_authenticate_valid_user(self):
        """Test authentication with a valid username and password."""
        user = self.backend.authenticate(username="testuser", password="securepassword")
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_invalid_password(self):
        """Test authentication with an invalid password."""
        user = self.backend.authenticate(username="testuser", password="wrongpassword")
        self.assertIsNone(user)

    def test_authenticate_invalid_username(self):
        """Test authentication with a username that does not exist."""
        user = self.backend.authenticate(username="nonexistent", password="securepassword")
        self.assertIsNone(user)

    def test_authenticate_inactive_user(self):
        """Test authentication with an inactive user."""
        self.user.is_active = False
        self.user.save()
        user = self.backend.authenticate(username="testuser", password="securepassword")
        self.assertIsNone(user)

    def test_authenticate_with_no_username(self):
        """Test authentication when no username is provided."""
        user = self.backend.authenticate(password="securepassword")
        self.assertIsNone(user)

    def test_authenticate_with_kwargs_username_field(self):
        """Test authentication using the username field from kwargs."""
        user = self.backend.authenticate(password="securepassword", username="testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

