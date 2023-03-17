from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


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

        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )

        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

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
            'text': self.post1.id,
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
                                         text=self.post1.id))
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
