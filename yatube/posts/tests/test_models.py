from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError

from ..models import Post, Group, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post' * 2,
        )

    def test_post_have_correct_object_names(self):
        """Тестируем корректную работу __str__ у модели Post."""
        post = PostModelTest.post
        text = post.text[:15]
        error_message = (
            'Текст модели Post отображается некорректно; '
            'проверь __str__ модели'
        )
        self.assertEqual(str(post), text, error_message)

    def test_group_have_correct_object_name(self):
        """Тестируем корректную работу __str__ у модели Group."""
        group = PostModelTest.group
        title = 'Тестовая группа'
        error_message = (
            'Название группы модели Group отображается '
            'некрорректно; проверь __str__ модели'
        )
        self.assertEqual(
            str(group),
            title,
            error_message
        )

    def test_post_have_correct_fields_titels(self):
        """Тестирование verbose_name и help_text модели Post"""
        post = self.post
        verbose_name = post._meta.get_field('text').verbose_name
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(verbose_name, 'Текст поста')
        self.assertEqual(
            help_text, 'Здесь вы можете написать содержание поста',
        )

    def test_group_have_correct_fields_titles(self):
        """Тестирование verbose_name и help_text модели Post"""
        group = self.group
        verbose_name = group._meta.get_field('title').verbose_name
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(verbose_name, 'Название группы')
        self.assertEqual(help_text, 'Напишите название вашей группы')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_follow_user',
        )

    def test_constraints_on_follow_yourself(self):
        """Тестируем constraints модели Follow"""
        expected_message = 'CHECK constraint failed: author_exclude_user'
        with self.assertRaisesMessage(IntegrityError, expected_message):
            Follow.objects.create(
                user=self.user,
                author=self.user,
            )
