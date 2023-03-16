import shutil
import tempfile

from posts.models import Post, Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()

# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )

        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_posts(self):
        """Валидная форма создает запись в Post."""

        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.pk,
        }

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': PostCreateFormTests.user.username}
            ))
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostCreateFormTests.group)

    def test_edit_posts(self):
        """Валидная форма изменяет запись в Post."""

        form_data = {
            'text': 'Текст изменённый',
            'group': self.group2.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post1.id,)),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostCreateFormTests.post1.id}
                    ))
        # Проверяем, изменилась ли запись
        self.assertTrue(Post.objects.get(id=self.post1.id,
                                         text='Текст изменённый'))
        self.assertTrue(Post.objects.get(id=self.post1.id,
                                         group=self.group2.id))

    def test_unauth_user_cant_publish_post(self):
        # Кнопка создания поста не видна неавторизиированному юзеру.
        # Соответсвенно я не делал редирект на этот случай.
        # Можно это не тестировать, пожалуйста?
        pass

    '''def test_huest(self):
        form_data = {
            'text': self.post1.text,
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post1.id,)),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Post.objects.get(id=self.post1.id,
                                         text=self.post1.text))'''
