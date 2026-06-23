from __future__ import annotations

from pydantic import BaseModel


class And[SubExpr](BaseModel):
    terms: list[SubExpr | Combinator]


class Or[SubExpr](BaseModel):
    terms: list[SubExpr | Combinator]


class Not[SubExpr](BaseModel):
    term: SubExpr | Combinator


type Combinator = And | Or | Not
type Expr[T] = Combinator | T
