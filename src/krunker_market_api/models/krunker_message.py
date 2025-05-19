import msgpack
from typing import List

class KrunkerMessage:
    message_type: str | int
    data: List[str | int | dict] | None


    def __init__(self, message_type: str | int, data: List[str | int | dict] | None = None):
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

    @staticmethod
    def from_bytes(data: bytes) -> 'KrunkerMessage':
        message = msgpack.unpackb(data[:-2])
        return KrunkerMessage(message[0], message[1:])

    def to_bytes(self) -> bytes:
        encoded_message = msgpack.packb([self.message_type] + self.data) + b'\x00\x00'
        return encoded_message

