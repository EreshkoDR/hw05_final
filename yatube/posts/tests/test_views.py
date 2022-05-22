from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, Follow


User = get_user_model()

EXPECTED_CONTEXT = {
    'text': 'Барак... Обама! Ну типа))0)',
    'author': 'DmitryGordon',
    'group': 'Test group',
    'description': 'test description',
    'first_name': 'Dmitry',
    'last_name': 'Gordon',
}

# Добавил для тестирования паджинатора
# Теперь думаю, не излишне ли это всё?
COUNT_POSTS = 14


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='DmitryGordon',
            first_name='Dmitry',
            last_name='Gordon',
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='test description'
        )
        text = 'Барак... Обама! Ну типа))0)'
        bulk = []
        for i in range(COUNT_POSTS):
            bulk.append(
                Post(
                    author=cls.user,
                    text=text,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(bulk)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class NamespaceTest(PostsViewsTest):
    def test_namespaces(self):
        """Тестирование namespace."""
        response = self.authorized_client.get('/')
        reverse_tempates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'DmitryGordon'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in reverse_tempates.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    (f'При тестировании {template}, namespace '
                     f'{reverse_name} оказался неверным')
                )


class IndexPageTest(PostsViewsTest):
    """Тесты для страницы index."""
    def test_index_show_correct_context(self):
        """Тестирование содержания context страницы index."""
        response = self.authorized_client.get('/')
        context = response.context.get('page_obj')[0]
        self.assertEqual(str(context.text), EXPECTED_CONTEXT['text'])
        self.assertEqual(str(context.author), EXPECTED_CONTEXT['author'])
        self.assertEqual(str(context.group), EXPECTED_CONTEXT['group'])

    def test_index_paginator_first_page(self):
        """Тест паджинотора, первая страница."""
        response = self.authorized_client.get('/')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_paginator_second_page(self):
        """Тест паджинатора, вторая страница."""
        response = self.authorized_client.get('/' + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), 4)


class GroupListPageTest(PostsViewsTest):
    """Тесты для страницы group_list."""
    def test_group_list_show_correct_context(self):
        """Тестирование содержания context страницы group_list."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        context = response.context.get('page_obj')[0]
        first_name = str(context.author.first_name)
        last_name = str(context.author.last_name)
        text = str(context.text)
        description = str(context.group.description)
        # Тесты
        self.assertEqual(first_name, EXPECTED_CONTEXT['first_name'])
        self.assertEqual(last_name, EXPECTED_CONTEXT['last_name'])
        self.assertEqual(text, EXPECTED_CONTEXT['text'])
        self.assertEqual(description, EXPECTED_CONTEXT['description'])

    def test_group_list_paginator_firs_page(self):
        """Тест паджинотора group_list первая страница."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_paginator_second_page(self):
        """Тест паджинотора group_list вторая страница."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), 4)


class ProfilePagetest(PostsViewsTest):
    """Тесты для страницы profile."""
    def test_profile_show_correct_context(self):
        """Тестирование содержания context страницы profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'DmitryGordon'}))
        context = response.context.get('page_obj')[0]
        first_name = str(context.author.first_name)
        last_name = str(context.author.last_name)
        text = str(context.text)
        # Тесты
        self.assertEqual(first_name, EXPECTED_CONTEXT['first_name'])
        self.assertEqual(last_name, EXPECTED_CONTEXT['last_name'])
        self.assertEqual(text, EXPECTED_CONTEXT['text'])

    def test_profile_paginator_firs_page(self):
        """Тест паджинотора profile первая страница."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_paginator_second_page(self):
        """Тест паджинотора group_list вторая страница."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), 4)


class PostDetailPageTest(PostsViewsTest):
    """Тесты для страницы post_detail."""
    def test_post_detail_show_correct_context(self):
        """Тестирование страницы post_detail."""
        post_id = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        ).context.get('page_obj')[0].id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        id = response.context.get('posts').id
        self.assertEqual(id, post_id)


class EditPostPageTest(PostsViewsTest):
    """Тесты для страницы edit_post."""
    def test_edit_post_context(self):
        """Тестирование на правильность форм страницы edit_post."""
        post_id = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        ).context.get('page_obj')[0].id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expectes in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expectes)


