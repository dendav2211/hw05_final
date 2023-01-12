from django.test import Client, TestCase

from http import HTTPStatus

from ..models import Group, Post, User

HOME_URL = '/'
PAGE_CREATE_URL = '/create/'
CREATE_REDIRECT_URL = '/auth/login/?next=/create/'
FOLLOW_URL = '/follow/'


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание группы',
            slug='test_slug'
        )
        self.user = User.objects.create_user(
            username='HasNoName'
        )
        self.user_no_author = User.objects.create_user(
            username='NoAuthor'
        )
        self.post = Post.objects.create(
            text='Текст для тестов',
            group=self.group,
            author=self.user
        )
        self.GROUP_URL = '/group/test_slug/'
        self.PROFILE_URL = f'/profile/{self.user.username}/'
        self.POST_URL = f'/posts/{self.post.id}/'
        self.PAGE_404_URL = '/unexisting_page/'
        self.EDIT_POST_URL = f'/posts/{self.post.id}/edit/'
        self.EDIT_POST_URLS = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        self.COMMENT_URL = f'/posts/{self.post.id}/comment/'
        self.FOLLOWING_URL = f'/profile/{self.user.username}/follow/'
        self.UN_FOLLOWING_URL = f'/profile/{self.user.username}/unfollow/'
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_no_author_client = Client()
        self.authorized_no_author_client.force_login(self.user_no_author)

    def test_all_desired_location(self):
        """Проверка доступности всех страниц"""
        list_for_test = [
            [self.guest_client, HOME_URL, HTTPStatus.OK],
            [self.guest_client, self.GROUP_URL, HTTPStatus.OK],
            [self.guest_client, self.PROFILE_URL, HTTPStatus.OK],
            [self.guest_client, self.POST_URL, HTTPStatus.OK],
            [self.guest_client, self.PAGE_404_URL, HTTPStatus.NOT_FOUND],
            [self.authorized_client, PAGE_CREATE_URL, HTTPStatus.OK],
            [self.authorized_client, self.EDIT_POST_URL, HTTPStatus.OK],
            [self.authorized_client, FOLLOW_URL, HTTPStatus.OK],
            [self.authorized_client, self.COMMENT_URL, HTTPStatus.FOUND],
            [self.authorized_client, self.FOLLOWING_URL, HTTPStatus.FOUND],
            [self.authorized_client, self.UN_FOLLOWING_URL, HTTPStatus.FOUND]
        ]
        for dicts in list_for_test:
            with self.subTest():
                client_for_test, url_for_test, status_for_test = dicts
                response = client_for_test.get(url_for_test)
                self.assertEqual(response.status_code, status_for_test)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        url1 = CREATE_REDIRECT_URL
        url2 = self.EDIT_POST_URLS
        pages = {PAGE_CREATE_URL: url1,
                 self.EDIT_POST_URL: url2}
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            HOME_URL: 'posts/index.html',
            self.GROUP_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            PAGE_CREATE_URL: 'posts/create_post.html',
            self.EDIT_POST_URL: 'posts/create_post.html',
            FOLLOW_URL: 'posts/follow.html',
            self.PAGE_404_URL: 'core/404.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
