from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from email.message import Message


class BaseMailer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send_message(self, msg: Message):
        pass
