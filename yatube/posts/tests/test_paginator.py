from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.paginator import Page

from posts.models import Post, Group

User = get_user_model()


class TestPaginator(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for _ in range(15):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,
            )

    def test_paginator_home(self):
        """Паджинатор шаблона index принимает 10 постов."""
        response = self.client.get(reverse('posts:index'))
        page: Page = response.context['page_obj']
        self.assertEqual(len(page), 10)

    def test_paginator_group_posts(self):
        """Паджинатор шаблона group_list принимает 10 постов."""
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': self.group.slug}))
        page: Page = response.context['page_obj']
        self.assertEqual(len(page), 10)

    def test_paginator_profile(self):
        """Паджинатор шаблона profile принимает 10 постов."""
        response = self.client.get(reverse('posts:profile',
                                           kwargs={'username': 'HasNoName'}))
        page: Page = response.context['page_obj']
        self.assertEqual(len(page), 10)
