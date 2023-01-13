import shutil
import tempfile
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from yatube import settings

from ..models import Comment, Group, Post, User

FINAL_DIFFERENCE = 1
CALC_COMMENT_DIFF = 1
POST_CREATE = reverse('posts:post_create')
LOGIN_URL = '/auth/login/?next=/posts/1/edit/'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
UPLOADED2 = SimpleUploadedFile(
    name='small_2.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание группы',
            slug='test_slug'
        )
        self.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group2',
            description='Описание'
        )
        self.user = User.objects.create_user(username='Baskov')
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group,
                                        image=UPLOADED)
        self.POST_EDIT_URL = reverse('posts:post_edit', args=[self.post.id])
        self.POST_DETAIL_URL = reverse('posts:post_detail',
                                       args=[self.post.id])
        self.POST_PROFILE_URL = reverse('posts:profile',
                                        args=[self.user.username])
        self.COMMENT_ADD_URL = reverse('posts:add_comment',
                                       args=[self.post.id])
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        start_posts_count = Post.objects.all().count()
        form_data = {
            'text': 'Тестовый текст для поста',
            'group': self.group.id,
            'image': UPLOADED2,
        }
        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )
        final_posts_count = Post.objects.all().count() - FINAL_DIFFERENCE
        post = Post.objects.all().latest('id')
        data_for_test = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.user,
            post.image: f'posts/{UPLOADED2}',
            final_posts_count: start_posts_count
        }
        for final_data, initial_data in data_for_test.items():
            with self.subTest(final_data=final_data):
                self.assertEqual(final_data, initial_data)
        self.assertRedirects(response, self.POST_PROFILE_URL)

    def test_create_post_null_image(self):
        start_posts_count = Post.objects.all().count()
        form_data = {
            'text': 'Тестовый текст для поста',
            'group': self.group.id,
            'image': ''
        }
        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )
        final_posts_count = Post.objects.all().count() - FINAL_DIFFERENCE
        post = Post.objects.all().latest('id')
        data_for_test = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.user,
            final_posts_count: start_posts_count
        }
        for final_data, initial_data in data_for_test.items():
            with self.subTest(final_data=final_data):
                self.assertEqual(final_data, initial_data)
        self.assertRedirects(response, self.POST_PROFILE_URL)

    def test_no_auth_no_post(self):
        '''Проверка запрета добавления поста в базу данных
           не авторизованого пользователя'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data,
                                          follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_can_edit_post_text(self):
        """Проверка прав редактирования"""
        start_posts_count = Post.objects.all().count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.id}
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True)
        post = Post.objects.all().latest('id')
        data_for_test = {
            post.pk: self.post.pk,
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.post.author,
            Post.objects.all().count(): start_posts_count
        }
        for final_data, initial_data in data_for_test.items():
            with self.subTest(final_data=final_data):
                self.assertEqual(final_data, initial_data)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_no_auth_can_not_edit_post_text(self):
        """Проверка неавторизованный не может редактировать пост"""
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.guest_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True)
        post = Post.objects.all().latest('id')
        self.assertEqual(post.text, self.post.text)
        self.assertRedirects(response, LOGIN_URL)

    def test_comment_create(self):
        """"Проверка создания комментария"""
        start_comment_count = Comment.objects.all().count()
        form_data = {'post_id': self.post.id,
                     'text': 'Новый комментарий'}
        response = self.authorized_client.post(
            self.COMMENT_ADD_URL,
            data=form_data,
            follow=True
        )
        final_posts_count = Comment.objects.all().count() - CALC_COMMENT_DIFF
        comment = Comment.objects.all().latest('pub_date')
        data_for_test = {
            comment.post.pk: self.post.id,
            comment.text: form_data['text'],
            final_posts_count: start_comment_count
        }
        for final_data, initial_data in data_for_test.items():
            with self.subTest(final_data=final_data):
                self.assertEqual(final_data, initial_data)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_comment_create_auth_only(self):
        """"Проверка неавторизованный пользователь не может комментировать"""
        start_comment_count = Comment.objects.all().count()
        form_data = {'post_id': self.post.id,
                     'text': 'Новый комментарий'}
        response = self.guest_client.post(
            self.COMMENT_ADD_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(start_comment_count, Comment.objects.all().count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
