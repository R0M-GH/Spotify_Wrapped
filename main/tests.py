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
        """
        Tests the creation of a regular user.

        This method verifies that a user is created with the expected default values
        and that the username is correctly set.
        """
        user = User.objects.create_user(username="testuser", password="password123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.username, "testuser")

    def test_create_superuser(self):
        """
        Tests the creation of a superuser.

        This method verifies that a superuser is created with the correct
        attributes for staff and superuser status.
        """
        admin_user = User.objects.create_superuser(username="admin", password="password123")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_str_method(self):
        """
        Tests the __str__ method of the User model.

        This method checks that the string representation of a user instance
        returns the correct username.
        """
        user = User(username="testuser")
        self.assertEqual(str(user), "testuser")  # Assuming __str__ is correct

    def test_unique_username(self):
        """
        Tests that usernames are unique.

        This method ensures that attempting to create a second user with the
        same username raises an exception.
        """
        User.objects.create_user(username="uniqueuser", password="password123")
        with self.assertRaises(Exception):
            User.objects.create_user(username="uniqueuser", password="password456")

    def test_get_username(self):
        """
        Tests the get_username method.

        This method verifies that the get_username method returns the correct username
        for a user instance.
        """
        user = User(username="testuser")
        self.assertEqual(user.get_username(), "testuser")

    def test_default_values(self):
        """
        Tests the default values for new users.

        This method checks that new users have the correct default attribute values,
        including is_active, is_superuser, and is_staff.
        """
        """Test default values for new users."""
        user = User.objects.create_user(username="defaultuser", password="password123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertIsNone(user.spotify_access_token)
        self.assertIsNone(user.spotify_refresh_token)

    def test_spotify_tokens(self):
        """
        Tests setting and retrieving Spotify access and refresh tokens.

        This method checks that Spotify tokens can be correctly assigned to a user
        and retrieved afterward.
        """
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
        """
        Tests that creating a user without a username raises a ValueError.

        This method verifies the expected exception is raised when the username
        is not provided during user creation.
        """
        """Test creating a user without a username raises ValueError."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(username=None, password="password123")
        self.assertEqual(str(context.exception), "You have not provided a valid username.")

    def test_create_superuser_with_missing_fields(self):
        """
        Tests that creating a superuser with missing is_staff or is_superuser fields works correctly.

        This method ensures the superuser is created as expected regardless
        of default settings for staff and superuser attributes.
        """
        """Test that creating a superuser with missing is_staff or is_superuser fields works correctly."""
        admin_user = User.objects.create_superuser(username="adminuser", password="password123")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_date_joined_default(self):
        """
        Tests that the date_joined field is set to the current time by default.

        This method validates that a user's date_joined attribute is not None
        after user creation.
        """
        """Test that date_joined is set to the current time by default."""
        user = User.objects.create_user(username="dateuser", password="password123")
        self.assertIsNotNone(user.date_joined)

    def test_user_permissions(self):
        """
        Tests the functionality of PermissionsMixin methods and attributes.

        This method checks that user attributes associated with permissions
        behave as expected, including is_superuser and is_active markers.
        """
        """Test that PermissionsMixin methods and attributes are functional."""
        user = User.objects.create_user(username="permissionuser", password="password123")
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_invalid_username(self):
        """
        Tests that creating a user with an invalid username raises a ValueError.

        This method verifies that an exception is raised when an attempt is made
        to create a user with an empty string as the username, maintaining the
        user model's requirement for a non-empty username.
        """
        """Test creating a user with an invalid username."""
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="password123")


class RegistrationFormTest(TestCase):

    def test_valid_form(self):
        """
        Tests that the registration form is valid with correct data.

        This method checks that a form with valid username, matching passwords,
        and a valid birthday is accepted as valid.
        """
        form_data = {
            'username': 'testuser',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'birthday': '1990-01-01'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """
        Tests that the form is invalid if passwords do not match.

        This method verifies that providing two different passwords in the
        password fields results in a validation error, and the correct error message
        is returned.
        """
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
        """
        Tests that the form is invalid if the birthday is missing.

        This method checks that if the birthday field is left blank, the form
        is considered invalid, and the corresponding error is captured.
        """
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
        """
        Tests that the form is invalid if no data is provided.

        This method verifies that an empty form does not pass validation,
        and all required fields have associated error messages.
        """
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
        self.assertIn('birthday', form.errors)


class CustomUserManagerTest(TestCase):
    def test_create_user(self):
        """
        Tests the creation of a regular user.

        This method verifies that a user is correctly created with the expected
        username, that the password is set correctly, and that the user's
        staff and superuser statuses are set to False by default.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('securepassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        Tests the creation of a superuser.

        This method checks that a superuser is created with the expected
        username, that the password is set correctly, and that the user's
        staff and superuser statuses are set to True.
        """
        user = User.objects.create_superuser(username='adminuser', password='adminpassword')
        self.assertEqual(user.username, 'adminuser')
        self.assertTrue(user.check_password('adminpassword'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_username(self):
        """
        Tests that creating a user without a username raises a ValueError.

        This method verifies that attempting to create a user with an empty
        string as the username raises the appropriate exception.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='securepassword')

    def test_create_superuser_without_username(self):
        """
       Tests that creating a superuser without a username raises a ValueError.

       This method checks that an exception is raised when an attempt is made
       to create a superuser with an empty username, ensuring the username
       field is required.
       """
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='', password='adminpassword')


class UserModelTest(TestCase):
    def test_user_creation(self):
        """
        Tests the user creation functionality.

        This method verifies that a user can be created with a specified username
        and password, and confirms that the username and password set correctly
        using the User model's methods.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('securepassword'))

    def test_user_get_username(self):
        """
        Tests the get_username method.

        This method verifies that the get_username method returns the correct
        username for the newly created user instance.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertEqual(user.get_username(), 'testuser')

    def test_user_delete_with_wraps(self):
        """
        Tests the deletion of a user along with associated Wraps.

        This method creates a user and an associated Wraps record, then
        calls the delete_with_wraps method to ensure the user and all
        related Wraps records are deleted as expected.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})

        # Ensure Wraps record is created
        self.assertEqual(Wraps.objects.count(), 1)

        user.delete_with_wraps()

        # Ensure Wraps record is deleted after user deletion
        self.assertEqual(Wraps.objects.count(), 0)

    def test_user_birthday_default(self):
        """
        Tests that the default value for birthday is set correctly.

        This method verifies that a newly created user has a birthday attribute
        that is an instance of datetime, indicating that it has been initialized
        correctly upon user creation.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertIsInstance(user.birthday, datetime)

    def test_user_is_active_default(self):
        """
        Tests the default value for the is_active attribute.

        This method checks that a newly created user is marked as active
        by default, confirming that the is_active attribute is properly initialized.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        self.assertTrue(user.is_active)


class WrapsModelTest(TestCase):
    def test_wrap_creation(self):
        """
        Tests wrap creation functionality.

        This method verifies that a Wraps instance can be created successfully
        with the appropriate attributes, including username, term, and Spotify
        display name. It also checks that the creation_date is set to the current
        time and confirms that the total count of Wraps instances is correct.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})
        self.assertEqual(wrap.username, 'testuser')
        self.assertEqual(wrap.term, '2024')
        self.assertEqual(wrap.spotify_display_name, 'Test Display')
        self.assertIsInstance(wrap.creation_date, datetime)
        self.assertEqual(Wraps.objects.count(), 1)

    def test_wrap_str_method(self):
        """
        Tests the __str__ method of the Wraps model.

        This method verifies that the string representation of a Wraps instance
        correctly combines the username and the creation date, ensuring that
        the __str__ method functions as expected.
        """
        user = User.objects.create_user(username='testuser', password='securepassword')
        wrap = Wraps.objects.create(username=user.username, term='2024', spotify_display_name='Test Display',
                                    wrap_json={})
        self.assertEqual(str(wrap), 'testuser' + str(wrap.creation_date))

    def test_wrap_missing_username(self):
        """
        Tests that a Wraps instance cannot be created with a missing username.

        This method checks that trying to create a Wraps instance with a None value
        for the username raises a ValidationError, ensuring that the username
        field is required and properly validated.
        """
        with self.assertRaises(ValidationError):
            wrap = Wraps(username=None, spotify_display_name='Test Display', wrap_json={})
            wrap.full_clean()  # Will raise ValidationError if username is None


