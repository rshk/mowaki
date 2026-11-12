from abc import abstractmethod
from typing import Protocol


class LoginSideFx(Protocol):
    """Dependencies of the login flow which may cause side effects"""

    @abstractmethod
    async def compose_and_sed_otp_challenge_email(self, email: str, code: str):
        pass

    @abstractmethod
    async def add_email_verification_session_assertion(self, email: str):
        pass

    @abstractmethod
    def generate_otp(length: int = 6) -> str:
        pass
