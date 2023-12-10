import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_paginate_count(client, create_many_news, home_url):
    response = client.get(home_url)
    object_context = response.context['object_list']
    assert object_context.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_check_comment_form_for_anonymous_user(client, news, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_check_comment_form_for_auth_user(admin_client, news, detail_url):
    response = admin_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_news_oreder(client, create_many_news, home_url):
    response = client.get(home_url)
    object_context = response.context['object_list']
    all_dates = [news.date for news in object_context]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(admin_client, news, create_many_comments, detail_url):
    response = admin_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    comments_sorted = sorted(all_dates)
    assert all_dates == comments_sorted
