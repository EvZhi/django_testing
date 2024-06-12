import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author, author_client, news, detail_url, form_data, comment_text
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    """
    Тест на запрещенные слова в комментариях.

    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, url_to_comments, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        edit_url,
        comment,
        new_comment_text,
        new_form_data,
        url_to_comments
):
    """Авторизованный пользователь может дедактировать свои комментарии."""
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_comment_text


def test_user_cant_edit_comment_of_another_user(
        not_author_client, edit_url, comment, comment_text, new_form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
