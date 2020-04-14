import bcrypt

from ..schema.user import UsersTable
from .base import TableDB


class UsersDB(TableDB):

    table = UsersTable

    def get_by_email(self, email):
        return self.get(email=email)

    def verify_credentials(self, email, password):
        """Verify a creadentials pair against the user database.

        Args:
            email: User-provided email
            password: User-provided password

        Returns:
            A User object if the credentials are valid, None otherwise
        """

        user = self.get_by_email(email)

        if not user:
            return None

        if _verify_password(password, user.password):
            return user

        return None

    def create(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['password'] = _encrypt_password(kwargs['password'])
        return super().create(*args, **kwargs)

    def update(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['password'] = _encrypt_password(kwargs['password'])
        return super().update(*args, **kwargs)

    def set_password(self, id, password):
        return self.update(id=id, password=password)


def _verify_password(password, hashed):
    if isinstance(password, str):
        password = password.encode()
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password, hashed)


def _encrypt_password(password):
    if isinstance(password, str):
        password = password.encode()
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode()
