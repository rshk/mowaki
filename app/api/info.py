from pyql import Object

from .base import schema
from .user import User

Info = Object('Info', {
    'version': str,
})


@Info.field('user')
def resolve_info_user(root, info) -> User:
    user = info.context.auth_info.user
    if not user:
        return None
    return user


@schema.query.field('info')
def resolve_info(root, info) -> Info:
    return Info(version='1.0')
