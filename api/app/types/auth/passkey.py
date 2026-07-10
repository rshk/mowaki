from pydantic import BaseModel


class PasskeyData(BaseModel):
    passkey_id: str
    pass
