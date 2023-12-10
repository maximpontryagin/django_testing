from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


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
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('login_url')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('logout_url')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('signup_url')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('home_url')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,
         pytest.lazy_fixture('detail_url')),

    ),
)
def test_pages_availability_for_auth_user(parametrized_client,
                                          url, comment, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('edit_url')),
    ),
)
def test_redirects(client, login_url, comment, url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
