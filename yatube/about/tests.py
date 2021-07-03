from django.test import Client, TestCase

from http import HTTPStatus


class AboutURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_templates_sub(self):
        """Проверка темлэйтов"""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_url(self):
        """Проверка УРЛ"""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
