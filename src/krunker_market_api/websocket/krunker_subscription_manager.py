import logging
from collections.abc import Callable
from typing import Optional, List, TypeVar
from dataclasses import dataclass
import asyncio

from krunker_market_api.models.krunker_message import KrunkerMessage
from krunker_market_api.websocket.krunker_websocket import KrunkerWebSocket
from typing import Type


def color(text, code):
    return f"\033[{code}m{text}\033[0m"


@dataclass
class _Subscription:
    matcher: Callable[[KrunkerMessage], bool]
    future: asyncio.Future[KrunkerMessage]


T = TypeVar('T', bound='KrunkerMessage')


class KrunkerSubscriptionManager:
    def __init__(self, krunker_web_socket: KrunkerWebSocket):
        self._krunker_web_socket = krunker_web_socket
        self._subscriptions: List[_Subscription] = []

    async def ready(self):
        # Wait for the websocket to be ready
        await self._krunker_web_socket.ready()

    def start(self):
        asyncio.create_task(self._receive_loop())

    async def send(self, message: KrunkerMessage):
        logging.info(color(f"[->] {message}", '35'))
        await self._krunker_web_socket.send(message)

    async def subscribe(self,
                        response_matcher: Callable[[KrunkerMessage], bool],
                        timeout: Optional[int] = 10,
                        response_type: Type[T] = KrunkerMessage
                        ) -> Optional[T]:

        loop = asyncio.get_event_loop()
        future: asyncio.Future[KrunkerMessage] = loop.create_future()
        sub = _Subscription(matcher=response_matcher, future=future)
        self._subscriptions.append(sub)

        try:
            response = await asyncio.wait_for(future, timeout)
            if response_type:
                return response_type.from_message(response)
            return response  # Type: KrunkerMessage
        finally:
            if sub in self._subscriptions:
                self._subscriptions.remove(sub)

    async def send_subscribe(self,
                             message: KrunkerMessage,
                             response_matcher: Callable[[KrunkerMessage], bool],
                             timeout: int = 10,
                             response_type: Type[T] = KrunkerMessage) -> Optional[T]:
        subscription = self.subscribe(response_matcher, timeout,
                                      response_type=response_type)  # Subscribe just before sending
        await self.send(message)
        return await subscription

    async def _receive_loop(self):
        async with self._krunker_web_socket as ws:
            async for msg in ws:
                # dispatch to all subscriptions
                handled = False
                for sub in list(self._subscriptions):
                    if not sub.future.done() and sub.matcher(msg):
                        handled = True
                        sub.future.set_result(msg)
                        self._subscriptions.remove(sub)

                if not handled:
                    logging.warning(f"Received message without matching subscription: {msg}")
                else:
                    logging.info(color(f"[<-]: {msg}", '34'))
