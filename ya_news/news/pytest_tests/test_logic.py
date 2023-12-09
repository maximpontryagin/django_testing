from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    assert comments_count_before - comments_count_after == 0


def test_auth_user_can_create_comment(author_client, author, news, detail_url):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    url_comment = f'{detail_url}#comments'
    assertRedirects(response, url_comment)
    comments_count_after = Comment.objects.count()
    assert comments_count_after - comments_count_before == 1
    comment = Comment.objects.last()
    assert comment.news == news
    assert comment.text == FORM_DATA['text']
    assert comment.author == author


def test_author_can_edit_comment(author_client, comment, author, news,
                                 detail_url, edit_url):
    response = author_client.post(edit_url, data=FORM_DATA)
    url_comment = detail_url + '#comments'
    assertRedirects(response, url_comment)
    comment.refresh_from_db()
    assert comment.news == news
    assert comment.text == FORM_DATA['text']
    assert comment.author == author


def test_auth_cant_edit_comment(admin_client, comment, edit_url):
    response = admin_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.last()
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(author_client, comment,
                                   detail_url, delete_url):
    comments_count_before = Comment.objects.count()
    url_comment = detail_url + '#comments'
    response = author_client.post(delete_url)
    assertRedirects(response, url_comment)
    assert comments_count_before - Comment.objects.count() == 1


def test_auth_cant_delete_comment(admin_client, comment, delete_url):
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_before - Comment.objects.count() == 0


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(admin_client, bad_word):
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {choice(bad_word)}, еще текст'}
    url = reverse('news:detail', args=('1'))
    response = admin_client.post(url, data=bad_words_data)
    assert 'form' not in response.context
    assert Comment.objects.count() == comments_count_before
