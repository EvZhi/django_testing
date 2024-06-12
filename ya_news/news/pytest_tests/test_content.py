import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('list_news')
def test_news_count(client, home_url):
    """
    Тест количества новостей на главной странице.

    Количество новостей на главной странице - не более 10.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('list_news')
def test_news_order(client, home_url):
    """
    Тест сортировки новостей.

    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('list_comments')
def test_comments_order(author_client, detail_url):
    """
    Тест сортировки комментариев.

    Комментарии на странице отдельной новости
    отсортированы в хронологическом порядке:
    старые в начале списка, новые — в конце.
    """
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_availability_form_for_different_users(
    parametrized_client, author_client, status, detail_url
):
    """
    Тест наличия формы комментария для различных пользователей.

    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is status
    if parametrized_client == author_client:
        assert isinstance(response.context['form'], CommentForm)
