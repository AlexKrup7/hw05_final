from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.comment_user = User.objects.create_user(username='TestCommentUser')
        cls.post = Post.objects.create(text='Test Text', author=cls.user)
        cls.url_comment = reverse('add_comment', kwargs={
            'username': cls.post.author.username,
            'post_id': cls.post.id
        })

    def setUp(self):
        self.anonymous = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.comment_user)

    def test_authorized_user_comment(self):
        """Только авторизированный пользователь может комментировать посты."""
        response = self.authorized_user.post(self.url_comment,
                                             {'text': 'Test Comment'},
                                             follow=True)
        self.assertContains(response, 'Test Comment')

    def test_anonymous_comment(self):
        response = self.anonymous.get(self.url_comment)
        urls = '/auth/login/?next={}'.format(self.url_comment)
        self.assertRedirects(response, urls, status_code=HTTPStatus.FOUND)
