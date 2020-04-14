from app.db.query.user import UsersDB

from .base import BaseCore
from .exceptions import AuthorizationError


class UsersCore(BaseCore):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._users_db = UsersDB()

    def get(self, uid):
        user = self._users_db.get(id=uid)

        if not self.can_access_user(user):
            raise AuthorizationError('Cannot get this user')

        return user

    def get_by_email(self, email):
        user = self._users_db.get_by_email(email)

        if not self.can_access_user(user):
            raise AuthorizationError('Cannot get this user')

        return user

    def list(self):
        if not self.can_list_users():
            raise AuthorizationError('Cannot list users')

        return self._users_db.list()

    def create(self, email, password, display_name=None):

        if not self.can_create_user():
            raise AuthorizationError('Cannot create users')

        return self._users_db.create(
            email=email,
            password=password,
            display_name=display_name,
        )

    def update(self, user, display_name=None):

        if not self.can_update_user(user):
            raise AuthorizationError('Cannot update user')

        updates = {}

        if display_name is not None:
            updates['display_name'] = display_name

        self._users_db.update(id=user.id, **updates)

    def set_password(self, user, new_password):

        if not self.can_update_user(user):
            raise AuthorizationError('Cannot update user')

        self._users_db.set_password(id=user.id, password=new_password)

    def delete(self, user):

        if not self.can_delete_user(user):
            raise AuthorizationError('Cannot delete user')

        self._users_db.delete(id=user.id)

    def verify_credentials(self, email, password):
        return self._users_db.verify_credentials(email, password)

    # Authorization --------------------------------------------------

    def can_access_user(self, user):
        auth = self.get_auth_info()
        return auth.is_superuser()

    def can_list_users(self):
        auth = self.get_auth_info()
        return auth.is_superuser()

    def can_create_user(self):
        auth = self.get_auth_info()
        return auth.is_superuser()

    def can_update_user(self, user):
        auth = self.get_auth_info()
        return auth.is_superuser()

    def can_delete_user(self, user):
        auth = self.get_auth_info()
        return auth.is_superuser()
