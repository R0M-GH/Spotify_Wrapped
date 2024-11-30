from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend


class AuthModelBackend(ModelBackend):
    """
    Custom authentication backend for handling user authentication.

    This backend overrides the default `authenticate` method to provide custom authentication logic.
    It uses the provided username and password to authenticate the user against the `UserModel`.
    If the user exists and the password is correct, the user is returned for further authentication.

    Attributes:
        None
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticates a user by their username and password.

        This method attempts to authenticate a user by looking up the `UserModel` using the provided username,
        checking if the password matches, and ensuring that the user is allowed to authenticate.

        Args:
            request (HttpRequest): The HTTP request object that triggered the authentication process.
            username (str, optional): The username provided by the user for authentication. If not provided,
                                      the `kwargs` dictionary is checked for the value.
            password (str, optional): The password provided by the user for authentication.
            **kwargs: Additional keyword arguments that may contain the username field if the `username` is not provided.

        Returns:
            UserModel or None: Returns the authenticated user if credentials are valid, otherwise returns None.

        Raises:
            None
        """
        UserModel = get_user_model()

        # Debug: Print the input username and password received
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Fetch the user by the provided username
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        # Check if the password matches and if the user can authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None