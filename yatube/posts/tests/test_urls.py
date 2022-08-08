from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_auth,
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user_auth)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_urls_for_auth_users(self):
        urls_for_auth_users = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for address, code in urls_for_auth_users.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertEqual(response.status_code, code)

    def test_task_detail_url_redirect_guest_client(self):
        urls_for_guest_client_users = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/edit/': f'/posts/{self.post.pk}/',
        }
        for address, redirect in urls_for_guest_client_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, redirect)

    def test_urls_uses_correct_template(self):
        create = 'posts/create.html'
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user_auth}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            create: f'/posts/{self.post.pk}/edit/',
            'posts/create.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertTemplateUsed(response, template)
