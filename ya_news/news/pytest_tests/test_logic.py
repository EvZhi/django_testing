from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    number_comments_up_to = Comment.objects.count()
    detail_url = reverse('news:detail', args=(news.id,))
    client.post(detail_url)
    comments_count = Comment.objects.count()
    assert comments_count == number_comments_up_to


def test_user_can_create_comment(
        author, author_client, news
):
    """Авторизованный пользователь может отправить комментарий."""
    detail_url = reverse('news:detail', args=(news.id,))
    form_data = {
        'text': 'Текст комментария'
    }
    number_comments_up_to = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count != number_comments_up_to
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """
    Тест на запрещенные слова в комментариях.

    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    detail_url = reverse('news:detail', args=(news.id,))
    number_comments_up_to = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == number_comments_up_to


def test_author_can_delete_comment(author_client, comment, news):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    number_comments_up_to = Comment.objects.count()
    response = author_client.delete(delete_url)
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count != number_comments_up_to


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    number_comments_up_to = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == number_comments_up_to


def test_author_can_edit_comment(
        author_client, comment, news,
):
    """Авторизованный пользователь может дедактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {
        'text': 'Новый текст комментария'
    }
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {
        'text': 'Новый текст комментария'
    }
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
