from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.post = Post.objects.bulk_create([
            Post(author=cls.user,
                 text='Тестовый текст',
                 group=cls.group,)
            for i in range(15)
        ])

    def test_paginator(self):
        """Паджинатор шаблонов принимает 10 постов."""
        pages = (
            (1, 10), (2, 5)
        )
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        )
        for url in urls:
            for page, expected_count in pages:
                response = self.client.get(url, {"page": page})
                self.assertEqual(len(
                    response.context['page_obj']), expected_count)
