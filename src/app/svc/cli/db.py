import click

from app.config import get_config_from_env
from app.exceptions import DevFeatureDisabled
from app.lib.sql.utils import create_async_engine
from app.repo._schema import metadata

from ._utils import run_sync


@click.group(name="db")
def grp_db():
    """Database related operations"""


@grp_db.command(name="create-schema")
@click.option(
    "--recreate", is_flag=True, default=False, help="Drop and recreate schema"
)
@run_sync
async def cmd_db_create_schema(recreate: bool):
    """Create database schema (development only)"""

    cfg = get_config_from_env()
    if cfg.development_mode is not True:
        raise DevFeatureDisabled(
            'The "create schema" command can only be used for development. '
            "For production, use migrations instead (via alembic)."
        )

    engine = create_async_engine(str(cfg.database_url))
    async with engine.begin() as conn:
        if recreate:
            await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


@grp_db.command(name="drop-schema")
@run_sync
async def cmd_db_drop_schema():
    """Drop database schema (development only)"""

    cfg = get_config_from_env()
    if cfg.development_mode is not True:
        raise DevFeatureDisabled(
            'The "drop schema" command can only be used for development. '
            "For production, use migrations instead (via alembic)."
        )

    engine = create_async_engine(str(cfg.database_url))
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@grp_db.command(name="show-schema")
@run_sync
async def cmd_db_show_schema():
    """Show database schema that would be created"""

    # Use a mock engine strategy that prints everything to a custom function
    def dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))

    # Create an engine with the mock executor
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://", strategy="mock", executor=dump)

    # This will print the entire schema creation script without touching a real database
    metadata.create_all(engine)
