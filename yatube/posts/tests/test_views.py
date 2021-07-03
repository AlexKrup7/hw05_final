from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Group, Post, User


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test title',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='Тест пятнадцати символов',
            author=cls.user,
            group=cls.group
        )

        cls.templates_url_names = {
            'misc/index.html': reverse('index'),
            'posts/group.html': reverse('group', kwargs={
                'slug': cls.group.slug}),
            'posts/new_post.html': reverse('new_post'),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_templates_sub(self):
        """Проверка шаблонов"""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_have_good_group(self):
        """Пост добавился в нужную группу"""
        response = self.authorized_client.get(reverse('index'))
        post = response.context['page'][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_context_index(self):
        """Проверка контекста главной страницы"""
        response = self.authorized_client.get(reverse('index'))
        test_post = response.context['page'][0]
        self.assertEqual(test_post, self.post)

    def test_context_group(self):
        """Проверка контекста группы"""
        response = self.authorized_client.get(reverse('group', kwargs={
            'slug': self.group.slug}))
        test_post = response.context['page'][0]
        test_group = response.context['group']
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_group, self.group)

    def test_context_new_post(self):
        """Проверка контекста нового поста"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, exp in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, exp)

    def test_context_edit_post(self):
        """Проверка контекста редактирования поста"""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, exp in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, exp)

    def test_context_profile(self):
        """Проверка контекста профиля"""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': self.user.username,
        }))

        profile = {
            'author': self.post.author,
            'post_count': self.user.posts.count()
        }
        for value, exp in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, exp)
        test_page = response.context['page'][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_context_post(self):
        """Проверка контекста поста"""
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))
        profile = {
            'author': self.post.author,
            'post': self.post
        }
        for value, exp in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, exp)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(title='TestGroup',
                                         slug='test_slug',
                                         description='Test description')
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user, text='Тестовый пост {i}',
                group=cls.group)
        cls.templates_pages_names = {
            'misc/index.html': reverse('index'),
            'posts/group.html': reverse('group',
                                        kwargs={'slug': cls.group.slug}),
            'posts/profile.html': reverse('profile', kwargs={
                'username': cls.user.username})}

    def test_first_page_contains_ten_records(self):
        """Проверка паджинатора 10 постов на 1 странице"""
        for adress, reverse_name in self.templates_pages_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(reverse_name)
                self.assertEqual(len(
                    response.context.get('page').object_list), 10
                )

    def test_second_page_contains_three_records(self):
        """Проверка паджинатора 3 поста на 2 странице"""
        for adress, reverse_name in self.templates_pages_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(
                    response.context.get('page').object_list), 3
                )


class TestCacheIndex(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(title='TestGroup',
                                         slug='test_slug',
                                         description='Test description')

    def test_cache_index(self):
        """Тест кэша"""
        cache.clear()
        Post.objects.create(
            text='test text',
            author=self.user
        )
        self.authorized_user.get(reverse('index'))
        response = self.authorized_user.get(reverse('index'))
        self.assertEqual(response.context, None)
        cache.clear()
        response = self.authorized_user.get(reverse('index'))
        self.assertNotEqual(response.context, None)
        self.assertEqual(response.context['page'][0].text, 'test text')
