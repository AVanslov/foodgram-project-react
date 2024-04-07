from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models

FIRSTNAME_MAX_LENGHT = 150
LASTNAME_MAX_LENGHT = 150
USERNAME_MAX_LENGHT = 150
EMAIL_MAX_LENGHT = 254


class User(AbstractBaseUser):

    first_name = models.CharField(
        verbose_name='first name', max_length=FIRSTNAME_MAX_LENGHT, blank=True
    )
    last_name = models.CharField(
        verbose_name='last name', max_length=LASTNAME_MAX_LENGHT, blank=True
    )
    username = models.CharField(
        verbose_name='username',
        max_length=USERNAME_MAX_LENGHT,
        unique=True,
        validators=[
            RegexValidator(regex='^[\w.@+-]+\z')
        ]
    )
    email = models.EmailField(
        verbose_name='email address', max_length=EMAIL_MAX_LENGHT, unique=True
    )

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('-username',)
