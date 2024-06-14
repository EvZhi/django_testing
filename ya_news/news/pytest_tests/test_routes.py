from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_obj',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, news_obj):
    """
    Тест доступности страниц для всех пользователей.

    Главная страница, страница отдельной новости,
    страницы регистрации, входа в учётную
    запись и выхода из неё доступны всем пользователям.
    """
    if news_obj is not None:
        url = reverse(name, args=(news_obj.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    Тест доступности страниц редактирования и удаления комментария.

    Страницы удаления и редактирования комментария доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, comment_obj',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_obj):
    """
    Тест редиректов страниц редактирования и удаления комментария.

    При попытке перейти на страницу редактирования или удаления
    комментария анонимный пользователь перенаправляется на
    страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_obj.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
