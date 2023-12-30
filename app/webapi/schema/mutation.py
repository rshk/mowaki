import strawberry

from .mut__login import resolve_mut_login
from .mut__signup import resolve_mut_signup


@strawberry.type
class Mutation:
    signup = strawberry.mutation(resolver=resolve_mut_signup)
    login = strawberry.mutation(resolver=resolve_mut_login)
