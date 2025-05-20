import asyncio
import websockets
import logging
from typing import Optional

from krunker_market_api.handler.handler import KrunkerMessageHandler
from krunker_market_api.models import KrunkerMessage

# lets make this simpler with just a send_subscribe method
class KrunkerWebSocket:
    def __init__(self):
        self._message_handler = KrunkerMessageHandler(self._send)
        self._connected_event = asyncio.Event()
        self._ws: Optional[websockets.ClientConnection] = None
        self._ws_lock = asyncio.Lock()

    async def start(self):
        async with self._ws_lock:
            if self._ws is not None:
                raise RuntimeError("Websocket already running")

            asyncio.create_task(self._receive())
            await self._connected_event.wait()


    async def _receive(self):
            async with websockets.connect(
                'wss://social.krunker.io/ws?',
                ping_interval=None,
                origin=websockets.Origin('https://krunker.io')
            ) as ws:
                logging.info("Krunker websocket connected")
                self._ws = ws
                self._connected_event.set()
                async for message in ws:
                    krunker_message = KrunkerMessage.from_bytes(message)

                    if await self._message_handler.can_handle_receive(krunker_message):
                        logging.info(f'HANDLING: {krunker_message}')
                        await self._message_handler.handle_receive(krunker_message)
                    else:
                        logging.warning(f'NO HANDLER: {krunker_message}')

    async def close(self):
        async with self._ws_lock:
            if self._ws is None:
                raise RuntimeError("Websocket already closed")

            await self._ws.close()
            self._ws = None