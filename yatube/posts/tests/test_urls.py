from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.index = (
            'posts/index.html',
            '/'
        )
        cls.group_list = (
            'posts/group_list.html',
            '/group/test_slug/'
        )
        cls.profile = (
            'posts/profile.html',
            '/profile/auth/'
        )
        cls.post_detail = (
            'posts/post_detail.html',
            '/posts/1/'
        )
        cls.create = (
            'posts/create_post.html',
            '/create/'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Any')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адреса."""
        url_names = {
            PostURLTest.index,
            PostURLTest.group_list,
            PostURLTest.profile,
            PostURLTest.post_detail
        }
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress[1])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_exists_at_desired_location(self):
        """Проверка доступности адреса /create/ для авторизованного клиена."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_redirect(self):
        """Проверка работы перенаправления гостя при попытке правки поста."""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_urls_uses_correct_template(self):
        """Проверка шаблона для адресов."""
        templates_url_names = {
            PostURLTest.index,
            PostURLTest.group_list,
            PostURLTest.profile,
            PostURLTest.post_detail,
            PostURLTest.create
        }
        for template in templates_url_names:
            adress = template[1]
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template[0],)

    def test_404_url_exists_at_desired_location(self):
        """Проверка ответа /страница не найдена/ на рандомный запрос"""
        response = self.guest_client.get('/random/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
