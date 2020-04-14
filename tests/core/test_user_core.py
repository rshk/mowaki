import pytest

from app.core.exceptions import AuthorizationError
from app.core.user import UsersCore

pytestmark = pytest.mark.usefixtures('db')


class Test_system:

    @pytest.fixture
    def core(self):
        return UsersCore.for_system()

    def test_create_and_retrieve_user(self, core):
        uid = core.create(
            email='foo@example.com',
            password='password',
            display_name='Foo Bar')

        assert uid is not None
        assert isinstance(uid, int)

        user = core.get(uid)

        assert user is not None
        assert user.id == uid
        assert user.email == 'foo@example.com'
        assert user.display_name == 'Foo Bar'
        assert not user.is_superuser
        assert not user.can_admin_users
        assert not user.can_admin_trips

    def test_get_user_by_email(self, core):
        uid = core.create(email='foo@example.com', password='password')
        user = core.get_by_email('foo@example.com')
        assert user is not None
        assert user.id == uid

    def test_get_empty_user_list(self, core):
        assert list(core.list()) == []

    def test_create_and_list_user(self, core):
        uid = core.create(
            email='foo@example.com',
            password='password',
            display_name='Foo Bar')
        users = list(core.list())

        assert len(users) == 1
        assert users[0].id == uid
        assert users[0].email == 'foo@example.com'

    def test_created_user_can_authenticate(self, core):
        uid = core.create(email='foo@example.com', password='password')
        user = core.verify_credentials('foo@example.com', 'password')
        assert user is not None
        assert user.id == uid

    def test_bad_email_will_return_none(self, core):
        core.create(email='foo@example.com', password='password')
        user = core.verify_credentials('BAD-EMAIL@example.com', 'password')
        assert user is None

    def test_bad_password_will_return_none(self, core):
        core.create(email='foo@example.com', password='password')
        user = core.verify_credentials('foo@example.com', 'BAD PASSWORD')
        assert user is None

    def test_can_change_user_password(self, core):
        uid = core.create(email='foo@example.com', password='password')
        core.set_password(core.get(uid), 'new password')

        user = core.verify_credentials('foo@example.com', 'password')
        assert user is None

        user = core.verify_credentials('foo@example.com', 'new password')
        assert user is not None
        assert user.id == uid

    def test_can_update_user_display_name(self, core):
        uid = core.create(email='foo@example.com', password='p',
                          display_name='Old Name')
        core.update(core.get(uid), display_name='New Name')
        assert core.get(uid).display_name == 'New Name'


class Test_superuser:

    @pytest.fixture
    def user(self):
        core = UsersCore.for_system()
        uid = core.create(
            email='self@example.com',
            password='password',
            is_superuser=True)
        return core.get(uid)

    @pytest.fixture
    def core(self, user):
        return UsersCore.for_user(user)

    def test_can_create_superuser(self, core):
        uid = core.create(
            email='foo@example.com',
            password='p',
            is_superuser=True)

        user = core.get(uid)
        assert user.is_superuser is True

    def test_can_promote_superuser(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(email='foo@example.com', password='p')
        core.update(core.get(uid), is_superuser=True)
        user = _uc.get(uid)
        assert user.is_superuser is True

    def test_can_demote_superuser(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(email='foo@example.com', password='p',
                         is_superuser=True)
        core.update(core.get(uid), is_superuser=False)
        user = _uc.get(uid)
        assert user.is_superuser is False


class Test_user_admin:

    @pytest.fixture
    def user(self):
        core = UsersCore.for_system()
        uid = core.create(
            email='self@example.com',
            password='password',
            can_admin_users=True)
        return core.get(uid)

    @pytest.fixture
    def core(self, user):
        return UsersCore.for_user(user)

    def test_cannot_create_superuser(self, core):
        uid = core.create(
            email='foo@example.com',
            password='p',
            is_superuser=True)

        user = core.get(uid)
        assert user.is_superuser is False

    def test_cannot_update_superuser(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(
            email='foo@example.com',
            password='p',
            is_superuser=True)

        with pytest.raises(AuthorizationError):
            core.update(core.get(uid), display_name='A different name')

        assert _uc.get(uid).is_superuser is True

    def test_cannot_promote_superuser(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(email='foo@example.com', password='p')
        core.update(core.get(uid), is_superuser=True)
        user = _uc.get(uid)
        assert user.is_superuser is False

    def test_cannot_demote_superuser(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(
            email='foo@example.com',
            password='p',
            is_superuser=True)

        with pytest.raises(AuthorizationError):
            core.update(core.get(uid), is_superuser=False)

        assert _uc.get(uid).is_superuser is True

    def test_can_change_user_password(self, core):
        uid = core.create(email='foo@example.com', password='password')
        core.set_password(core.get(uid), 'new password')

        # Old password is no longer valid
        user = core.verify_credentials('foo@example.com', 'password')
        assert user is None

        # New password is valid
        user = core.verify_credentials('foo@example.com', 'new password')
        assert user is not None
        assert user.id == uid

    def test_cannot_change_superuser_password(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(
            email='foo@example.com',
            password='password',
            is_superuser=True)

        with pytest.raises(AuthorizationError):
            core.set_password(core.get(uid), 'new password')

        # Old password is still valid
        user = core.verify_credentials('foo@example.com', 'password')
        assert user is not None


class Test_normal_user:

    @pytest.fixture
    def user(self):
        core = UsersCore.for_system()
        uid = core.create(
            email='self@example.com',
            password='password')
        return core.get(uid)

    @pytest.fixture
    def core(self, user):
        return UsersCore.for_user(user)


class Test_anonymous:

    @pytest.fixture
    def core(self):
        return UsersCore.for_anonymous()

    def test_anonymous_cannot_create_user(self, core):
        with pytest.raises(AuthorizationError):
            core.create(email='foo@example.com', password='p')

    def test_anonymous_cannot_get_user(self, core):
        uid = UsersCore.for_system().create(
            email='foo@example.com',
            password='p')

        with pytest.raises(AuthorizationError):
            core.get(uid)

    def test_anonymous_cannot_list_users(self, core):
        with pytest.raises(AuthorizationError):
            core.list()

    def test_anonymous_cannot_update_user(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(
            email='a@example.com',
            password='p',
            display_name='OLD NAME')
        with pytest.raises(AuthorizationError):
            core.update(uid, display_name='NEW NAME')
        assert _uc.get(uid).display_name == 'OLD NAME'

    def test_anonymous_cannot_delete_user(self, core):
        _uc = UsersCore.for_system()
        uid = _uc.create(
            email='a@example.com',
            password='p')

        with pytest.raises(AuthorizationError):
            core.delete(uid)

        assert _uc.get(uid) is not None
