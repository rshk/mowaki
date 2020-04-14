from pyql import Object
import hashlib

from app.utils.normalize import normalize_email_address


User = Object('User', {
    'id': int,
    'email': str,
    'display_name': str,
    'image_url': str,
})


@User.field('display_name')
def resolve_display_name(user, info) -> str:
    if user.display_name:
        return user.display_name

    return get_name_from_email(user.email)


@User.field('image_url')
def resolve_image_url(user, info) -> str:
    return get_gravatar_url(user.email)


def get_name_from_email(email):
    return email.split('@')[0]


def get_gravatar_url(email):
    _email = normalize_email_address(email).encode()
    email_hash = hashlib.md5(_email).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?s=80&d=mp'.format(email_hash)
