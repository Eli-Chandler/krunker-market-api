from krunker_market_api.handler.protocol import _KrunkerMessageHandlerProtocol
from krunker_market_api.models import KrunkerMessage
from altcha_solver import solve_challenge_async
from typing import Callable, Awaitable, Optional
import logging
from collections import deque



class _PingHandler(_KrunkerMessageHandlerProtocol):
    _PING_MESSAGE_TYPES = ['pi', 'pir']

    def __init__(self,
                 send_message: Callable[[KrunkerMessage], Awaitable[None]]
                 ):
        self._send_message = send_message
        self._recent_pings = deque(maxlen=10)

    @property
    def ping(self) -> Optional[float]:
        if len(self._recent_pings) == 0:
            return None
        return sum(self._recent_pings) / len(self._recent_pings)

    async def can_handle_receive(self, message: KrunkerMessage) -> bool:
        return message.message_type in self._PING_MESSAGE_TYPES

    async def can_handle_send(self, message: KrunkerMessage) -> bool:
        return False

    async def handle_receive(self, message: KrunkerMessage):
        if not await self.can_handle_receive(message):
            raise ValueError("This handler cannot process the given message.")

        if message.message_type in 'pir':
            # pir: [127]
            self._recent_pings.append(message.data[0])

        await self._send_message(KrunkerMessage('po'))

    async def handle_send(self, message: KrunkerMessage):
        raise ValueError("This handler does not send messages.")