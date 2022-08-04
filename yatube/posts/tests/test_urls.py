from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_auth,
            id=10
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user_auth)
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_urls_for_all_users(self):
        urls_for_all_users = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/auth/': 200,
            '/posts/10/': 200,
            '/unexisting_page/': 404,
        }
        for address, code in urls_for_all_users.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_for_auth_users(self):
        urls_for_auth_users = {
            '/posts/10/edit/': 200,
            '/create/': 200,
        }
        for address, code in urls_for_auth_users.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_for_authorized_client_users(self):
        urls_for_auth_users = {
            '/create/': 200,
        }
        for address, code in urls_for_auth_users.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_task_detail_url_redirect_guest_client(self):
        urls_for_guest_client_users = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/10/edit/': '/posts/10/',
        }
        for address, redirect in urls_for_guest_client_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, redirect)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/10/',
            'posts/create.html': '/posts/10/edit/',
            'posts/create.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertTemplateUsed(response, template)
