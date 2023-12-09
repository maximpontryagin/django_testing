from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_COUNT = 5
User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )
    return comment


@pytest.fixture
def create_many_news():
    today = datetime.today()
    all_news = [
        News(title=f'Новсть {index}',
             text='Текст новости',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_many_comments(news, author):
    author = author
    news = news
    now = timezone.now()
    for index in range(COMMENT_COUNT):
        all_comments = Comment(news=news, text=f'комментарий {index}',
                               author=author)
        all_comments.created = now - timedelta(days=index)
        all_comments.save()


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(news):
    return reverse('news:edit', args=(news.id,))


@pytest.fixture
def delete_url(news):
    return reverse('news:delete', args=(news.id,))


@pytest.fixture
def home_url():
    return reverse('news:home')
