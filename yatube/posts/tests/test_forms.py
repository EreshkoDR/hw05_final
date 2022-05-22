import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='testing',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FormsTest.user)

    def test_create_new_post(self):
        """Тест на создаение новой записи."""
        count = Post.objects.count()
        data_to_send = {
            'text': 'test text',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=data_to_send,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='test text',
                group=self.group.id,
                author=self.user
            ).exists()
        )
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        last_post = response.context.get('page_obj')[0]
        self.assertEqual(last_post.text, 'test text', 'Не создалось')

    def test_edit_post(self):
        """Тест на редакцию текста."""
        old_text = Post.objects.create(
            text='Old text',
            author=self.user,
            group=self.group,
        )
        data_to_send = {
            'text': 'New text',
            'group': self.group.id,
            'author': self.user,
        }
        # Нахожу id последнего созданного поста
        id_post = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        ).context.get('page_obj')[0].id
        transmit_data = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': id_post}),
            data=data_to_send
        )
        new_text = Post.objects.get(id=id_post)
        self.assertRedirects(
            transmit_data,
            reverse('posts:post_detail', kwargs={'post_id': id_post})
        )
        self.assertNotEqual(old_text.text, new_text.text)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageFormTest(FormsTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User_with_image')
        cls.group = Group.objects.create(
            title='I have image',
            slug='image_slug',
            description='I_AM_YOUR_FATHER'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Test post with image',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ImageFormTest.user)

    def test_pages_context(self):
        """Проверка на нахождение картинки в контексте страниц."""
        pages = {
            'index': reverse(
                'posts:index'
            ),
            'profile': reverse(
                'posts:profile', kwargs={'username': self.user}
            ),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'post_detail': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ),
        }
        for page, adress in pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(adress)
                if page != 'post_detail':
                    for image in response.context.get('page_obj'):
                        self.assertEqual(image.image, 'posts/small.gif')
                else:
                    image = response.context.get('posts')
                    self.assertEqual(image.image, 'posts/small.gif')

    def test_upload_image(self):
        """Тест на загрузку картинки через PostForm."""
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test post_method upload',
            'author': self.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertTrue(Post.objects.filter(
            text='Test post_method upload',
            author=self.user,
            image='posts/small_2.gif'
        ).exists())

    def test_upload_not_image(self):
        """Тестируем загрузку (не)картинки."""
        try:
            uploaded = SimpleUploadedFile(
                name='I_AM_NOT_A_IMAGE',
                content_type='text/plain',
                content='I_AM_A_STRING',
            )
            form_data = {
                'text': 'Test_upload_not_image',
                'author': self.user,
                'image': uploaded,
            }
            self.authorized_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            )
        except TypeError:
            has_type_error = True
        error_message = 'При попытке загрузить строку, всё получилось о_О'
        self.assertTrue(has_type_error, error_message)


class CommentTest(FormsTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Commetator')
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user
        )
        cls.comment = {
            'text': 'ПеРвЫйНаХ'
        }

    def setUp(self):
        self.anonimous_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_create(self):
        """Тест на создание комментария."""
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=self.comment
        )
        is_in = Comment.objects.filter(text=self.comment['text'])
        self.assertTrue(is_in.exists())
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        is_in = response.context.get(
            'comments'
        ).filter(text=self.comment['text'])
        self.assertTrue(is_in.exists())

    def test_comment_can_create_only_authorized_user(self):
        """Тестирование на создание комментария анонимным польхователем."""
        response = self.anonimous_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=self.comment,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=%2Fposts%2F1%2Fcomment%2F'
        )
