from sqlalchemy import literal, text
from sqlalchemy.dialects import postgresql


def test_sql_with_quoted_name():
    dialect = postgresql.dialect()
    query = text("""CREATE DATABASE :dbname ENCODING :encoding""").bindparams(
        dbname=(
            dialect.preparer(dialect).quote_identifier('some "database" name')
        ),
        encoding="utf8",
    )
    compiled = query.compile(dialect=dialect, compile_kwargs={"literal_binds": True}).string
    assert compiled == ""

    pass
    # query = text("""CREATE DATABASE :name""").bindparams(name=quoted_name('foo "and" bar', True))
    # compiled = query.compile(dialect=dialect())
    # assert (compiled.string % compiled.params) == "CREATE DATABASE foo"
