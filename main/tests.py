from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
from .models import User, CustomUserManager  # Replace with actual models
import os

class IndexViewTests(TestCase):
    def test_index_view_access(self):
        response = self.client.get(reverse('main:index-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

class HomeViewTests(TestCase):
    def test_home_view_access(self):
        response = self.client.get(reverse('main:home-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_home_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('main:home-page'))
        self.assertRedirects(response, reverse('main:login') + '?next=' + reverse('main:home-page'))

class OtherPagesTests(TestCase):
    def test_game_view_renders_template(self):
        response = self.client.get(reverse('main:game_page'))
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')

    def test_library_view_renders_template(self):
        response = self.client.get(reverse('main:library_page'))
        self.assertTemplateUsed(response, 'Spotify_Wrapper/library.html')

    def test_info_page_get_renders_template(self):
        response = self.client.get(reverse('main:info_page'))
        self.assertTemplateUsed(response, 'Spotify_Wrapper/info.html')

    def test_info_page_post_redirects(self):
        response = self.client.post(reverse('main:info_page'))
        self.assertRedirects(response, reverse('main:wrapper_page'))

class RegistrationViewTests(TestCase):
    def test_valid_form_creates_user_and_redirects(self):
        response = self.client.post(reverse('main:registration'), {
            'username': 'testuser', 'password1': 'password123', 'password2': 'password123'
        })
        self.assertRedirects(response, reverse('main:login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_duplicate_user_returns_error(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('main:registration'), {
            'username': 'testuser', 'password1': 'password123', 'password2': 'password123'
        })
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_invalid_form_does_not_create_user(self):
        response = self.client.post(reverse('main:registration'), {
            'username': 'testuser', 'password1': 'password123', 'password2': 'wrongpassword'
        })
        self.assertFalse(User.objects.filter(username='testuser').exists())

class LoginViewTests(TestCase):
    def test_valid_login_redirects_to_home(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('main:home-page'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('main:login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_session_cleared_on_logout(self):
        self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'password123'})
        self.client.logout()
        self.assertIsNone(self.client.session.get('_auth_user_id'))

class SpotifyAuthTests(TestCase):
    @patch('your_app.views.generate_random_state')
    def test_generate_state_returns_string(self, mock_generate):
        mock_generate.return_value = 'randomstate'
        state = mock_generate()
        self.assertEqual(state, 'randomstate')
        self.assertEqual(len(state), 12)

    @patch('your_app.views.exchange_code_for_token')
    def test_spotify_callback_success(self, mock_exchange):
        mock_exchange.return_value = {'access_token': 'token', 'refresh_token': 'refresh'}
        response = self.client.get(reverse('main:spotify_callback') + '?code=validcode')
        self.assertEqual(response.status_code, 200)

    def test_spotify_callback_no_code_or_error(self):
        response = self.client.get(reverse('main:spotify_callback'))
        self.assertEqual(response.json(), {'error': 'Missing code or authorization error'})

class SpotifyDataViewTests(TestCase):
    def test_spotify_data_requires_authentication(self):
        response = self.client.get(reverse('main:spotify_data'))
        self.assertEqual(response.status_code, 302)

    @patch('your_app.views.get_spotify_top_tracks')
    def test_spotify_api_call_success(self, mock_top_tracks):
        mock_top_tracks.return_value = {'top_tracks': [], 'top_artists': []}
        response = self.client.get(reverse('main:spotify_data'))
        self.assertEqual(response.status_code, 200)

class LlamaRequestTests(TestCase):
    @patch('your_app.views.make_llama_request')
    def test_llama_api_call_success(self, mock_llama_call):
        mock_llama_call.return_value = {'result': 'mocked response'}
        response = self.client.post(reverse('main:llama_request'))
        self.assertEqual(response.json(), {'result': 'mocked response'})

    def test_invalid_llama_api_key(self):
        response = self.client.post(reverse('main:llama_request'), {'api_key': 'wrong_key'})
        self.assertEqual(response.status_code, 403)

class SettingsTests(TestCase):
    def test_env_variables_loaded_correctly(self):
        required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI', 'OPENAI_API_KEY']
        for var in required_vars:
            self.assertTrue(os.getenv(var) is not None)

    def test_django_essential_settings(self):
        self.assertIsNotNone(os.getenv('SECRET_KEY'))
        self.assertIn('localhost', os.getenv('ALLOWED_HOSTS'))

    def test_database_connection(self):
        from django.db import connections
        conn = connections['default']
        self.assertEqual(conn.settings_dict['ENGINE'], 'django.db.backends.sqlite3')

    def test_static_settings(self):
        from django.conf import settings
        self.assertTrue(settings.STATIC_URL is not None)
        self.assertTrue(settings.STATICFILES_DIRS)

class UserManagerTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(username='admin', password='password123')
        self.assertTrue(superuser.is_superuser and superuser.is_staff)

    def test_create_user_no_username_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='password123')

# Integration and End-to-End Tests

class SpotifyAuthenticationFlowTests(TestCase):
    @patch('your_app.views.exchange_code_for_token')
    def test_end_to_end_spotify_auth_flow(self, mock_exchange):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'password123'})

        mock_exchange.return_value = {'access_token': 'token', 'refresh_token': 'refresh'}
        response = self.client.get(reverse('main:spotify_callback') + '?code=validcode')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())

class UserRegistrationAndLoginFlowTests(TestCase):
    def test_complete_registration_flow(self):
        response = self.client.post(reverse('main:registration'), {
            'username': 'testuser', 'password1': 'password123', 'password2': 'password123'
        })
        self.assertRedirects(response, reverse('main:login'))

        response = self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('main:home-page'))

        response = self.client.get(reverse('main:library_page'))
        self.assertEqual(response.status_code, 200)

    def test_session_management_between_login_and_spotify_interactions(self):
        self.client.post(reverse('main:registration'), {
            'username': 'testuser', 'password1': 'password123', 'password2': 'password123'
        })
        self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'password123'})

        response = self.client.get(reverse('main:spotify_data'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('main:library_page'))
        self.assertEqual(response.status_code, 200)

class APIErrorAndTimeoutHandlingTests(TestCase):
    @patch('your_app.views.get_spotify_top_tracks')
    def test_spotify_api_timeout(self, mock_spotify):
        mock_spotify.side_effect = TimeoutError('Request timed out')
        response = self.client.get(reverse('main:spotify_data'))
        self.assertEqual(response.status_code, 500)

    @patch('your_app.views.make_llama_request')
    def test_llama_api_timeout(self, mock_llama_call):
        mock_llama_call.side_effect = TimeoutError('Request timed out')
        response = self.client.post(reverse('main:llama_request'))
        self.assertEqual(response.status_code, 500)
