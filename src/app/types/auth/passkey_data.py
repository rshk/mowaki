from __future__ import annotations

import uuid
from typing import NewType

from pydantic import BaseModel

PasskeyID = NewType("PasskeyID", uuid.UUID)


class PasskeyData(BaseModel):
    credential_id: PasskeyID
    public_key: str
    sign_count: int
