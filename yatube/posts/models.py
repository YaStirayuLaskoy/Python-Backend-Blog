from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст',
        max_length=100,
        help_text='Напишите сюда свой текст'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # upload_to это директория, куда загрузится картинка

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        # выводим текст поста
        return self.text[:15]


'''class Comment(models.Model):

    text = models.TextField(
        'Комментарий',
        max_length=100,
        help_text='Напишите сюда свой текст'
    )

    created = models.DateField(auto_created=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        # on_delete=models.Чтото_тут,
        related_name='comments'
    )'''
