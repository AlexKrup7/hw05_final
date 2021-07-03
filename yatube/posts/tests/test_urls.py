from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from http import HTTPStatus

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.not_author = User.objects.create_user(username='test_not_author')
        cls.text = 'Тестовый текст'
        cls.group = Group.objects.create(title='Group', slug='slug')
        cls.post = Post.objects.create(
            text=cls.text,
            author=cls.author
        )
        cls.templates_url_names = {
            'misc/index.html': '/',
            'posts/group.html': f'/group/{cls.group.slug}/',
            'posts/new_post.html': '/new/',
            'posts/profile.html': f'/{cls.author.username}/',
            'posts/post.html': f'/{cls.author.username}/{cls.post.id}/'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
        cache.clear()

    def test_anonim_user(self):
        """Анонимный пользователь получит 302 при попытке редактирования"""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                if adress == reverse('new_post'):
                    response = self.guest_client.get(adress)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.guest_client.get(adress)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get(f'/{self.author.username}/'
                                         f'{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_author_user(self):
        """Автор поста получит 200 при попытке редактирования своего поста"""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(f'/{self.author.username}/'
                                              f'{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_author_user(self):
        """Зарегестированный не автор получит 302 при попытке редактирования"""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.not_author_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.not_author_client.get(f'/{self.author.username}/'
                                              f'{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_templates(self):
        """Проверка УРЛ и шаблонов"""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """Проверка 404"""
        response = self.guest_client.get('/test404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
