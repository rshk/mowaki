from dataclasses import dataclass
from datetime import datetime
from typing import NewType

UserID = NewType("UserID", int)


@dataclass
class User:
    id: UserID
    email: str
    date_created: datetime
