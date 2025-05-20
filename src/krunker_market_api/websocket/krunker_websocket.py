import asyncio
import logging
from contextlib import suppress
from typing import AsyncIterator, Optional

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from krunker_market_api.models.messages.krunker_message import KrunkerMessage


class KrunkerWebSocket:
    def __init__(
        self,
        uri: str = "wss://social.krunker.io/ws?",
        origin: str = "https://krunker.io"
    ):
        self._uri = uri
        self._origin = origin
        self._ws: Optional[websockets.ClientConnection] = None
        self._ws_event = asyncio.Event()
        self._recv_queue: asyncio.Queue[KrunkerMessage] = asyncio.Queue()
        self._recv_task: Optional[asyncio.Task] = None
        self._send_lock = asyncio.Lock()

    async def ready(self):
        await self._ws_event.wait()

    async def connect(self) -> None:
        logging.info("Connecting to websocket...")
        if self._ws is not None:
            raise RuntimeError("WebSocket already connected")
        self._ws = await websockets.connect(
            self._uri,
            ping_interval=None,
            origin=websockets.Origin(self._origin),
            
        )
        logging.info("Krunker websocket connected")
        self._ws_event.set()
        # spawn the background reader
        self._recv_task = asyncio.create_task(self._reader())

    async def _reader(self) -> None:
        assert self._ws is not None
        try:
            async for message in self._ws:
                krunker_message = KrunkerMessage.from_bytes(message)
                await self._recv_queue.put(krunker_message)
        except (ConnectionClosedOK, ConnectionClosedError) as e:
            logging.warning(f"WebSocket closed: {e}")
        finally:
            # ensure clean shutdown
            await self.close()

    async def send(self, message: KrunkerMessage) -> None:
        if self._ws is None:
            raise RuntimeError("WebSocket is not connected")
        async with self._send_lock:
            await self._ws.send(message.to_bytes())

    async def receive(self) -> KrunkerMessage:
        """
        Await the next incoming message.
        """
        if self._ws is None:
            raise RuntimeError("WebSocket is not connected")
        return await self._recv_queue.get()

    async def close(self) -> None:
        # close the socket
        if self._ws is not None:
            await self._ws.close()
        self._ws = None

        # cancel the reader task
        if self._recv_task:
            self._recv_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._recv_task
            self._recv_task = None

        logging.info("Krunker websocket closed")

    # support async context manager
    async def __aenter__(self) -> "KrunkerWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[KrunkerMessage]:
        return self

    async def __anext__(self) -> KrunkerMessage:
        try:
            return await self.receive()
        except RuntimeError:
            raise StopAsyncIteration
