from typing import List, TypeVar, Generic
import msgpack
from abc import ABC, abstractmethod


class KrunkerMessage:
    message_type: str | int
    data: List[str | int | dict | bool | None | list] | None

    def __init__(self, message_type: str | int, data: List[str | int | dict | bool | None | list] | None = None):
        if data is None:
            data = []

        self.message_type = message_type
        self.data = data

    def __repr__(self) -> str:
        return f'Message(event={self.message_type}, data={self.data})'

    def __str__(self) -> str:
        return f'{self.message_type}: {self.data}'

    def __eq__(self, other) -> bool:
        return self.message_type == other.message_type and self.data == other.data

    @classmethod
    def from_bytes(cls, data: bytes):
        message = msgpack.unpackb(data[:-2])
        return cls(message[0], message[1:])

    @classmethod
    def from_message(cls, message: 'KrunkerMessage'):
        return cls(message.message_type, message.data)

    def to_bytes(self) -> bytes:
        encoded_message = msgpack.packb([self.message_type] + self.data) + b'\x00\x00'
        return encoded_message


T = TypeVar("T", bound=KrunkerMessage)

class KrunkerRequest(ABC, KrunkerMessage, Generic[T]):
    @abstractmethod
    def matches(self, message: KrunkerMessage) -> bool:
        pass

    @property
    @abstractmethod
    def response_type(self) -> type[T]:
        pass
