from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend

class AuthModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            print("authenticate username is None")
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            print("authenticate about to get user from Model")
            # username_field = UserModel.USERNAME_FIELD
            # user = UserModel._default_manager.get(**{username_field: username})

            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            print("UserModel.DoesNotExist exception occurred")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            print("properly returning user from authenticate method")
            return user

        return None