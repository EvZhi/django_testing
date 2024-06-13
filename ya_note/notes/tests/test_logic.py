from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):
    """Класс тестирования логики."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')

    def equal_fields_note(self, note, data):
        return (
            note.title == data['title']
            and note.text == data['text']
            and note.slug == data['slug']
        )

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.author_client.post(
            self.url_add, data=self.data
        )
        number_up_to = Note.objects.count()
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), number_up_to)

        new_note = Note.objects.last()
        self.assertTrue(self.equal_fields_note(new_note, self.data))
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        number_up_to = Note.objects.count()
        response = self.client.post(self.url_add, self.data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url_add}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), number_up_to)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        number_up_to = Note.objects.count()
        response = self.author_client.post(self.url_add, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), number_up_to)

    def test_empty_slug(self):
        """
        Тест на автомматическое заполнение поля slug.

        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify
        """
        self.data.pop('slug')
        response = self.author_client.post(self.url_add, self.data)
        number_up_to = Note.objects.count()
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), number_up_to)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        number_up_to = Note.objects.count()
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), number_up_to)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.not_author_client.post(url)
        number_up_to = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), number_up_to)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertTrue(self.equal_fields_note(self.note, self.data))

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.not_author_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertFalse(self.equal_fields_note(self.note, self.data))
