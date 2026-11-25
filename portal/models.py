from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.full_name})"

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class Application(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'Принято в работу'
        COMPLETED = 'completed', 'Выполнено'

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Автор заявки'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название заявки'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Категория'
    )
    plan_image = models.ImageField(
        upload_to='plans/%Y/%m/%d/',
        verbose_name='Фото помещения или план'
    )
    design_image = models.ImageField(
        upload_to='designs/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Изображение готового дизайна'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий администратора'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус заявки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}] — {self.user.username}"