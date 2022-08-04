from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    # def test_about_url_exists_at_desired_location(self):
    #     """Проверка доступности адреса /page/about/."""
    #     response = self.guest_client.get('/about/author/')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_about_url_uses_correct_template(self):
    #     """Проверка шаблона для адреса /page/about/."""
    #     response = self.guest_client.get('/about/author/')
    #     self.assertTemplateUsed(response, 'posts/about/author.html')

    def test_about_url_exists_at_desired_location(self):
        """URL-адрес использует соответствующий адрес."""
        templates_url_names = ['/about/author/', '/about/tech/']
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/about/author.html': '/about/author/',
            'posts/about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
