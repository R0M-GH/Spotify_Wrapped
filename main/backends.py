from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend

class AuthModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
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