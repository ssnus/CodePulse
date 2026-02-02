from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name='Содержание')
    image = models.FileField(upload_to='posts/', null=True, blank=True, verbose_name='Вложение')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'{self.author.username} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()

    def is_image(self):
        if not self.image:
            return False
        name = self.image.name.lower()
        return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))


class Attachment(models.Model):
    post = models.ForeignKey(Post, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='posts/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def is_image(self):
        name = self.file.name.lower()
        return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author.username} commented on {self.post.author.username}\'s post'
