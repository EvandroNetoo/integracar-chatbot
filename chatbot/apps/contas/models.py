from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    validate_email,
)
from django.db import models

from contas.managers import UserManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    email = models.EmailField(
        'email',
        unique=True,
        blank=False,
        validators=[validate_email],
    )

    name = models.CharField(
        'nome',
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                r'^[a-zA-Z\s]+$',
                'O nome deve conter apenas letras',
            ),
            MinLengthValidator(3, 'O nome deve ter pelo menos 3 caracteres'),
        ],
    )

    is_staff = models.BooleanField(
        'status de staff',
        default=False,
    )
    is_active = models.BooleanField(
        'ativo',
        default=True,
        help_text=(
            'Indica se este usuário deve ser tratado como ativo. '
            'Desmarque esta opção ao invés de excluir contas.'
        ),
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True,
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def first_name(self):
        return self.name.split(' ')[0]
