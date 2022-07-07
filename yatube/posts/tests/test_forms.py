from ..forms import PostForm
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostCreateTest(TestCase):
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
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def template_test(self, test_post, form_data):
        """Общие тесты для создания новой/редактирования записи в БД."""
        self.assertEqual(
            test_post.text, form_data['text'])
        self.assertEqual(
            test_post.author.username, self.post.author.username)
        self.assertEqual(
            test_post.group.title, self.post.group.title)

    def test_create_post(self):
        """Проверка создания новой записи в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username]))
        self.assertEqual(
            Post.objects.count(), posts_count + 1)
        test_post = response.context['page_obj'].object_list[0]
        self.template_test(test_post, form_data)

    def test_edit_post(self):
        """Проверка изменения записи в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[1]), data=form_data, follow=True)
        self.assertRedirects(response, reverse((
            'posts:post_detail'), args=[1]))
        self.assertEqual(Post.objects.count(), posts_count)
        test_edit_post = response.context['post']
        self.template_test(test_edit_post, form_data)
