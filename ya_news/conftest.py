import pytest
from datetime import datetime, timedelta

from django.utils import timezone
from news.models import News, Comment
from django.contrib.auth import get_user_model

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

COMMENT_COUNT = 5
User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
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
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def create_many_comments():
    author = User.objects.create(username='username')
    news = News.objects.create(title='Новость', text='Текст')
    now = timezone.now()
    all_comments = [
        Comment(news=news, text=f'комментарий {index}', author=author,
                created=now - timedelta(days=index))
        for index in range(COMMENT_COUNT)
    ]
    Comment.objects.bulk_create(all_comments)
    return all_comments


@pytest.fixture
def form_data(news):
    return {'text': 'Новый текст', 'news': news}
