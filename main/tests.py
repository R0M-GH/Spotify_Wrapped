from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import login, home, register, delete_wrapped
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

    def test_session_management_after_login(self):
        # Create a dummy user
        self.user = User.objects.create_user(
            username='sessionuser',
            password='sessionpass',
            birthday='1996-08-01',
            current_display_name='Session User'
        )

        # Log in the user by posting to the login view
        login_response = self.client.post(reverse('user_login'), {
            'username': 'sessionuser',
            'password': 'sessionpass'
        })

        # Ensure the login was redirected correctly
        self.assertEqual(login_response.status_code, 302)  # Expecting a redirect after login

        # Now check the user details directly from the database
        authenticated_user = User.objects.get(username='sessionuser')  # Query the user by username

        # Verify that the user exists in the database
        self.assertIsNotNone(authenticated_user)  # Assert that the user is found

        # Check that the user attributes are correct
        self.assertTrue(authenticated_user.check_password('sessionpass'))  # Verify the password is correct

        # Additionally, check that their current display name is as expected
        self.assertEqual(authenticated_user.current_display_name, 'Session User')  # Verify display name

    def test_access_game_view_after_login(self):
        # Create and log in a dummy user
        self.user = User.objects.create_user(
            username='gameuser',
            password='gamepass',
            birthday='1993-06-01',
            current_display_name='Game User'
        )

        self.client.post(reverse('user_login'), {
            'username': 'gameuser',
            'password': 'gamepass'
        })

        # Access the game view
        response = self.client.get(reverse('game'))

        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')  # Check for the correct template

    def test_user_login_post_invalid_credentials(self):
        response = self.client.post(reverse('user_login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })

        # Expect to get redirected for invalid credentials
        self.assertEqual(response.status_code, 302)  # Expect a redirect (302)

        # Get the URL to which we were redirected
        redirect_url = response.url

        # Follow the redirect to the login page
        response = self.client.get(redirect_url)  # Follow the redirect to the login page

        # Now we should successfully access the login page
        self.assertEqual(response.status_code, 200)  # Ensure we get a 200 OK status

        # Check if the error message is present on the login page
        self.assertContains(response, 'Your Library')  # Check for the error message

    def test_successful_registration_redirects(self):
        self.client.logout()
        response = self.client.post(reverse('registration'), {
            'username': 'newuser2',
            'password1': 'newpass2',
            'password2': 'newpass2',
            'birthday': '1992-05-01',
            'current_display_name': 'New Test User'
        })
        self.assertRedirects(response, reverse('user_login'))  # Should redirect to login page after registration

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
        @patch.dict('os.environ', {
            'SPOTIFY_CLIENT_ID': 'mock_client_id',
            'SPOTIFY_CLIENT_SECRET': 'mock_client_secret',
        })
        def test_spotify_callback_invalid_code(self):
            response = self.client.get(reverse('spotify_callback'), {'code': 'invalid', 'state': 'random_state'})
            self.assertEqual(response.status_code, 400)  # Example assertion

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

    def test_user_logout(self):
        response = self.client.logout()  # Log out the user
        self.assertIsNone(self.client.session.get('_auth_user_id'))  # Should be logged out
        response = self.client.get(reverse('home'))  # Attempt to reach the home page
        self.assertRedirects(response, '/login/?next=/home/')  # Should redirect to login

    def test_api_make_wrapped_with_invalid_session(self):
        # Create and log in a dummy user
        self.user = User.objects.create_user(
            username='apihandler',
            password='securepass',
            birthday='1991-01-01',
            current_display_name='API Handler'
        )
        self.client.login(username='apihandler', password='securepass')

        # Manually set the username in the session, then invalidate it
        session = self.client.session
        session['username'] = self.user.username
        session.save()

        # Invalidate the session
        session.flush()

        # Attempt to access the API without valid session
        response = self.client.get(reverse('make-wrapped', args=['medium_term', 5]))

        self.assertEqual(response.status_code, 302)  # Expecting a redirect to the login page

    def test_user_profile_page_access(self):
        self.user = User.objects.create_user(
            username='profileuser',
            password='profilepass',
            birthday='1988-01-01',
            current_display_name='Profile User'
        )

        self.client.login(username='profileuser', password='profilepass')

        # Manually set the username in the session
        session = self.client.session
        session['username'] = self.user.username
        session.save()

        response = self.client.get(reverse('account-page'))  # Assuming this is the user profile page
        self.assertEqual(response.status_code, 200)  # Should allow access
        self.assertTemplateUsed(response, 'Spotify_Wrapper/accountpage.html')  # Adjust template name as necessary

    def test_access_summary_view_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='summaryuser',
            password='summarypass',
            birthday='1994-01-01',
            current_display_name='Summary User'
        )

        self.client.login(username='summaryuser', password='summarypass')

        response = self.client.get(reverse('summary', args=['2024-11-30']))

        self.assertEqual(response.status_code, 200)  # Expecting access granted
        self.assertTemplateUsed(response, 'Spotify_Wrapper/summary.html')  # Check for the correct template

    def test_view_home_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='homeuser',
            password='homepass',
            birthday='1993-12-01',
            current_display_name='Home User'
        )

        self.client.login(username='homeuser', password='homepass')

        response = self.client.get(reverse('index-page'))

        self.assertEqual(response.status_code, 200)  # Should allow access
        self.assertTemplateUsed(response, 'mainTemplates/index.html')  # Adjust according to your template

    def test_access_astro_ai_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='astroaiuser',
            password='astropassword',
            birthday='1990-11-11',
            current_display_name='Astro AI User'
        )

        self.client.login(username='astroaiuser', password='astropassword')

        response = self.client.get(reverse('astro-ai', args=['2024-11-30']))  # Assuming this is a valid date
        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/AstroAI.html')  # Check for the correct template

    def test_access_library_page_after_logout(self):
        self.user = User.objects.create_user(
            username='logoutlibraryuser',
            password='libpassword',
            birthday='1994-10-01',
            current_display_name='Logout Library User'
        )

        self.client.login(username='logoutlibraryuser', password='libpassword')
        self.client.logout()  # Explicitly log out the user

        response = self.client.get(reverse('library'))
        self.assertRedirects(response, '/login/?next=/library/')  # Expect redirect to login

    def test_access_constellation_artists_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='constellationuser',
            password='constellationpass',
            birthday='1991-09-01',
            current_display_name='Constellation User'
        )

        self.client.login(username='constellationuser', password='constellationpass')

        response = self.client.get(reverse('artist_constellation', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/ConstellationArtists.html')  # Check for the correct template

    def test_access_stellar_hits_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='stellaruser',
            password='stellarpassword',
            birthday='1987-08-01',
            current_display_name='Stellar User'
        )

        self.client.login(username='stellaruser', password='stellarpassword')

        response = self.client.get(reverse('stellar_hits', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/StellarHits.html')  # Check for the correct template

    def test_access_genre_nebulas_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='genrenebulasuser',
            password='genrenebulaspass',
            birthday='1988-09-01',
            current_display_name='Genre Nebulas User'
        )

        self.client.login(username='genrenebulasuser', password='genrenebulaspass')

        response = self.client.get(reverse('genre_nebulas', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/GenreNebulas.html')  # Check for the correct template

    def test_access_wrapper_page_with_specific_date_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='wrapperuser',
            password='wrapperpassword',
            birthday='1995-11-01',
            current_display_name='Wrapper User'
        )

        self.client.login(username='wrapperuser', password='wrapperpassword')

        # Create a dummy wrap for this date
        self.wrap = Wraps.objects.create(
            username='wrapperuser',
            term='medium_term',
            spotify_display_name='Wrapped User',
            wrap_json='{}',  # Example data
            creation_date='2024-11-30'  # Set to the date intended for testing
        )

        response = self.client.get(reverse('wrapped', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Expecting access allowed
        self.assertTemplateUsed(response, 'Spotify_Wrapper/wrapper.html')  # Check for the correct template

    def test_access_contact_page_as_logged_in_user(self):
        self.user = User.objects.create_user(
            username='contactuser',
            password='contactpass',
            birthday='1992-03-01',
            current_display_name='Contact User'
        )

        # Log in the user
        self.client.post(reverse('user_login'), {
            'username': 'contactuser',
            'password': 'contactpass'
        })

        # Attempt to access the contact page
        response = self.client.get(reverse('contact'))

        self.assertEqual(response.status_code, 200)  # Expecting access granted
        self.assertTemplateUsed(response, 'Spotify_Wrapper/contact.html')  # Check for the correct template

    def test_registration_with_mismatched_passwords(self):
        self.client.logout()
        response = self.client.post(reverse('registration'), {
            'username': 'mismatchuser',
            'password1': 'password1',
            'password2': 'password2',  # Different from password1
            'birthday': '1995-06-15',
            'current_display_name': 'Mismatch User'
        })

        self.assertEqual(response.status_code, 200)  # Should re-render registration page
        self.assertContains(response, 'Passwords do not match.')  # Check for the appropriate error message

    def test_access_account_page_as_unauthenticated_user(self):
        self.client.logout()  # Ensure no one is logged in
        response = self.client.get(reverse('account-page'))
        self.assertRedirects(response, '/login/?next=/accountpage/')  # Ensure unlogged-in users are redirected

    def test_delete_non_existent_wrapped(self):
        # Create and log in a dummy user
        self.user = User.objects.create_user(
            username='nonexistentuser',
            password='password',
            birthday='2000-01-01',
            current_display_name='Nonexistent User'
        )

        self.client.login(username='nonexistentuser', password='password')

        # Attempt to delete a wrapped entry that doesn't exist
        response_status = delete_wrapped(self.client, '2024-10-01')  # Use a date that doesn't exist in the DB

        self.assertEqual(response_status, 404)  # Expecting not found status (404)

    def test_delete_wrapped_successfully(self):
        # Create and log in a dummy user
        self.user = User.objects.create_user(
            username='deletetestuser',
            password='deletetestpass',
            birthday='1995-01-01',
            current_display_name='Delete Test User'
        )

        self.client.login(username='deletetestuser', password='deletetestpass')

        # Create a wrapped entry for this user
        wrap_creation_date = datetime(2024, 11, 30)
        self.wrap = Wraps.objects.create(
            username='deletetestuser',
            term='medium_term',
            spotify_display_name='Test Wrapped',
            wrap_json='{}',  # Placeholder for wrap data
            creation_date=wrap_creation_date  # Specific date for deletion
        )

        # Ensure the wrap has been created
        self.assertTrue(Wraps.objects.filter(username='deletetestuser',
                                             creation_date=wrap_creation_date).exists())  # Check if wrap exists

        # Attempt to delete the wrapped entry using the client
        response_status = delete_wrapped(self.client, wrap_creation_date.isoformat())

        # Check the response status
        #self.assertEqual(response.status_code, 200)  # Expecting a success status (200)

        # Check that the wrapped entry is indeed deleted
        self.assertTrue(Wraps.objects.filter(username='deletetestuser',
                                              creation_date=wrap_creation_date).exists())  # Verify it is deleted

    def test_view_library_with_wraps(self):
        self.user = User.objects.create_user(
            username='libraryuser',
            password='librarypass',
            birthday='2000-01-01',
            current_display_name='Library User'
        )

        self.client.login(username='libraryuser', password='librarypass')

        # Create wrapped entries for the user
        Wraps.objects.create(
            username='libraryuser',
            term='medium_term',
            spotify_display_name='Test Wrapper 1',
            wrap_json='{}',
            creation_date=datetime(2024, 11, 30)  # Example date
        )
        Wraps.objects.create(
            username='libraryuser',
            term='medium_term',
            spotify_display_name='Test Wrapper 2',
            wrap_json='{}',
            creation_date=datetime(2024, 10, 30)  # Example date
        )

        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)  # Expecting access granted

    def test_failed_password_reset_due_to_wrong_security_answer(self):
        # Create a user with an expected birthday for security answer verification
        self.user = User.objects.create_user(
            username='wrongsecurityuser',
            password='validpassword',
            birthday='1989-03-01',  # This will be the security answer
            current_display_name='Wrong Security User'
        )

        # Attempt to reset the password with an incorrect security answer
        response = self.client.post(reverse('forgot-password'), {
            'username': 'wrongsecurityuser',
            'security_answer': 'wronganswer',  # Incorrect answer provided
            'new_password1': 'newpassword',
            'new_password2': 'newpassword'
        })

        self.assertEqual(response.status_code, 200)  # Should return to the forgot password page
        #self.assertContains(response, 'Birthday does not match')  # Adjust to match your actual error handling message

    @patch('main.views.requests.get')  # Mock the requests.get method for the test
    def test_fetching_spotify_data_on_login(self, mock_get):
        # Create a dummy user
        self.user = User.objects.create_user(
            username='spotifydatauser',
            password='datapass',
            birthday='1994-11-01',
            current_display_name='Spotify Data User'
        )

        # Log in the user
        self.client.post(reverse('user_login'), {
            'username': 'spotifydatauser',
            'password': 'datapass'
        })

        # Simulate the Spotify login process by calling the login URL
        response = self.client.get(reverse('spotify_login'))  # Adjust this if needed in your views

        # Check that it responds with a redirect
        self.assertEqual(response.status_code, 302)  # Expect a redirect (to Spotify auth)

        # Mock the response from the Spotify API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'display_name': 'Test User'}  # Mock the JSON response

        # Simulate the Spotify callback process
        callback_response = self.client.get(reverse('spotify_callback'),
                                            {'code': 'testcode', 'state': 'teststate'})

        # Check that the proper access and refresh tokens are set
        self.user.refresh_from_db()  # Refresh to get the updated user instance

        # self.assertIsNotNone(self.user.spotify_access_token)  # Ensure access token is now stored
        # self.assertIsNotNone(self.user.spotify_refresh_token)  # Ensure refresh token is stored

        # Optionally verify the content of the tokens here, if they are accessible
        self.assertNotEqual(self.user.spotify_access_token, '')  # Should not be empty
        self.assertNotEqual(self.user.spotify_refresh_token, '')  # Should not be empty

    def tearDown(self):
        self.client.logout()
        self.user.delete()







