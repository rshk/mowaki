import logging

import click
from tabulate import tabulate

from app.core.user import UsersCore

from .base import cli

logger = logging.getLogger(__name__)


@cli.group(name="user")
def grp_user():
    """Manage users"""
    pass


@grp_user.command(name="list")
def cmd_user_list():
    users = UsersCore.for_system().list()
    headers = ["ID", "Email", "Name"]
    table = [
        (
            x.id,
            x.email,
            x.display_name,
        )
        for x in users
    ]

    if not len(table):
        print("No users found")
        return

    print(tabulate(table, headers, tablefmt="psql"))


@grp_user.command(name="create")
@click.argument("email")
@click.option(
    "--password", prompt=True, hide_input=True, confirmation_prompt=True
)
@click.option("--display-name", prompt=True, default="")
def cmd_user_create(email, password, display_name):

    if "@" not in email:
        raise ValueError("Bad email address")

    data = {}

    if display_name is not None:
        data["display_name"] = display_name

    core = UsersCore.for_system()
    uid = core.create(email=email, password=password, **data)

    print("Created user: {}".format(uid))


@grp_user.command(name="update")
@click.argument("id_or_email")
@click.option("--display-name", default=None)
def cmd_user_update(id_or_email, display_name):

    core = UsersCore.for_system()
    user = _require_user_by_id_or_email(id_or_email)
    updates = {}

    if display_name is not None:
        updates["display_name"] = display_name

    core.update(user, **updates)


@grp_user.command(name="set-password")
@click.argument("id_or_email")
@click.option(
    "--password", prompt=True, hide_input=True, confirmation_prompt=True)
def cmd_user_set_password(id_or_email, password):
    core = UsersCore.for_system()
    user = _require_user_by_id_or_email(id_or_email)
    core.set_password(user, password)


@grp_user.command(name="delete")
@click.argument("id_or_email")
def cmd_user_delete(id_or_email):
    core = UsersCore.for_system()
    user = _require_user_by_id_or_email(id_or_email)
    core.delete(user)


def _get_user_by_id_or_email(id_or_email):
    core = UsersCore.for_system()

    if "@" in id_or_email:
        return core.get_by_email(id_or_email)

    return core.get(int(id_or_email))


def _require_user_by_id_or_email(id_or_email):
    user = _get_user_by_id_or_email(id_or_email)
    if user is None:
        raise ValueError("User not found: {}".format(id_or_email))
    return user


@grp_user.command(name="verify-credentials")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_user_verify_credentials(email, password):
    core = UsersCore.for_system()
    user = core.verify_credentials(email, password)

    if not user:
        print('\x1b[31mLogin failed\x1b[0m')
        return

    print('\x1b[32mLogin successful\x1b[0m')
    print('User #{}: {} <{}>'
          .format(user.id, user.display_name, user.email))
