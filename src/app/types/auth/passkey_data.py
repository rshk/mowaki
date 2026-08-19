from __future__ import annotations

from typing import NewType

from pydantic import BaseModel

PasskeyID = NewType("PasskeyID", str)


class PasskeyData(BaseModel):
    credential_id: PasskeyID
    public_key: str
    sign_count: int
