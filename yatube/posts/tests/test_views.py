from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()

NUM_POSTS = 10
NUM_OF_POST = 0


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )
        cls.index = (
            'posts/index.html',
            'posts:index',
            None
        )
        cls.group_list = (
            'posts/group_list.html',
            'posts:group_list',
            {'slug': cls.group.slug}
        )
        cls.profile = (
            'posts/profile.html',
            'posts:profile',
            {'username': cls.user}
        )
        cls.post_detail = (
            'posts/post_detail.html',
            'posts:post_detail',
            {'post_id': cls.post.id}
        )
        cls.create = (
            'posts/create_post.html',
            'posts:post_create',
            None
        )
        cls.post_edit = (
            'posts/create_post.html',
            'posts:post_edit',
            {'post_id': cls.post.id}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = [
            PostViewTest.index,
            PostViewTest.group_list,
            PostViewTest.profile,
            PostViewTest.post_detail,
            PostViewTest.create
        ]
        for url_template in templates_pages_names:
            reverse_url_template = reverse(
                url_template[1], kwargs=url_template[2])
            with self.subTest(reverse_url_template=reverse_url_template):
                response = self.authorized_client.get(reverse_url_template)
                self.assertTemplateUsed(response, url_template[0])

    def test_post_edit_page_show_correct_context(self):
        """URL-адрес использует соответствующий шаблон post_edit."""
        response = self.authorized_client.get(
            reverse(self.post_edit[1], kwargs=self.post_edit[2])
        ),
        if self.authorized_client == self.post.author:
            self.assertTemplateUsed(response, self.create[0])

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(self.index[1]))
        self.assertEqual(
            response.context['page_obj'].object_list[0], self.post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(self.group_list[1], kwargs=self.group_list[2])
        )
        self.assertEqual(response.context.get('group'), self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile получает правильный контекст."""
        response = self.guest_client.get(
            reverse(self.profile[1], kwargs=self.profile[2]))
        self.assertEqual(response.context.get('author'), self.post.author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail получает правильный контекст."""
        response = self.guest_client.get(
            reverse(self.post_detail[1], kwargs=self.post_detail[2]))
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(self.create[1])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            self.post_edit[1], kwargs=self.post_edit[2])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_correct_create_on_page(self):
        """Проверка, что пост добавился на страницы."""
        templates = [
            PostViewTest.index,
            PostViewTest.group_list,
            PostViewTest.profile
        ]
        for template in templates:
            rev_template = reverse(template[1], kwargs=template[2])
            with self.subTest(rev_template=rev_template):
                response = self.authorized_client.get(rev_template)
                self.assertEqual(
                    response.context.get('page_obj')[NUM_OF_POST], self.post)

    def test_post_in_correct_group(self):
        """Проверка, что пост попал в нужную группу."""
        uncorrect_group = Group.objects.create(
            title='Тестовый заголовок',
            slug='uncorrect-slug',
            description='Тестовое описание',
        )
        response = self.authorized_client.get(
            reverse(self.group_list[1], args=[uncorrect_group.slug]))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_paginator_correct(self):
        """ Проверка паджинатора. """
        templates = [
            PostViewTest.index,
            PostViewTest.group_list,
            PostViewTest.profile
        ]
        for template in templates:
            rev_template = reverse(template[1], kwargs=template[2])
            with self.subTest(rev_template=rev_template):
                response = self.authorized_client.get(rev_template)
                self.assertEqual(len(response.context['page_obj']), NUM_POSTS)
