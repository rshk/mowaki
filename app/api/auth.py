from pyql import Object

from app.lib.auth import get_token_for_credentials

from .base import schema


AuthResult = Object('AuthResult', {
    'ok': bool,
    'token': str,
})


@schema.mutation.field('authenticate')
def resolve_auth(root, info, username: str, password: str) -> AuthResult:

    token = get_token_for_credentials(username, password)

    if not token:
        return AuthResult(ok=False, token=None)

    return AuthResult(ok=True, token=token)
