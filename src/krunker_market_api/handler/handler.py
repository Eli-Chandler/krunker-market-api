from krunker_market_api.handler.protocol import _KrunkerMessageHandlerProtocol
from krunker_market_api.handler.handlers import _CaptchaHandler, _PingHandler, _IgnoreHandler
from krunker_market_api.models import KrunkerMessage
from typing import List, Callable, Awaitable
import asyncio

class MultipleHandlersMatchError(Exception):
    """Raised when more than one handler claims it can handle the same message."""
    pass

class NoHandlerFoundError(Exception):
    """Raised when no handler is found for a given message."""
    pass

class KrunkerMessageHandler(_KrunkerMessageHandlerProtocol):
    _handlers: List[_KrunkerMessageHandlerProtocol]
    def __init__(self, send_message: Callable[[KrunkerMessage], Awaitable[None]]):
        self._ping_handler = _PingHandler(send_message)

        self._handlers = [
            _CaptchaHandler(send_message, None),
            self._ping_handler,
            _IgnoreHandler()
        ]

    @property
    def ping(self):
        return self._ping_handler.ping


    async def can_handle_receive(self, message: KrunkerMessage) -> bool:
        can_handle = await asyncio.gather(
            *[asyncio.create_task(handler.can_handle_receive(message)) for handler in self._handlers]
        )
        if can_handle.count(True) > 1:
            raise MultipleHandlersMatchError(f"Multiple handlers claim to be able to receive message: {message}")
        return any(can_handle)


    async def can_handle_send(self, message: KrunkerMessage) -> bool:
        can_handle = await asyncio.gather(
            *[asyncio.create_task(handler.can_handle_send(message)) for handler in self._handlers]
        )
        if can_handle.count(True) > 1:
            raise MultipleHandlersMatchError(f"Multiple handlers claim to be able to send message: {message}")
        return any(can_handle)

    async def handle_receive(self, message: KrunkerMessage):
        can_handle = await asyncio.gather(
            *[asyncio.create_task(handler.can_handle_receive(message)) for handler in self._handlers]
        )

        if not any(can_handle):
            raise NoHandlerFoundError(f"No receive handler found for message: {message}")

        index = can_handle.index(True)
        await self._handlers[index].handle_receive(message)


    async def handle_send(self, message: KrunkerMessage):
        can_handle = await asyncio.gather(
            *[asyncio.create_task(handler.can_handle_send(message)) for handler in self._handlers]
        )

        if not any(can_handle):
            raise NoHandlerFoundError(f"No send handler found for message: {message}")

        index = can_handle.index(True)
        await self._handlers[index].handle_send(message)