from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Введите название группы'
                             )
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес группы',
                            help_text='Желаемый адрес группы'
                            )
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Введите описание группы'
                                   )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('title',)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    POST_TEXT_LEN = 15
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, в которой будет этот пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:Post.POST_TEXT_LEN]


class Comment(models.Model):
    COMMENT_TEXT_LEN = 15
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Текст поста',
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:Comment.COMMENT_TEXT_LEN]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(user=F('author')),
                            name='could_not_follow_itself'),
            UniqueConstraint(fields=['user', 'author'], name='unique_follower')
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
