from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user_auth,
            group=cls.group,
            pk=10
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_auth)
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        create = 'posts/create.html'
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': 'auth'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': 10}),
            create: reverse('posts:post_create'),
            'posts/create.html': reverse('posts:post_edit',
                                         kwargs={'post_id': 10}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_pages_show_correct_context(self):
        for_resp = reverse('posts:post_detail', kwargs={'post_id': 10})
        response = self.authorized_client.get(for_resp)
        self.assertEqual(response.context.get('post').text, 'Текст')
        self.assertEqual(response.context.get('post').author,
                         ViewsTests.user_auth)
        self.assertEqual(response.context.get('post').group,
                         ViewsTests.group)

    def test_post_profile_group_list_index_correct_context(self):
        response = [reverse('posts:index'),
                    reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
                    reverse('posts:profile',
                            kwargs={'username': ViewsTests.user_auth})]
        for reverse_name in response:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.text, 'Текст')
                self.assertEqual(post.author, ViewsTests.user_auth)
                self.assertEqual(post.group, ViewsTests.group)

    def test_post_create_and_edit(self):
        self.post_create_url = ('posts:post_create', None, PostForm)
        self.post_edit_url = ('posts:post_edit', (self.post.id,), PostForm)
        url_list = (self.post_create_url,
                    self.post_edit_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name, argument, post_form in url_list:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name,
                                                              args=argument))
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        field = response.context.get('form').fields.get(value)
                        self.assertIsInstance(field, expected)


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=self.user,
                text=f'Тестовый пост № {i}',
                group=self.group,
            )

    def test_first_page_contains_ten_records(self):
        pages_for_pagination = [reverse('posts:index'),
                                reverse('posts:group_list',
                                        kwargs={'slug': 'test-slug'}),
                                reverse('posts:profile',
                                        kwargs={'username': 'HasNoName'})]
        for reverse_name in pages_for_pagination:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
