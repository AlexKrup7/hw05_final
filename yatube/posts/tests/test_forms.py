import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='test title',
            slug='test_slug',
            description='test'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test text num',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create(self):
        """Проверка формы создания нового поста"""
        posts = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_post = {'text': 'test text form',
                     'group': self.group.id,
                     'image': uploaded}
        self.authorized_client.post(reverse('new_post'), data=form_post)
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(Post.objects.count(), posts + 1)
        self.assertTrue(Post.objects.filter(text='test text form',
                                            group=self.group,
                                            image='posts/small.gif'
                                            ).exists())
        self.assertTrue(response.context['page'][0].image.name, uploaded.name)

    def test_post_edit(self):
        """При редактировании поста , изменяется соответсвующая запись в БД"""
        form_data = {
            'text': 'test text num 2',
            'group': self.group.id
        }
        self.authorized_client.post(reverse('post_edit', kwargs={
            'username': self.author.username,
            'post_id': self.post.id
        }), data=form_data)
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': self.author.username,
            'post_id': self.post.id
        }))
        self.assertEqual(response.context['post'].text, form_data['text'])
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            id=self.post.id,
            group=form_data['group']
        ).exists())
