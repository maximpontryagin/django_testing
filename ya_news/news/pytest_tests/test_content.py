import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_paginate_count(client, create_many_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_check_comment_form_for_anonymous_user(client, news):
    url = reverse('news:detail', args=('1'))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_check_comment_form_for_auth_user(admin_client, news):
    url = reverse('news:detail', args=('1'))
    response = admin_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_news_oreder(client, create_many_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(admin_client, news, create_many_comments):
    response = admin_client.get(reverse('news:detail', args=('1',)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    comments_sorted = sorted(all_dates)
    assert all_dates == comments_sorted
