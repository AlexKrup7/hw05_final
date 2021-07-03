from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст Тестовый текст Тестовый',
            author=cls.user,
        )

    def test_post_15(self):
        """Отображается ли только 15 символов"""
        test_post = self.post.text[:15]
        self.assertEqual(test_post, str(self.post))

    def test_group_title(self):
        """Проверка титула группы"""
        test_title = self.group.title
        self.assertEqual(test_title, str(self.group))
