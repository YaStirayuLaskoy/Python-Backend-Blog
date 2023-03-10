from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


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

        # Создам запись в БД Post
        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

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

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        object = response.context['page_obj']
        self.assertEqual(object[0].id, self.post1.id)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': 'HasNoName'})))
        self.assertEqual(response.context.get('author').username, 'HasNoName')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      args=[self.post1.id]))
        object = response.context.get('post')
        expected = self.post1.id
        self.assertEqual(object.id, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=[self.post1.id]))
        object = response.context.get('form').instance.id
        expected = self.post1.id
        self.assertEqual(object, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_new_home(self):
        """Новый пост на главной странице сайта."""
        response = self.authorized_client.get(reverse('posts:index'))
        object = response.context['page_obj']
        new_post = self.post1
        self.assertIn(new_post, object)

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
