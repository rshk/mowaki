from pyql import InputObject, Object

from app.core.exceptions import AuthorizationError
from app.core.user import UsersCore

from .base import schema
from .user import User


CreateUserInput = InputObject('CreateUserInput', {
    'email': str,
    'password': str,
    'display_name': str,
})


CreateUserOutput = Object('CreateUserOutput', {
    'ok': bool,
    'user': User,
})


@schema.mutation.field('create_user')
def mut_create_user(root, info, data: CreateUserInput) -> CreateUserOutput:
    core = UsersCore.from_request()

    try:
        uid = core.create(
            email=data.email,
            password=data.password,
            display_name=data.display_name)

    except AuthorizationError:
        return CreateUserOutput(ok=False)

    user = core.get(uid)
    return CreateUserOutput(ok=True, user=user)


UpdateUserInput = InputObject('UpdateUserInput', {
    'email': str,
    'password': str,
    'display_name': str,
})


UpdateUserOutput = Object('UpdateUserOutput', {
    'ok': bool,
    'user': User,
})


@schema.mutation.field('update_user')
def mut_update_user(
        root, info,
        id: int,
        data: UpdateUserInput) -> UpdateUserOutput:
    core = UsersCore.from_request()

    try:
        core.update(
            core.get(id),
            display_name=data.display_name)

    except AuthorizationError:
        return UpdateUserOutput(ok=False)

    # Get + return an updated version of the user
    user = core.get(id)
    return UpdateUserOutput(ok=True, user=user)


DeleteUserOutput = Object('DeleteUserOutput', {
    'ok': bool,
})


@schema.mutation.field('delete_user')
def mut_delete_user(root, info, id: int) -> DeleteUserOutput:
    core = UsersCore.from_request()

    try:
        core.delete(core.get(id))

    except AuthorizationError:
        return DeleteUserOutput(ok=False)

    return DeleteUserOutput(ok=True)
