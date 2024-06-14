import pytest
from datetime import timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return (
        News.objects.create(title='Заголовок', text='Текст заметки',)
    )


@pytest.fixture
def list_news():
    now = timezone.now()
    list_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=now - timedelta(days=index)
        )
        list_news.append(news)
    News.objects.bulk_create(list_news)


@pytest.fixture
def comment(author, news):
    return (
        Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария'
        )
    )


@pytest.fixture
def list_comments(news, author):
    now = timezone.now()
    count_comment = 10
    for index in range(count_comment):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
