from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()

TEMPLATES_URL_NAMES = {
    '/group/test-slug/': 'posts/group_list.html',
    '/profile/TestUser/': 'posts/profile.html',
    '/posts/1/': 'posts/post_detail.html',
    '/posts/1/edit/': 'posts/create_post.html',
    '/create/': 'posts/create_post.html',
}


class StaticURLTesting(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTesting(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test-slug',
            description='Testing',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            pk=1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_templates(self):
        """Тест на соответствие шаблонов для адресов."""
        for adress, template in TEMPLATES_URL_NAMES.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Проверь шаблон {template} для адреса {adress}'
                )

    def test_create_url_redirect_anonymous_on_login(self):
        """Тест на корректность редиректа для анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        error_message = (
            'Проверь правильность редиректа со страницы "/create/" '
            'для анонимного пользователя'
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/', msg_prefix=error_message
        )

    def test_edit_post_url_not_author(self):
        """
        Тест на проверку возможности редактирования поста
        пользователем, не являющимся автором.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        error_message = 'Проверь права для доступа к редакции поста'
        self.assertRedirects(
            response, '/posts/1/', msg_prefix=error_message
        )

    def test_edit_post_url_author(self):
        """
        Тест на возможность зайти на страницу редактирования поста
        пользователем, являющимся автором данного поста
        """
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_url(self):
        """
        Тест на корректность возвращаемого кода ошибки
        к несуществующему адресу.
        """
        response = self.guest_client.get('/404/')
        error_message = 'Несуществующий запрос не возвращает код ошибки 404'
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND.value,
            error_message
        )

    def test_404_template(self):
        """Тестирование на переход к кастомной странице 404."""
        response = self.guest_client.get('net_takoy_stranitcy')
        self.assertTemplateUsed(response, 'core/404.html')
