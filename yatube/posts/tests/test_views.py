from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PagesTests(TestCase):

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

    def test_index_page_correct_template(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_group_posts_page_correct_template(self):
        response = self.authorized_client.\
            get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_profile_page_correct_template(self):
        response = self.authorized_client\
            .get(reverse('posts:profile', kwargs={'username': self.user}))
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_post_detail_page_correct_template(self):
        response = self.authorized_client.\
            get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post1.id}))
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_create_post_page_correct_template(self):
        response = self.authorized_client.get(reverse('posts:create_post'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_edit_page_correct_template(self):
        response = self.authorized_client\
            .get(reverse('posts:post_edit', kwargs={'post_id': self.post1.id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')
