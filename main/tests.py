from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import login, home, register
from .forms import RegistrationForm, LoginForm
from unittest.mock import patch

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

    def test_registration_post(self):
        response = self.client.post(reverse('registration'), {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'password123'
        })

        self.assertRedirects(response, reverse('login'))  # Expect redirect to login
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Ensure the user is created

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

    def test_spotify_data_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('spotify_data', kwargs={'time_range': 'medium_term'}))
        self.assertEqual(response.status_code, 200)  # Adjust according to actual behavior

    @patch('requests.get')
    def test_spotify_data_api_call(self, mock_get):
        mock_response = {
            "top_tracks": {"items": []},
            "top_artists": {"items": []},
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('spotify_data', kwargs={'time_range': 'medium_term'}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, mock_response)

