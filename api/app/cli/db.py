import click


from app.cli._utils import run_sync
from app.config import get_config_from_env
from app.lib.database.utils import create_async_engine
from app.repo._schema import metadata


@click.group(name="db")
def grp_db():
    """Database related operations"""
    pass


@grp_db.command(name="create-schema")
@click.option("--recreate", is_flag=True, default=False, help="Drop and recreate schema")
@run_sync
async def cmd_db_create_schema(recreate: bool):
    """Create database schema (development only)"""

    cfg = get_config_from_env()
    if cfg.development_mode is not True:
        raise Exception(
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
        raise Exception(
            'The "drop schema" command can only be used for development. '
            "For production, use migrations instead (via alembic)."
        )

    engine = create_async_engine(str(cfg.database_url))
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
