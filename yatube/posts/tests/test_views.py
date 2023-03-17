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

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      args=[self.post1.id]))
        object = response.context.get('post')
        expected = self.post1.id
        self.assertEqual(object.id, expected)

    def test_create_edit_post_show_correct_context(self):
        """create_post и post_edit сформированы с правильным контекстом."""
        urls = (
            ('posts:create_post', 'posts/create_post.html'),
            ('posts:post_edit', 'posts/create_post.html', [self.post1.id])
        )
        for name, html, args in urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name))
                self.assertTemplateUsed(response, html)
                self.assertIn(args, response.context)

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
