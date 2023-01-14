from django.test import TestCase
from yatube.settings import POST_COUNT

from ..models import Comment, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый п',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коммен'
        )

    def test_post_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        test_dict = {
            self.post: ' '.join(
                self.post.text.split()[:POST_COUNT]),
            self.group: self.group.title,
            self.comment: ' '.join(
                self.comment.text.split()[:POST_COUNT])
        }
        for field, expected_value in test_dict.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value, 'oops!')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        DICT = {
            Post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
                'image': 'Картинка',
            },
            Comment: {
                'text': 'Текст комментария',
                'author': 'Автор',
                'post': 'Текст поста',
                'pub_date': 'Дата публикации'
            },
            Group: {
                'title': 'Название группы',
                'description': 'Описание группы',
                'slug': 'Адрес группы'
            },
        }
        for model, dict in DICT.items():
            for field, expected_value in dict.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        DICT = {
            Post: {
                'text': 'Введите текст поста',
                'group': 'Группа, в которой будет этот пост',
            },
            Comment: {
                'text': 'Введите текст комментария'
            },
            Group: {
                'title': 'Введите название группы',
                'description': 'Введите описание группы',
                'slug': 'Желаемый адрес группы'
            },
        }
        for model, field_help_texts in DICT.items():
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_value)
