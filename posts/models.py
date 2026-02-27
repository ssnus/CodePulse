from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    content = models.TextField(verbose_name='Содержание')
    content_lower = models.TextField(
        blank=True,
        null=True,
        editable=False,
        help_text='Для быстрого поиска без учёта регистра'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        blank=True,
        verbose_name='Лайки'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        indexes = [
            models.Index(fields=['content_lower']),
        ]

    def __str__(self):
        return f"{self.author.username} — {self.created_at:%Y-%m-%d %H:%M}"

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()

    def save(self, *args, **kwargs):
        if self.content:
            self.content_lower = self.content.lower()
        super().save(*args, **kwargs)


class Attachment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='attachments',
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    file = models.FileField(
        upload_to='posts/attachments/%Y/%m/%d/',
        verbose_name='Файл'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return self.file.name

    @property
    def is_image(self):
        ext = self.file.name.lower()
        return ext.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    content = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"{self.author.username} → {self.post} ({self.created_at:%H:%M})"