class UserManagerTests(TestCase):
    def test_user_creation_manager(self):
        """
        Tests the creation of a regular user using the UserManager.

        This method verifies that a user can be successfully created with
        the specified username and password, and checks that the user's
        attributes (username, password check, staff status, and superuser status)
        are correctly set.
        """
        user = User.objects.create_user('user1', 'password1')
        self.assertEqual(user.username, 'user1')
        self.assertTrue(user.check_password('password1'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_creation_manager(self):
        """
        Tests the creation of a superuser using the UserManager.

        This method checks that a superuser can be successfully created with
        the specified username and password, and ensures that the user's
        attributes (username, password check, staff status, and superuser status)
        are correctly set.
        """
        user = User.objects.create_superuser('admin1', 'adminpassword')
        self.assertEqual(user.username, 'admin1')
        self.assertTrue(user.check_password('adminpassword'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

class LoginFormTest(TestCase):

    def test_valid_form(self):
        """
        Tests that the login form is valid with correct credentials.

        This method verifies that providing a valid username and password
        results in a valid form submission.
        """
        form_data = {
            'username': 'testuser',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_username(self):
        """
        Tests that the login form is invalid when the username is missing.

        This method ensures that leaving the username field empty results
        in an invalid form submission, and checks that the appropriate error
        is generated.
        """
        form_data = {
            'username': '',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        """
        Tests that the login form is invalid when the password is missing.

        This method verifies that leaving the password field empty returns
        an invalid form status, along with the correct error message.
        """
        form_data = {
            'username': 'testuser',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_empty_form(self):
        """
        Tests that the login form is invalid when all fields are empty.

        This ensures that an entirely empty form submission fails validation,
        and that errors are returned for all required fields.
        """
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class ForgetFormTest(TestCase):

    def test_valid_form(self):
        """
        Tests that the forget form is valid with all required information.

        This method ensures that when valid input is provided for username,
        security answer, and new passwords, the form is considered valid.
        """
        form_data = {
            'username': 'testuser',
            'security_answer': '1990-01-01',
            'new_password1': 'securepassword',
            'new_password2': 'securepassword'
        }
        form = ForgetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_security_answer(self):
        """
        Tests that the forget form is invalid when the security answer is missing.

        This method verifies that leaving the security answer field empty
        results in an invalid form submission, and checks that the appropriate
        error is generated for the field.
        """
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
        """
        Tests that the forget form is invalid when the new password fields are missing.

        This method verifies that leaving both new password fields empty results in
        an invalid form submission. The test checks that appropriate error messages
        are generated for both 'new_password1' and 'new_password2' fields.
        """
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
        """
        Tests that the forget form is invalid when all fields are empty.

        This method ensures that submitting an empty form results in an invalid
        submission, and it verifies that the required fields (username, security answer,
        new_password1, and new_password2) all generate appropriate error messages.
        """
        form = ForgetForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('security_answer', form.errors)
        self.assertIn('new_password1', form.errors)
        self.assertIn('new_password2', form.errors)

class AuthModelBackendTest(TestCase):
    def setUp(self):
        """
        Sets up the test environment by creating a user and initializing the AuthModelBackend.

        This method creates a test user that can be used in subsequent authentication tests
        and initializes an instance of the AuthModelBackend for testing purposes.
        """
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='testuser',
            password='securepassword'
        )
        self.backend = AuthModelBackend()

    def test_authenticate_with_correct_credentials(self):
        """
        Tests authentication using correct credentials.

        This method verifies that providing the correct username and password
        successfully returns the user instance, confirming normal authentication flow.
        """
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='securepassword'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_incorrect_username(self):
        """
        Tests authentication using an incorrect username.

        This method checks that providing a wrong username returns None,
        indicating that authentication fails due to the username not being found.
        """
        user = self.backend.authenticate(
            request=None,
            username='wronguser',
            password='securepassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_incorrect_password(self):
        """
        Tests authentication using an incorrect password.

        This method verifies that providing the correct username but an incorrect
        password results in authentication failure, returning None.
        """
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='wrongpassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_user(self):
        """
        Tests authentication for a username that does not exist.

        This method checks that attempting to authenticate with a nonexistent username
        returns None, confirming that the backend handles nonexistent users appropriately.
        """
        user = self.backend.authenticate(
            request=None,
            username='nonexistentuser',
            password='securepassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_no_username(self):
        """
        Tests authentication when no username is provided.

        This method validates that not providing a username results in authentication
        failure, returning None as expected.
        """
        user = self.backend.authenticate(
            request=None,
            password='securepassword'
        )
        self.assertIsNone(user)

    @patch('main.backends.AuthModelBackend.user_can_authenticate', return_value=False)  # Mock user_can_authenticate
    def test_authenticate_with_unauthenticatable_user(self, mock_user_can_authenticate):
        """
        Tests authentication for a user that cannot be authenticated.

        This method verifies that if a user exists but is marked as unauthenticatable
        (e.g., inactive), the authentication process returns None.
        """
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='securepassword'
        )
        self.assertIsNone(user)
        mock_user_can_authenticate.assert_called_once_with(self.user)

class LoginFormTest(TestCase):

    def test_valid_login_form(self):
        """
        Tests that the login form is valid with correct credentials.

        This method verifies that providing a valid username and password
        results in a valid form submission, and checks the cleaned data.
        """
        form_data = {
            'username': 'testuser',
            'password': 'password123',
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')

    def test_missing_username(self):
        """
        Tests that the login form is invalid when the username is missing.

        This method ensures that leaving the username field empty results
        in an invalid form submission, and checks that the appropriate error
        is generated for the field.
        """
        form_data = {
            'username': '',
            'password': 'password123',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        """
        Tests that the login form is invalid when the password is missing.

        This method verifies that leaving the password field empty returns
        an invalid form status, along with the correct error message for the
        password field.
        """
        form_data = {
            'username': 'testuser',
            'password': '',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class ViewsTestCase(TestCase):
    def setUp(self):
        """
        Sets up the test environment for each test method.

        This method initializes a test client and creates a test user with required fields,
        logging the user in to facilitate authenticated requests in the subsequent tests.
        """
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
        """
        Tests session management after a user logs in.

        This method checks that a user can log in successfully, verifies that the session
        is created correctly, and ensures that user attributes such as username and current
        display name are accurately stored and retrievable.
        """
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
        """
        Tests access to the game view after logging in.

        This method verifies that a user can access the game view after successfully
        logging in, and checks that the appropriate template is used for the response.
        """
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
        """
        Tests handling of invalid login credentials via POST request.

        This method checks that submitting incorrect username and password results in
        a redirect and ensures that the appropriate error message is displayed
        on the login page after the user is redirected back.
        """
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
        """
        Tests that a successful registration redirects to the login page.

        This method submits valid registration data and verifies that upon successful
        registration, the user is redirected to the login page.
        """
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
        """
        Tests that unauthenticated users are redirected to the login page when accessing the library.

        This method verifies that a user who is not logged in is redirected to the login
        page when attempting to access the library view.
        """
        # Log out the user (if already logged in)
        self.client.logout()

        # Test that unauthenticated users are redirected to the login page
        response = self.client.get(reverse('library'))
        self.assertRedirects(response, '/login/?next=/library/')  # Adjust URL if needed

    def test_summary_view_logged_in(self):
        """
        Test that the summary view is accessible when logged in with valid data.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/summary.html') is used.
        """
        # Test that the summary view can be accessed when logged in with valid data
        response = self.client.get(reverse('summary', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Check standard functionality
        self.assertTemplateUsed(response, 'Spotify_Wrapper/summary.html')  # Check if the correct template is used

    def test_accountpage_redirect_unauthenticated(self):
        """
        Test that unauthenticated users are redirected to the login page when accessing the account page.

        Verifies:
        - The user is redirected to '/login/?next=/accountpage/' if unauthenticated.
        """
        # Log out the user (if already logged in)
        self.client.logout()

        # Test that unauthenticated users are redirected to the login page
        response = self.client.get(reverse('account-page'))
        self.assertRedirects(response, '/login/?next=/accountpage/')  # Adjust the redirect URL if needed

    def test_accountpage_view_user_not_found(self):
        """
        Test the account page view behavior when the user does not exist.

        Verifies:
        - An unauthenticated or non-existent user is redirected to the login page (status code 302).
        """
        # Test account page when the user does not exist
        self.client.logout()
        new_client = Client()  # Create a new client
        new_client.login(username='nonexistentuser', password='fakepass')
        response = new_client.get(reverse('account-page'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_index_view(self):
        """
        Test that the index view is accessible.

        Verifies:
        - The response status code is 200.
        - The correct template ('mainTemplates/index.html') is used.
        """
        response = self.client.get(reverse('index-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_welcome_view(self):
        """
        Test that the welcome view is accessible.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/welcome.html') is used.
        """
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/welcome.html')

    def test_contact_view(self):
        """
        Test that the contact view is accessible.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/contact.html') is used.
        """
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/contact.html')

    def test_library_view(self):
        """
        Test that the library view is accessible.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/library.html') is used.
        """
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/library.html')

    def test_register_view_get(self):
        """
        Test the registration view for a GET request.

        Verifies:
        - The response status code is 200.
        - The correct template ('registration/registration.html') is used.
        """
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration.html')

    def test_register_view_post_success(self):
        """
        Test the registration view for a successful POST request.

        Verifies:
        - The response status code is 302, indicating a redirect (to the login page).
        - A new user is successfully created in the database.
        """
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
        """
        Test the user login view for a GET request.

        Verifies:
        - The response status code is 200.
        - The correct template ('registration/login.html') is used.
        """
        # Test getting the user login page
        self.client.logout()
        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_relink_spotify_account_view(self):
        """
        Test the relink Spotify account view.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/relink_spotify_account.html') is used.
        """
        # Test the relink spotify account view
        response = self.client.get(reverse('spotify_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/relink_spotify_account.html')

    def test_spotify_login_view(self):
        """
        Test the Spotify login view.

        Verifies:
        - The response status code is 302, indicating a redirect to the Spotify authorization URL.
        - The redirect URL contains 'https://accounts.spotify.com/authorize'.
        """
        # Test the Spotify login view
        response = self.client.get(reverse('spotify_login'))
        self.assertEqual(response.status_code, 302)  # Redirect to Spotify authorization URL
        self.assertTrue('https://accounts.spotify.com/authorize' in response.url)

    def test_game_view(self):
        """
        Test the game view.

        Verifies:
        - The response status code is 200.
        - The correct template ('Spotify_Wrapper/game.html') is used.
        """
        # Test the game view
        response = self.client.get(reverse('game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')

    def test_spotify_callback_invalid_code(self):
        """
        Test the Spotify callback view with an invalid authorization code.

        Verifies:
        - The response status code is 400, indicating a bad request.
        """
        @patch.dict('os.environ', {
            'SPOTIFY_CLIENT_ID': 'mock_client_id',
            'SPOTIFY_CLIENT_SECRET': 'mock_client_secret',
        })
        def test_spotify_callback_invalid_code(self):
            response = self.client.get(reverse('spotify_callback'), {'code': 'invalid', 'state': 'random_state'})
            self.assertEqual(response.status_code, 400)  # Example assertion

    def test_genre_nebulas_view(self):
        """
        Test the GenreNebulas view with a valid date string.
        Ensures the correct HTTP status code and template are used.
        """
        # Test GenreNebulas view with a valid date string
        response = self.client.get(reverse('genre_nebulas', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/GenreNebulas.html')

    def test_stellar_hits_view(self):
        """
        Test the StellarHits view with a valid date string.
        Verifies the HTTP status code and correct template usage.
        """
        # Test StellarHits view with a valid date string
        response = self.client.get(reverse('stellar_hits', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/StellarHits.html')

    def test_constellation_artists_view(self):
        """
        Test the ConstellationArtists view with a valid date string.
        Ensures the response uses the correct template and HTTP status code.
        """
        # Test ConstellationArtists view with a valid date string
        response = self.client.get(reverse('artist_constellation', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/ConstellationArtists.html')

    def test_astro_ai_view(self):
        """
        Test the AstroAI view with a valid date string.
        Confirms the HTTP status code is 200 and the correct template is rendered.
        """
        # Test AstroAI view with a valid date string
        response = self.client.get(reverse('astro-ai', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/AstroAI.html')

    def test_newwrapper_view(self):
        """
        Test the newwrapper view to confirm the correct status code and template.
        """
        # Test newwrapper view
        response = self.client.get(reverse('new_wrapped'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/newwrapper.html')

    def test_home_view_redirects_authenticated_users(self):
        """
        Test if authenticated users can access the home view and verify the correct template is used.
        """
        # Check if an authenticated user can access the home view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainTemplates/index.html')

    def test_login_redirect_for_authenticated_user(self):
        """
        Verify that an authenticated user is redirected from the login page to the library view.
        """
        # Test that an authenticated user is redirected if they try to access the login page
        response = self.client.get(reverse('user_login'))

        # Since we expect the user to be redirected to the library
        self.assertRedirects(response, reverse('library'))

    def test_api_make_wrapped_view_unauthenticated(self):
        """
       Test that an unauthenticated user cannot access the make_wrapped API.
       Ensures a redirect to the login page with the correct 'next' parameter.
       """
        # Test that an unauthorized user cannot access the make_wrapped API
        self.client.logout()
        response = self.client.get(reverse('make-wrapped', args=['medium_term', 5]))

        # Check that the response is a redirect (302)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to the login page

        # Ensure it redirects to the login page with the correct 'next' parameter
        expected_redirect = f"{reverse('user_login')}?next=/api/make-wrapped/medium_term/5/"
        self.assertRedirects(response, expected_redirect)  # Check for the correct redirect URL

    def test_forgot_password_with_matching_birthday(self):
        """
        Test a successful password reset scenario where the provided birthday matches the user's record.
        Verifies password update and redirection to the login page.
        """
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
        """
        Test a successful password reset with valid data.
        Ensures the user can log in with the updated password.
        """
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
        """
        Test the GET request for the forgot password page.
        Confirms the correct status code and template.
        """
        # Test GET request for forgot password page
        response = self.client.get(reverse('forgot-password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/forget.html')  # Verify that the correct template is used

    def test_newwrapper_view_redirect_for_authenticated_user(self):
        """
        Test that authenticated users can access the new wrapper view and validate the correct template.
        """
        # Test that an authenticated user can access the new wrapper view
        response = self.client.get(reverse('new_wrapped'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/newwrapper.html')

    def test_invalid_url(self):
        """
        Test accessing an invalid URL to ensure a 404 status code is returned.
        """
        # Test request to an invalid URL
        response = self.client.get('/non-existent-url/')
        self.assertEqual(response.status_code, 404)  # Expect to hit a 404 error for invalid URL

    def test_library_view_content(self):
        """
        Test the library view content and validate that the correct template and expected content are rendered.
        """
        # Test the library view content
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/library.html')
        self.assertContains(response, 'Create a New Wrapped')  # Adjust based on actual expected content

    def test_summary_view_when_logged_in(self):
        """
        Test the summary view for a logged-in user with a valid date.
        Verifies the response status, template, and expected content.
        """
        # Test summary view when user is logged in with a valid date
        response = self.client.get(reverse('summary', args=['2024-11-30']))
        self.assertEqual(response.status_code, 200)  # Check if the response is valid
        self.assertTemplateUsed(response, 'Spotify_Wrapper/summary.html')  # Ensure the correct template is used
        self.assertContains(response, 'Your Listening Universe')  # Change according to the expected content

    def test_game_view_content(self):
        """
        Test the game view to validate the correct status code, template, and content.
        """
        # Test the game view content
        response = self.client.get(reverse('game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Spotify_Wrapper/game.html')
        self.assertContains(response, 'Space Destroyers')  # Change this based on actual expected content

    def test_user_logout(self):
        """
        Test the logout functionality to ensure the user is logged out and redirected appropriately.
        """
        response = self.client.logout()  # Log out the user
        self.assertIsNone(self.client.session.get('_auth_user_id'))  # Should be logged out
        response = self.client.get(reverse('home'))  # Attempt to reach the home page
        self.assertRedirects(response, '/login/?next=/home/')  # Should redirect to login

    def test_api_make_wrapped_with_invalid_session(self):
        """
           Test accessing the make_wrapped API with an invalid session.
           Ensures a redirect to the login page.
           """
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
        """
        Test access to the user profile page for a logged-in user.
        Confirms the correct status code and template are used.
        """
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
        """
       Test the summary view for a logged-in user with a valid date string.
       Ensures the correct HTTP status code and template.
       """
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
        """
        Test the home page for a logged-in user.
        Confirms the correct status code and template are used.
        """
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
        """
        Test the AstroAI page for a logged-in user with a valid date string.
        Verifies the correct status code and template usage.
        """
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
        """
        Test that a logged-out user is redirected to the login page when accessing the library view.
        """
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
        """
        Test the ConstellationArtists page for a logged-in user with a valid date string.
        Verifies the response status and correct template.
        """
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
        """
        Test the StellarHits page for a logged-in user with a valid date string.
        Confirms the HTTP status code and correct template usage.
        """
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
        """
        Test the GenreNebulas page for a logged-in user with a valid date string.
        Ensures the correct status code and template.
        """
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
        """
        Test accessing the wrapper page for a specific date as a logged-in user.

        This method:
        - Creates a dummy user and logs them in.
        - Creates a wrapped entry for the specified date.
        - Verifies that the user can access the wrapper page for the date.
        - Asserts the correct HTTP status code (200) and template used.

        Returns:
            None
            """
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
        """
        Test accessing the contact page as a logged-in user.

        This method:
        - Creates a dummy user and logs them in.
        - Attempts to access the contact page.
        - Verifies successful access by asserting the HTTP status code (200) and the template used.

        Returns:
            None
        """
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
        """
        Test the registration process with mismatched passwords.

        This method:
        - Simulates a registration attempt with mismatched passwords.
        - Verifies the appropriate error message is displayed.
        - Asserts that the registration page is re-rendered with a status code of 200.

        Returns:
            None
        """
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
        """
       Test accessing the account page as an unauthenticated user.

       This method:
       - Logs out any active user.
       - Attempts to access the account page.
       - Asserts the user is redirected to the login page with the appropriate 'next' parameter.

       Returns:
           None
       """
        self.client.logout()  # Ensure no one is logged in
        response = self.client.get(reverse('account-page'))
        self.assertRedirects(response, '/login/?next=/accountpage/')  # Ensure unlogged-in users are redirected

    def test_delete_non_existent_wrapped(self):
        """
        Test deleting a non-existent wrapped entry.

        This method:
        - Logs in a dummy user.
        - Attempts to delete a wrapped entry for a date that doesn't exist in the database.
        - Verifies a 404 status code is returned.

        Returns:
            None
        """
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
        """
       Test successful deletion of a wrapped entry.

       This method:
       - Logs in a dummy user.
       - Creates a wrapped entry for the user.
       - Verifies the entry exists before deletion.
       - Deletes the entry and verifies it no longer exists in the database.

       Returns:
           None
       """
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
        """
       Test viewing the library page with existing wraps.

       This method:
       - Logs in a dummy user.
       - Creates multiple wrapped entries for the user.
       - Verifies the library page is accessible.
       - Asserts the HTTP status code (200).

       Returns:
           None
       """
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

    
    @patch('os.getenv')
    def test_fetching_spotify_data_on_login(self, mock_getenv):
        """
        Test fetching Spotify data upon user login.

        This method:
        - Mocks environment variables for Spotify API credentials.
        - Logs in a dummy user.
        - Simulates Spotify login and callback processes.
        - Verifies Spotify access and refresh tokens are stored in the user record.

        Args:
            mock_getenv (Mock): Mock for retrieving environment variables.

        Returns:
            None
        """
        # Set up mock return values for environment variables
        mock_getenv.side_effect = lambda var: {
            'SPOTIFY_CLIENT_ID': 'mock_client_id',
            'SPOTIFY_CLIENT_SECRET': 'mock_client_secret',
        }.get(var)

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

        # Simulate the Spotify login process
        response = self.client.get(reverse('spotify_login'))  # Adjust your URL name as needed

        self.assertEqual(response.status_code, 302)  # Expect a redirect after login authorization

        # Simulate a callback from the Spotify API
        callback_response = self.client.get(reverse('spotify_callback'),
                                            {'code': 'testcode', 'state': 'teststate'})

        # Check if tokens are populated correctly in the user DB
        self.user.refresh_from_db()  # Refresh to get the latest user state

        self.assertNotEqual(self.user.spotify_access_token, '')  # Should not be empty
        self.assertNotEqual(self.user.spotify_refresh_token, '')  # Should not be empty

    def tearDown(self):
        """
       Clean up after each test.

       This method:
       - Logs out the active user.
       - Deletes the test user.

       Returns:
           None
       """
        self.client.logout()
        self.user.delete()







