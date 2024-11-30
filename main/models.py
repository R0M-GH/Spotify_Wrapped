from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import JSONField


# Create your models here.
class CustomUserManager(UserManager):
	def _create_user(self, username, password, **extra_fields):
		if not username:
			raise ValueError('You have not provided a valid username.')
		user = self.model(username=username, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(username, password, **extra_fields)

	def create_superuser(self, username=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(max_length=50, unique=True)
	is_active = models.BooleanField(default=True)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)

	date_joined = models.DateTimeField(default=datetime.now(tz=None))

	birthday = models.DateField(default=datetime.now(tz=None))

	spotify_access_token = models.CharField(max_length=255, blank=True, null=True, default=None)
	spotify_refresh_token = models.CharField(max_length=255, blank=True, null=True, default=None)

	current_display_name = models.CharField(max_length=255, blank=True, null=True, default=None)

	objects = CustomUserManager()
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = 'User'
		verbose_name_plural = 'Users'

	def get_username(self):
		return self.username

	def delete_with_wraps(self):
		# Delete all associated Wraps first
		Wraps.objects.filter(username=self.username).delete()
		# Delete the user
		self.delete()


class Wraps(models.Model):
	username = models.CharField(max_length=50, unique=False)
	term = models.CharField(max_length=15, null=True, blank=True)
	spotify_display_name = models.CharField(max_length=255, default='')
	creation_date = models.DateTimeField(default=datetime.now)
	wrap_json = JSONField()

	def __str__(self):
		return self.username + str(self.creation_date)
