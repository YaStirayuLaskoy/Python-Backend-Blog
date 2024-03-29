import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from http import HTTPStatus

from posts.models import Post, Group, Follow

User = get_user_model()

# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создам юзера для поста
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
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

        # Создам запись в БД Post
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

    def setUp(self):
        self.user2 = User.objects.create_user(username='UserTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post1.id}):
                        'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post1.id}):
                        'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostPagesTests.user)
        self.assertEqual(post.pub_date, PostPagesTests.post1.pub_date)
        self.assertEqual(post.text, PostPagesTests.post1.text)
        self.assertEqual(post.group, PostPagesTests.post1.group)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'})))
        self.check_context_contains_page_or_post(response.context)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': 'HasNoName'})))
        self.check_context_contains_page_or_post(response.context)
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostPagesTests.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      args=[self.post1.id]))
        self.check_context_contains_page_or_post(response.context, post=True)
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'], PostPagesTests.post1)
        self.assertIn('post_count', response.context)
        self.assertEqual(
            response.context['post_count'], PostPagesTests.user.posts.count()
        )

    def test_image_correct_context(self):
        """Шаблоны передают картинку в контекст."""
        urls = (
            reverse('posts:index'),
            reverse('posts:profile', args=(self.user.username,)),
            reverse('posts:post_detail', args=[self.post1.id]),
            reverse('posts:group_list', args=(self.group.slug,))
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertContains(response, '<img')

    def test_create_edit_post_show_correct_context(self):
        """create_post и post_edit сформированы с правильным контекстом."""
        urls = (
            ('posts:create_post', []),
            ('posts:post_edit', [self.post1.id])
        )
        for name, args in urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertIn('is_edit', response.context)
                self.assertIsInstance(response.context["is_edit"], bool)
                self.assertEqual(response.context["is_edit"],
                                 (name == "posts:post_edit"))
                self.assertIn('form', response.context)

    def test_post_new_home(self):
        """Новый пост на главной странице сайта."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)

    def test_post_new_group_posts(self):
        """Новый пост на странице группы."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'})))
        object = response.context['page_obj']
        new_post = self.post1
        self.assertIn(new_post, object)

    def test_post_new_group_post(self):
        """Новый пост в профайле пользователя."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': 'HasNoName'})))
        object = response.context['page_obj']
        new_post = self.post1
        self.assertIn(new_post, object)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        post_cache = Post.objects.create(
            text='Текст для теста кэша',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('posts:index'))

        post_cache.delete()
        response_old = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_old.content, response.content)

        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_new.content)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        new_user_follow = User.objects.create_user(username='test_follow')

        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(new_user_follow.username,)),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.first()
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, new_user_follow)

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться от других"""
        author = User.objects.create_user(username='test')
        Follow.objects.create(user=self.user, author=author)

        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(author.username,)),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.count(), 0)
