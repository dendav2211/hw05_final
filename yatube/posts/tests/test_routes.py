from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

HOME_URL = ' / '
INDEX_NAME_URL = 'posts:index'
PAGE_CREATE_URL = 'create/'
CREATE_NAME_URL = 'posts:post_create'
FOLLOW_URL = 'follow/'
FOLLOW_NAME_URL = 'posts:follow_index'


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
        self.post = Post.objects.create(
            text='Текст для тестов',
            group=self.group,
            author=self.user
        )
        self.GROUP_URL = f'/group/{self.group.slug}/'
        self.GROUP_LIST_URL = reverse('posts:group_list',
                                      args=[self.group.slug])
        self.PROFILE_URL = f'/profile/{self.user.username}/'
        self.PROFILE_NAME_URL = reverse('posts:profile',
                                        args=[self.user.username])
        self.POST_DETAIL_URL = f'/posts/{self.post.id}/'
        self.POST_DETAIL_NAME_URL = reverse('posts:post_detail',
                                            args=[self.post.id])
        self.POST_EDIT_URL = f'/posts/{self.post.id}/edit/'
        self.POST_EDIT_NAME_URL = reverse('posts:post_edit',
                                          args=[self.post.id])
        self.POST_COMMENT_URL = f'/posts/{self.post.id}/comment/'
        self.POST_COMMENT_NAME_URL = reverse('posts:add_comment',
                                             args=[self.post.id])
        self.POST_FOLLOW_URL = f'/profile/{self.user.username}/follow/'
        self.POST_FOLLOW_NAME_URL = reverse('posts:profile_follow',
                                            args=[self.user.username])
        self.POST_UNFOLLOW_URL = f'/profile/{self.user.username}/unfollow/'
        self.POST_UNFOLLOW_NAME_URL = reverse('posts:profile_unfollow',
                                              args=[self.user.username])
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_routes(self):
        urls_for_test = {
            HOME_URL: INDEX_NAME_URL,
            PAGE_CREATE_URL: CREATE_NAME_URL,
            self.GROUP_URL: self.GROUP_LIST_URL,
            self.PROFILE_URL: self.PROFILE_NAME_URL,
            self.POST_DETAIL_URL: self.POST_DETAIL_NAME_URL,
            self.POST_EDIT_URL: self.POST_EDIT_NAME_URL,
            self.POST_COMMENT_URL: self.POST_COMMENT_NAME_URL,
            FOLLOW_URL: FOLLOW_NAME_URL,
            self.POST_FOLLOW_URL: self.POST_FOLLOW_NAME_URL,
            self.POST_UNFOLLOW_URL: self.POST_UNFOLLOW_NAME_URL
        }
        for address, route_name in urls_for_test.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                response2 = self.authorized_client.get(route_name)
                self.assertEqual(response.status_code, response2.status_code)
