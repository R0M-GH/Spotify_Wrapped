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
from django.utils import timezone
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
        # Set up a client and create a test user with required fields
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            birthday='2000-01-01',
            current_display_name='Test User'
        )
        self.client.login(username='testuser', password='testpass')

    def test_library_redirect_unauthenticated(self):
        # Log out the user (if already logged in)
        self.client.logout()

        # Test that unauthenticated users are redirected to the login page
        response = self.client.get(reverse('library'))
        self.assertRedirects(response, '/login/?next=/library/')  # Adjust URL if needed

    def test_summary_view_logged_in(self):
        # Test that the summary view can be accessed when logged in with valid data
        response = self.client.get(reverse('summary', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Check standard functionality
        self.assertTemplateUsed(response, 'Spotify_Wrapper/summary.html')  # Check if the correct template is used

    def test_accountpage_redirect_unauthenticated(self):
        # Log out the user (if already logged in)
        self.client.logout()

        # Test that unauthenticated users are redirected to the login page
        response = self.client.get(reverse('account-page'))
        self.assertRedirects(response, '/login/?next=/accountpage/')  # Adjust the redirect URL if needed

    def test_accountpage_view_user_not_found(self):
        # Test account page when the user does not exist
        self.client.logout()
        new_client = Client()  # Create a new client
        new_client.login(username='nonexistentuser', password='fakepass')
        response = new_client.get(reverse('account-page'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_index_view(self):
        response = self.client.get(reverse('index-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_welcome_view(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/welcome.html')

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

    def test_register_view_post_success(self):
        # Test successful registration
        self.client.logout()
        response = self.client.post(reverse('registration'), {
            'username': 'newuser',
            'password1': 'newpass',
            'password2': 'newpass',
            'birthday': '1995-05-01'
        })
        self.assertEqual(response.status_code, 302)  # Expected redirect to login page
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login_get(self):
        # Test getting the user login page
        self.client.logout()
        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_relink_spotify_account_view(self):
        # Test the relink spotify account view
        response = self.client.get(reverse('spotify_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/relink_spotify_account.html')

    def test_spotify_login_view(self):
        # Test the Spotify login view
        response = self.client.get(reverse('spotify_login'))
        self.assertEqual(response.status_code, 302)  # Redirect to Spotify authorization URL
        self.assertTrue('https://accounts.spotify.com/authorize' in response.url)

    def test_game_view(self):
        # Test the game view
        response = self.client.get(reverse('game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')

    def test_spotify_callback_invalid_code(self):
        # Test Spotify callback with an invalid code
        response = self.client.get(reverse('spotify_callback'), {'code': 'invalid', 'state': 'random_state'})
        self.assertEqual(response.status_code, 400)  # Expect a bad request due to invalid code

    def test_genre_nebulas_view(self):
        # Test GenreNebulas view with a valid date string
        response = self.client.get(reverse('genre_nebulas', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/GenreNebulas.html')

    def test_stellar_hits_view(self):
        # Test StellarHits view with a valid date string
        response = self.client.get(reverse('stellar_hits', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/StellarHits.html')

    def test_constellation_artists_view(self):
        # Test ConstellationArtists view with a valid date string
        response = self.client.get(reverse('artist_constellation', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/ConstellationArtists.html')

    def test_astro_ai_view(self):
        # Test AstroAI view with a valid date string
        response = self.client.get(reverse('astro-ai', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/AstroAI.html')

    def test_newwrapper_view(self):
        # Test newwrapper view
        response = self.client.get(reverse('new_wrapped'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/newwrapper.html')

    def test_home_view_redirects_authenticated_users(self):
        # Check if an authenticated user can access the home view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_login_redirect_for_authenticated_user(self):
        # Test that an authenticated user is redirected if they try to access the login page
        response = self.client.get(reverse('user_login'))

        # Since we expect the user to be redirected to the library
        self.assertRedirects(response, reverse('library'))

    def test_api_make_wrapped_view_unauthenticated(self):
        # Test that an unauthorized user cannot access the make_wrapped API
        self.client.logout()
        response = self.client.get(reverse('make-wrapped', args=['medium_term', 5]))

        # Check that the response is a redirect (302)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to the login page

        # Ensure it redirects to the login page with the correct 'next' parameter
        expected_redirect = f"{reverse('user_login')}?next=/api/make-wrapped/medium_term/5/"
        self.assertRedirects(response, expected_redirect)  # Check for the correct redirect URL

    def test_forgot_password_with_matching_birthday(self):
        # Test successful password reset with a matching birthday
        self.user.birthday = '2000-01-01'  # Set the birthday for matching
        self.user.save()

        response = self.client.post(reverse('forgot-password'), {
            'username': self.user.username,  # Use the stored username
            'security_answer': '2000-01-01',  # Matching answer
            'new_password1': 'newpassword',
            'new_password2': 'newpassword'
        })

        self.assertRedirects(response, reverse('user_login'))  # Ensure redirect to login after password reset

        # Reload the user from the database to ensure we have the latest data
        self.user.refresh_from_db()  # Refresh the user instance to get updated data
        self.assertTrue(self.user.check_password('newpassword'))  # Check if the password was updated successfully

    def test_forgot_password_view_post_success(self):
        # Test successful password reset with valid data
        self.user.birthday = '2000-01-01'
        self.user.save()

        response = self.client.post(reverse('forgot-password'), {
            'username': self.user.username,
            'security_answer': '2000-01-01',
            'new_password1': 'newsecurepassword',
            'new_password2': 'newsecurepassword'
        })

        self.assertRedirects(response, reverse('user_login'))  # Ensure redirect after successful password reset
        self.user.refresh_from_db()  # Refresh user instance to verify password update
        self.assertTrue(self.user.check_password('newsecurepassword'))  # Verify the new password

    def test_forgot_password_view_get(self):
        # Test GET request for forgot password page
        response = self.client.get(reverse('forgot-password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/forget.html')  # Verify that the correct template is used

    def test_newwrapper_view_redirect_for_authenticated_user(self):
        # Test that an authenticated user can access the new wrapper view
        response = self.client.get(reverse('new_wrapped'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/newwrapper.html')

    def test_invalid_url(self):
        # Test request to an invalid URL
        response = self.client.get('/non-existent-url/')
        self.assertEqual(response.status_code, 404)  # Expect to hit a 404 error for invalid URL

    def test_library_view_content(self):
        # Test the library view content
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/library.html')
        self.assertContains(response, 'Create a New Wrapped')  # Adjust based on actual expected content

    def test_summary_view_when_logged_in(self):
        # Test summary view when user is logged in with a valid date
        response = self.client.get(reverse('summary', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Check if the response is valid
        self.assertTemplateUsed(response, 'Spotify_Wrapper/summary.html')  # Ensure the correct template is used
        self.assertContains(response, 'Your Listening Universe')  # Change according to the expected content

    def test_game_view_content(self):
        # Test the game view content
        response = self.client.get(reverse('game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')
        self.assertContains(response, 'Space Destroyers')  # Change this based on actual expected content


    def tearDown(self):
        self.client.logout()
        self.user.delete()






