from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Класс тестирования контента."""

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

    def test_notes_list_for_different_users(self):
        """
        Тест списка заметок для различных пользователей.

        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list, в словаре context; в список заметок
        одного пользователя не попадают заметки другого пользователя;
        """
        url = reverse('notes:list')
        users_statuses = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest(user=user, note_in_list=note_in_list):
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
