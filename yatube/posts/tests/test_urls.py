from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-test',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.quest_client = Client()
        self.user = User.objects.create_user(username='NoBody')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_correct_html(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_page_for_author(self):
        if self.user == self.post.author:
            response = self.authorized_client\
                .get(f'posts/{self.post.id}/edit/', follow=True)
            self.assertRedirects(response, f'/posts/{self.post.id}/edit/')

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        response = self.guest_client.get('/profile/NoBody/')
        self.assertEqual(response.status_code, 200)

    def test_posts(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 400)

    def test_urls_uses_correct_template(self):

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': '/profile/NoBody/',
            'posts/post_detail.html': f'/posts/{self.post.id}/'
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
