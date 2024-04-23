from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Менеджер модели User."""

    def create_user(self, phone: str, **extra_fields):
        """Метод для создания нового пользователя."""
        if not phone:
            raise ValueError('Для создания нового пользователя необходимо '
                             'установить номер телефона')
        user = self.model(phone=phone, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, **extra_fields):
        """Метод для создания суперпользователя."""
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Для создания суперпользователя поле is_superuser'
                             ' должно иметь значение True.')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(phone, **extra_fields)


class User(AbstractUser):
    """Модель пользователя."""
    username = None
    password = None
    phone = PhoneNumberField(
        verbose_name='Номер телефона',
        unique=True)
    my_invite_code = models.CharField(
        verbose_name='Мой код приглашения',
        max_length=6,
        null=True,
        default=None,
    )
    referal_user = models.ForeignKey(
        'self',
        verbose_name='Приглашен пользователем',
        on_delete=models.SET_NULL,
        related_name='refered_users',
        null=True
    )

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.phone)
