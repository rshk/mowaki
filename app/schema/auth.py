from pyql import Object

from app.lib.auth import get_token_for_credentials, get_user

from .base import schema

AuthResult = Object('AuthResult', fields={
    'ok': bool,
    'token': str,
})


UserInfo = Object('UserInfo', fields={
    'id': int,
    'username': str,
    'email': str,
    'display_name': str,
})


@schema.mutation.field('authenticate')
def resolve_authenticate(root, info, email: str, password: str) -> AuthResult:
    token = get_token_for_credentials(email, password)
    if not token:
        return AuthResult(ok=False, token=None)
    return AuthResult(ok=True, token=token.decode())


@schema.query.field('user')
def resolve_user(root, info, user_id: int = None) -> UserInfo:

    user = info.context.auth_info.require_user()

    if user_id is not None:
        if user_id != user.id:
            user = get_user(user_id)
            if not user:
                return None

    return UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name)
