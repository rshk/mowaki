import pytest

from app.lib.auth import auth_tokens

pytestmark = pytest.mark.usefixtures('db')


def test_can_authenticate_user(users_core, client):
    users_core.create(email='foo@example.com', password='password')

    resp = client.execute("""
    mutation ($user: String!, $pass: String!) {
      authenticate(username: $user, password: $pass) {
        ok
        token
      }
    }
    """, variables={
        'user': 'foo@example.com',
        'pass': 'password',
    })

    assert resp.status_code == 200
    assert resp.json['data']['authenticate']['ok'] is True
    assert resp.json['data']['authenticate']['token']


def test_bad_credentials(users_core, client):
    users_core.create(email='foo@example.com', password='BAD PASSWORD')

    resp = client.execute("""
    mutation ($user: String!, $pass: String!) {
      authenticate(username: $user, password: $pass) {
        ok
        token
      }
    }
    """, variables={
        'user': 'foo@example.com',
        'pass': 'password',
    })

    assert resp.status_code == 200
    assert resp.json['data']['authenticate']['ok'] is False
    assert resp.json['data']['authenticate']['token'] is None


def test_info_user_is_empty_for_anonymous(users_core, client):
    resp = client.execute("""
    query {
      info {
        user {
          id, email, displayName
        }
      }
    }
    """)

    assert resp.status_code == 200
    assert resp.json['data']['info']['user'] is None


def test_info_user_is_populated_for_user(users_core, client):
    uid = users_core.create(email='foo@example.com', password='BAD PASSWORD')
    token = auth_tokens.issue(uid).decode()

    resp = client.execute("""
    query {
      info {
        user {
          id, email, displayName
        }
      }
    }
    """, token=token)

    assert resp.status_code == 200
    assert resp.json['data']['info']['user']['id'] == uid
