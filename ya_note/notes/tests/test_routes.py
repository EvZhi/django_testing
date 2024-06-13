from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс тестирования маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

        cls.name_url_add = 'notes:add'
        cls.name_url_success = 'notes:success'
        cls.name_url_list = 'notes:list'
        cls.name_url_detail = 'notes:detail'
        cls.name_url_edit = 'notes:edit'
        cls.name_url_delete = 'notes:delete'

    def test_pages_availability_for_anonymous_user(self):
        """
        Тест доступности страниц для анонимных пользователей.

        Всем пользователям доступны главная, страницы регистрации
        пользователей, входа в учётную запись и выхода из неё.
        """
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Тест доступности страниц для аутен. пользователя.

        Аутентифицированному пользователю доступна страница
        со списком заметок notes/, страница успешного добавления
        заметки done/, страница добавления новой заметки add/.
        """
        urls = (
            (self.name_url_add),
            (self.name_url_success),
            (self.name_url_list),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_user(self):
        """
        Тест доступности страниц для различных пользователей.

        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (
                self.name_url_detail,
                self.name_url_edit,
                self.name_url_delete
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Тест редиректа для анонимного пользователя.

        При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления
        заметки, отдельной заметки, редактирования или удаления
        заметки анонимный пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            (self.name_url_add, None),
            (self.name_url_success, None),
            (self.name_url_list, None),
            (self.name_url_detail, (self.note.slug,)),
            (self.name_url_edit, (self.note.slug,)),
            (self.name_url_delete, (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
