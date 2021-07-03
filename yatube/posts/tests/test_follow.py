from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User, Follow


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.follower = User.objects.create_user(username='TestFollower')
        cls.post = Post.objects.create(text='Test Text', author=cls.user)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_authorized_follow(self):
        """Авторизированный фоловится"""
        self.authorized_client.get(reverse('profile_follow', kwargs={
            'username': self.user.username
        }))
        follow = Follow.objects.first()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author, self.user)
        self.assertEqual(follow.user, self.follower)

    def test_authorized_unfollow(self):
        """Отписывается"""
        self.authorized_client.get(reverse('profile_follow', kwargs={
            'username': self.user.username
        }))
        self.authorized_client.get(reverse('profile_unfollow', kwargs={
            'username': self.user.username
        }))
        self.assertFalse(Follow.objects.exists())

    def test_follow_index(self):
        """Пост появляется у подписчика."""
        self.user = User.objects.create(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.get(reverse('profile_follow', kwargs={
            'username': FollowTest.user.username
        }))
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertIn(self.post, response.context['page'])

    def test_unfollow_index(self):
        """Пост не появляется у не подписчика."""
        self.user = User.objects.create(username='TestUser3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertNotIn(self.post, response.context['page'])
