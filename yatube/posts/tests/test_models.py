from django.test import TestCase

from ..models import Comment, Group, Post, User

from yatube.settings import POST_COUNT


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
            text='Тестовый коммент'
        )

    def test_post_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        self.assertEqual(self.post.text[:POST_COUNT], str(self.post))

    def test_group_have_correct_object_names(self):
        """Проверяем, что у модели group корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))

    def test_title_post(self):
        """Проверка заполнения verbose_name в post"""
        field_verboses = {'text': 'Текст поста',
                          'pub_date': 'Дата публикации',
                          'group': 'Группа',
                          'author': 'Автор',
                          'image': 'Картинка'
                          }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_title_help_text_post(self):
        """Проверка заполнения help_text в post"""
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Группа, в которой будет этот пост'
                            }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value)

    def test_title_label_group(self):
        """Проверка заполнения verbose_name в group"""
        field_verboses = {'title': 'Название группы',
                          'slug': 'Адрес группы',
                          'description': 'Описание группы'
                          }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_title_help_text_group(self):
        """Проверка заполнения help_text в group"""
        field_help_texts = {'title': 'Введите название группы',
                            'slug': 'Желаемый адрес группы',
                            'description': 'Введите описание группы'
                            }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).help_text,
                    expected_value)

    def test_title_comment(self):
        """Проверка заполнения verbose_name в comment"""
        field_verboses = {'text': 'Текст комментария',
                          'pub_date': 'Дата публикации'
                          }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_comment(self):
        """Проверка заполнения help_text в comment"""
        self.assertEqual(Comment._meta.get_field('text').help_text,
                         'Введите текст комментария')
