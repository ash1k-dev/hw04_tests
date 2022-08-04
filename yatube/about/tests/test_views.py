from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        status_for_static = ['about:author', 'about:tech']
        for response_status in status_for_static:
            with self.subTest(response_status=response_status):
                response = self.guest_client.get(reverse('about:author'))
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        response_for_static = {reverse('about:author'): 'posts/about/author.html',
                               reverse('about:tech'): 'posts/about/tech.html'
                               }
        for response_status, expected in response_for_static.items():
            with self.subTest(response_status=response_status):
                response = self.guest_client.get(response_status)
                self.assertTemplateUsed(response, expected)