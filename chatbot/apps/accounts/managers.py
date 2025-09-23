from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        Create and return a regular user with the given username and password.
        """
        if not username:
            raise ValueError('The username field must be set.')

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and return a superuser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)
