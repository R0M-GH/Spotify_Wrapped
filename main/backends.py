from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend

class AuthModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user with the given username and password.

        This method attempts to retrieve a user based on the provided username and
        checks if the password matches. If authentication is successful and the user
        can be authenticated, the user object is returned; otherwise, None is returned.

        Args:
            request: The HTTP request object.
            username (str, optional): The username of the user attempting to authenticate.
            password (str, optional): The password of the user attempting to authenticate.
            **kwargs: Additional keyword arguments.

        Returns:
            UserModel | None: The authenticated user object if authentication succeeds,
            or None if authentication fails (e.g., user does not exist or password does not match).

        Raises:
            UserModel.DoesNotExist: If the user with the given username does not exist.
        """
        UserModel = get_user_model()

        # Debug: Print the input username and password received
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # username_field = UserModel.USERNAME_FIELD
            # user = UserModel._default_manager.get(**{username_field: username})

            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None