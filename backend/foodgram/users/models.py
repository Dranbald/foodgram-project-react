from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['username']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} - {self.following}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            )
        ]