class CreatePostPageTest(PostsViewsTest):
    """Тесты для страницы create_post."""
    def test_create_post_form(self):
        """Тестирование на правильность форм страницы create_post."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expectes in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expectes)


class CreatePost(PostsViewsTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            author=cls.user,
            text='Some text for test',
            group=cls.group,
        )

    def is_in(self, page, search):
        """Функция проверки содержания паджинатора."""
        # Спасибо за ревью <3
        count_page = (COUNT_POSTS // 10) + 1
        for i in range(1, count_page + 1):
            pages = self.authorized_client.get(page + f'?page={i}')
            for k in pages.context.get('page_obj'):
                if k.text == search:
                    return True
        return False

    def test_post_in_pages(self):
        """
        Тест страниц index, post_list, profile на нахождение
        в них созданного поста
        """
        pages = {
            'index': reverse(
                'posts:index'
            ),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ),
            'profile': reverse(
                'posts:profile', kwargs={'username': CreatePost.user}
            ),
        }
        for page, adress in pages.items():
            with self.subTest(page=page):
                self.assertTrue(self.is_in(adress, 'Some text for test'))


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_user_for_cache')
        Post.objects.create(
            author=cls.user,
            text='Test cache'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_delete_post_and_check_context(self):
        """Тестирование кэша страницы index"""
        # проверяем создание поста в базе
        self.assertTrue(
            Post.objects.filter(text='Test cache').exists()
        )
        # проверяем создание поста на странице index
        response = self.authorized_client.get('/')
        is_in = response.context.get('page_obj')[0]
        content_before_delete = response.content.decode()
        self.assertEqual(is_in.text, 'Test cache')
        # Удаляем пост
        Post.objects.get(text='Test cache').delete()
        # Проверяем удаление из базы
        self.assertFalse(
            Post.objects.filter(text='Test cache').exists(),
            'Пост не удален из базы'
        )
        # Проверяем кэш на наличие поста
        response = self.authorized_client.get('/')
        # Проверяем, что страница не отдаёт контекст
        self.assertIsNone(response.context)
        content_after_delete = response.content.decode()
        # Сравниваем контент страницы до удаления и после
        self.assertEqual(
            content_before_delete,
            content_after_delete
        )


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bulk_users = []
        bulk_text = []
        for i in range(4):
            bulk_users.append(User(username=f'Test_user{i}'))
        User.objects.bulk_create(bulk_users)
        for i in range(4):
            bulk_text.append(
                Post(
                    author=User.objects.get(username=f'Test_user{i}'),
                    text=f'Test_text_by_user_{i}'
                )
            )
        Post.objects.bulk_create(bulk_text)

    def setUp(self):
        self.user = User.objects.get(username='Test_user0')
        self.anonimous_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def is_in(self, page, obj):
        response = self.authorized_client.get(
            reverse(page)
        )
        for i in response.context.get('page_obj'):
            if i.text == obj:
                return True
        return False

    def test_following(self):
        """Тест на подписку и отписку."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Test_user1'})
        )
        following = User.objects.get(username='Test_user1')
        is_in = Follow.objects.filter(user=self.user, author=following)
        self.assertTrue(is_in.exists(), 'Подписка не удалась')
        # Проверяем отписку
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'Test_user1'}
            )
        )
        self.assertFalse(is_in.exists(), 'Не удалось отписаться')

    def test_following_anonimous(self):
        response = self.anonimous_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Test_user1'})
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/profile/Test_user1/follow/'
        )

    def test_follow_page(self):
        """"Тестируем страницу follow_index."""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Test_user1'})
        )
        expected_text = 'Test_text_by_user_1'
        error_message = 'На странице не найдены подписки'
        self.assertTrue(
            self.is_in('posts:follow_index', expected_text),
            error_message
        )
        # Тестируем, что нет постов других пользователей
        expected_text = 'Test_text_by_user_2'
        error_message = 'На странице присутствуют посты других пользователей'
        self.assertFalse(
            self.is_in('posts:follow_index', expected_text),
            error_message
        )
