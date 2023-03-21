import shutil
import tempfile

from posts.models import Post, Group, Comment, Follow
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
        cls.user228 = User.objects.create_user(username='TestUser2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        '''cls.user = User.objects.create_user(username='TestUser2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)'''

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

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
            'image': self.uploaded,
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
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostCreateFormTests.group)

    def test_edit_posts(self):
        """Валидная форма изменяет запись в Post."""
        self.post1 = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
        )
        form_data = {
            'text': 'Текст изменённый',
            'group': self.group2.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post1.id,)),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post1.id}
                    ))
        post = Post.objects.get(id=self.post1.id)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.group, self.group2)

    def test_unauth_user_cant_publish_pos(self):
        """Валидная форма не создает запись в Post."""
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=/create/')
        self.assertEqual(Post.objects.count(), 0)

    def test_user_can_comment_post(self):
        """Комментировать посты может только авторизованный пользователь."""
        self.post2 = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
        )
        form_data = {
            'text': 'Комментарий для теста'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post2.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 1)

    def test_subscribe(self):
        """Авторизованный пользователь может подписываться на других"""
        self.post228 = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
        )
        self.authorized_client.get('/profile/TestUser2/follow/')
        self.assertEqual(Follow.objects.count(), 1)

    def test_subscribe2(self):
        """Авторизованный пользователь может отписываться от других"""
        self.post228 = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
        )
        self.authorized_client.get('profile/TestUser2/unfollow/')
        self.assertEqual(Follow.objects.count(), 0)
