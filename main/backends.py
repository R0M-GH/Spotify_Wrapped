from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class AuthModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            username_field = UserModel.USERNAME_FIELD
            user = UserModel._default_manager.get(**{username_field: username})
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user