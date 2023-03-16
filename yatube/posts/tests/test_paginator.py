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

    def test_sdfsdfsdf(self):

        CASES = [
            [reverse('posts:index'), 10],
            [reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}), 10],
            [reverse('posts:profile',
                     kwargs={'username': 'HasNoName'}), 10]
        ]

        for url, posts_per_page in CASES:
            with self.subTest(url):
                self.assertEqual(len(
                    self.client.get(
                        url).context['page_obj']), posts_per_page)
