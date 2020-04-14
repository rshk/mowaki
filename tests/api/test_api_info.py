import pytest

from app.core.user import UsersCore
from app.lib.auth import auth_tokens

pytestmark = pytest.mark.usefixtures('db')


def test_info_user_is_empty_for_anonymous(client):
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
