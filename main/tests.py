from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import User
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import login, home, register
from .forms import RegistrationForm, LoginForm

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
        self.assertIn('password2', form.errors)  # Check for the specific field error

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

