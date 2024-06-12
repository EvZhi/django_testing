import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
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
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def home_url():
    home_url = reverse('news:home')
    return home_url


@pytest.fixture
def detail_url(news):
    detail_url = reverse('news:detail', args=(news.id,))
    return detail_url


@pytest.fixture
def list_news():
    today = datetime.today()
    list_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        list_news.append(news)
    News.objects.bulk_create(list_news)


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news, comment_text):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=comment_text
    )
    return comment


@pytest.fixture
def edit_url(comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    return edit_url


@pytest.fixture
def delete_url(comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    return delete_url


@pytest.fixture
def url_to_comments(detail_url):
    url_to_comments = detail_url + '#comments'
    return url_to_comments


@pytest.fixture
def comment_text():
    comment_text = 'Текст комментария'
    return comment_text


@pytest.fixture
def new_comment_text():
    new_comment_text = 'Новый текст комментария'
    return new_comment_text


@pytest.fixture
def form_data(comment_text):
    form_data = {'text': comment_text}
    return form_data


@pytest.fixture
def new_form_data(new_comment_text):
    new_form_data = {'text': new_comment_text}
    return new_form_data


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
