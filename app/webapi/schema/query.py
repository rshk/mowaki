import strawberry

from .query__hello import resolve_hello
from .query__user import resolve_query_user


@strawberry.type
class Query:
    hello = strawberry.field(resolver=resolve_hello)
    user = strawberry.field(resolver=resolve_query_user)
