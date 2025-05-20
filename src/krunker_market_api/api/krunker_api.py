import asyncio
from collections import deque

from krunker_market_api.websocket.krunker_subscription_manager import KrunkerSubscriptionManager
from krunker_market_api.websocket.krunker_websocket import KrunkerWebSocket
from krunker_market_api.models.krunker_captcha import solve_captcha
from krunker_market_api.models.messages.user import *
from krunker_market_api.models.messages.captcha import *
from krunker_market_api.models.messages.ping import *


class KrunkerApi:
    def __init__(self):
        self._sub = KrunkerSubscriptionManager(KrunkerWebSocket())
        self._recent_pings = deque(maxlen=10)

        # Start all the background handlers
        asyncio.create_task(self._handle_ignored_messages())
        asyncio.create_task(self._handle_ping())
        asyncio.create_task(self._handle_captcha())
        asyncio.create_task(self._handle_connection_error())

        # Start the websocket
        self._sub.start()

    async def ready(self):
        await self._sub.ready()

    async def login(self, email: str, password: str):
        message = await self._sub.send_subscribe(
            ClientLoginCaptchaMessage(),
            lambda msg: msg.message_type == "_0" and msg.data[0] == 0,
            timeout=10,
            response_type=ServerLoginCaptchaMessage
        )

        solution = await solve_captcha(message.captcha)

        await self._sub.send_subscribe(
            ClientLoginRequest(email, password, solution),
            lambda msg: msg.message_type == "a" and msg.data[0] == 0,
            timeout=10
        )

    def ping(self) -> float:
        """Returns the average ping in ms."""
        if not self._recent_pings:
            return 0.0
        return sum(self._recent_pings) / len(self._recent_pings)

    async def _handle_captcha(self):
        while True:
            message = await self._sub.subscribe(
                lambda msg: msg.message_type == 'cpt',
                timeout=None,
                response_type=ServerCaptchaMessage
            )

            solution = await solve_captcha(message.captcha)

            captcha_result = await self._sub.send_subscribe(
                ClientCaptchaSolutionMessage(solution),
                lambda msg: msg.message_type == 'cptR',
                timeout=10,
                response_type=ServerCaptchaResultMessage
            )

            if not captcha_result.success:
                raise RuntimeError("Captcha solution failed")

    async def _handle_connection_error(self):
        await self._sub.subscribe(
            lambda msg: msg.message_type == 'error' and msg.data[0] == 'CON ERROR 3',
            None
        )
        raise RuntimeError("Connection error 3")

    async def _handle_ignored_messages(self):
        ignored_message_types = ['cntry', 'news']

        async def ignore_message(message_type):
            while True:
                await self._sub.subscribe(
                    lambda msg: msg.message_type == message_type,
                    timeout=None)

        await asyncio.gather(
            *[ignore_message(message_type) for message_type in ignored_message_types]
        )

    async def _handle_ping(self):
        async def handle_regular_ping():
            while True:
                await self._sub.subscribe(
                    lambda msg: msg.message_type == 'pi',
                    timeout=30,
                    response_type=ServerPingMessage
                )
                await self._sub.send(ClientPongMessage())

        async def handle_latency_ping():
            while True:
                response = await self._sub.subscribe(
                    lambda msg: msg.message_type == 'pir',
                    timeout=30,
                    response_type=ServerPingWithLatencyMessage
                )
                self._recent_pings.append(response.latency)
                await self._sub.send(ClientPongMessage())

        await asyncio.gather(
            handle_regular_ping(),
            handle_latency_ping()
        )
