import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post, User
from yatube.settings import POST_COUNT

INDEX_URL = reverse('posts:index')
POST_CREATE_POST = reverse('posts:post_create')
TEST_OF_POST: int = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CALC_FOLLOW_DIFF = 1
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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.group = Group.objects.create(
            title='название',
            description='описание группы',
            slug='test_slug'
        )
        self.user = User.objects.create_user(
            username='username'
        )
        self.post = Post.objects.create(
            text='Текст',
            group=self.group,
            author=self.user
        )
        self.post1 = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)

        self.group_test = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group2')

        self.GROUP_LIST_URL = reverse('posts:group_list',
                                      kwargs={'slug':
                                              self.group.slug})
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username':
                                           self.user.username})
        self.POST_DETAIL_URL = reverse('posts:post_detail',
                                       kwargs={'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('posts:post_edit',
                                     kwargs={'post_id': self.post.id})
        self.GROUP_LIST_TEST = reverse('posts:group_list',
                                       kwargs={'slug':
                                               self.group_test.slug})

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def exttest_post_index_group_profile_page_show_correct_cont(self):
        """Проверяем Context страницы index, group, profile, detail"""
        context = [
            self.authorized_client.get(INDEX_URL),
            self.authorized_client.get(self.GROUP_LIST_URL),
            self.authorized_client.get(self.PROFILE_URL),
            self.authorized_client.get(self.POST_DETAIL_URL),
        ]
        for response in context:
            first_object = response.context['page_obj'][0]
            context_objects = {
                self.author.id: first_object.author.id,
                self.post.text: first_object.text,
                self.group.slug: first_object.group.slug,
                self.post.id: first_object.id,
            }
            for reverse_name, response_name in context_objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_POST)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании с указанием группы добавлен корректно"""

        response_index = self.authorized_client.get(
            INDEX_URL)
        response_group = self.authorized_client.get(
            self.GROUP_LIST_URL)
        response_profile = self.authorized_client.get(
            self.PROFILE_URL)
        response_group2 = self.authorized_client.get(
            self.GROUP_LIST_TEST)
        group2 = response_group2.context['page_obj']
        response_list = [
            response_index.context['page_obj'],
            response_group.context['page_obj'],
            response_profile.context['page_obj']
        ]
        for i in response_list:
            with self.subTest():
                self.assertIn(self.post1, i)
        self.assertNotIn(self.post1, group2)

    def test_cache(self):
        """Проверка кеша"""
        start_content = self.authorized_client.get(INDEX_URL).content
        Post.objects.all().delete()
        after_delete_content = self.authorized_client.get(INDEX_URL).content
        self.assertEqual(start_content, after_delete_content)
        cache.clear()
        after_clear_content = self.authorized_client.get(INDEX_URL).content
        self.assertNotEqual(start_content, after_clear_content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(title='группа',
                                          slug='test_group')
        self.GROUP_LIST_URL = reverse('posts:group_list',
                                      kwargs={'slug':
                                              self.group.slug})
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username':
                                           self.user.username})
        posts = [
            Post(text=f'текст {i}',
                 group=self.group,
                 author=self.user)
            for i in range(TEST_OF_POST)
        ]
        self.posts = Post.objects.bulk_create(posts)

        self.client = Client()

    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на первой и второй страницах."""
        pages: tuple = (INDEX_URL,
                        self.PROFILE_URL,
                        self.GROUP_LIST_URL)
        for page in pages:
            response1 = self.client.get(page)
            response2 = self.client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(count_posts1, POST_COUNT)
            self.assertEqual(count_posts2, TEST_OF_POST - POST_COUNT)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.user = User.objects.create_user(
            username='User1'
        )
        self.user2 = User.objects.create_user(
            username='User2'
        )
        self.author = User.objects.create_user(
            username='User3')

        self.FOLLOW_URL = reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        )
        self.UNFOLLOW_URL = reverse(
            'posts:profile_unfollow', kwargs={'username': self.author.username}
        )
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username':
                                           self.author.username})
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.form_data = {'user': self.user,
                          'author': self.author
                          }
        self.test_post = Post.objects.create(author=self.author,
                                             text='Текстовый текст')

    def test_auth_user_can_follow(self):
        """Тест авторизованный пользователь может
        подписываться."""
        count_followers = Follow.objects.all().count()
        response = self.authorized_client.post(
            self.FOLLOW_URL,
            data=self.form_data,
            follow=True
        )
        final_follow = Follow.objects.all().count() - CALC_FOLLOW_DIFF
        self.assertEqual(count_followers, final_follow)
        self.assertRedirects(response, self.PROFILE_URL)

    def test_auth_user_can_unfollow(self):
        """Тест авторизованный пользователь может
        отписаться."""
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        count_followers = Follow.objects.all().count()
        unfollow = self.authorized_client.post(
            self.UNFOLLOW_URL,
            data=self.form_data,
            follow=True
        )
        final_follow = Follow.objects.all().count() + CALC_FOLLOW_DIFF
        self.assertEqual(count_followers, final_follow)
        self.assertRedirects(unfollow, self.PROFILE_URL)

    def test_follower_see_new_post(self):
        """У подписчика появляется новый пост автора.
        А у не подписчика его нет"""
        Follow.objects.create(user=self.user,
                              author=self.author)
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        posts_follow = response_follow.context['page_obj']
        self.assertIn(self.test_post, posts_follow)

    def test_follower_not_see_new_post(self):
        """У не подписчика не появляется новый пост автора."""
        Follow.objects.create(user=self.user,
                              author=self.author)
        response_no_follower = self.authorized_client2.get(
            reverse('posts:follow_index'))
        posts_no_follow = response_no_follower.context['page_obj']
        self.assertNotIn(self.test_post, posts_no_follow)
