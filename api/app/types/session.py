from typing import NewType

from pydantic import BaseModel


SessionID = NewType("SessionID", str)


class Session(BaseModel):
    pass
