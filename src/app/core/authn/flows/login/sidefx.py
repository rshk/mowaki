from abc import abstractmethod
from typing import Protocol

from .utils import (
    compose_and_send_otp_challenge_email,
    do_add_session_assertion,
    generate_otp,
)


class LoginSideFxProto(Protocol):
    """Dependencies of the login flow which may cause side effects"""

    @abstractmethod
    async def compose_and_sed_otp_challenge_email(self, email: str, code: str):
        pass

    @abstractmethod
    async def add_email_verification_session_assertion(self, email: str):
        pass

    @abstractmethod
    def generate_otp(self, length: int = 6) -> str:
        pass


class LoginSideFx(LoginSideFxProto):
    async def compose_and_sed_otp_challenge_email(self, email: str, code: str):
        return await compose_and_send_otp_challenge_email(email, code)

    async def add_email_verification_session_assertion(self, email: str):
        return await do_add_session_assertion(email)

    def generate_otp(self, length: int = 6) -> str:
        return generate_otp(length=length)
