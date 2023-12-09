from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:home', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, news_object):
    if news_object is not None:
        url = reverse('news:detail', args=('1'))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status, url',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,
         pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,
         pytest.lazy_fixture('edit_url')),
    ),
)
def test_pages_availability_for_auth_user(parametrized_client,
                                          url, comment, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_redirects(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=('1'))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
