import pytest

from http import HTTPStatus

from news.models import Comment
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from news.forms import BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    url = reverse('news:detail', args=('1'))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_auth_user_can_create_comment(form_data, author_client, author, news):
    url = reverse('news:detail', args=('1'))
    response = author_client.post(url, data=form_data)
    url_comment = f'{url}#comments'
    assertRedirects(response, url_comment)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.news == news
    assert comment.text == 'Новый текст'
    assert comment.author == author


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    detail_url = reverse('news:detail', args=('1'))
    edit_url = reverse('news:edit', args=('1'))
    form_data = {'text': 'Текст проверка'}
    response = author_client.post(edit_url, data=form_data)
    url_comment = detail_url + '#comments'
    assertRedirects(response, url_comment)
    comment.refresh_from_db()
    assert comment.text == 'Текст проверка'


@pytest.mark.django_db
def test_auth_cant_edit_comment(admin_client, comment):
    edit_url = reverse('news:edit', args=('1'))
    form_data = {'text': 'Текст проверка'}
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get()
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    detail_url = reverse('news:detail', args=('1'))
    url_comment = detail_url + '#comments'
    delete_url = reverse('news:delete', args=('1'))
    response = author_client.post(delete_url)
    assertRedirects(response, url_comment)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_cant_delete_comment(admin_client, comment):
    delete_url = reverse('news:delete', args=('1'))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.parametrize('bad_word', BAD_WORDS)
@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, bad_word):
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    url = reverse('news:detail', args=('1'))
    response = admin_client.post(url, data=bad_words_data)
    assert 'form' not in response.context
    assert Comment.objects.count() == 0
