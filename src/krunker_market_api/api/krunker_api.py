import asyncio
from collections import deque

from krunker_market_api.websocket.krunker_subscription_manager import KrunkerSubscriptionManager
from krunker_market_api.websocket.krunker_websocket import KrunkerWebSocket
from krunker_market_api.models.captcha import *
from krunker_market_api.models.user import *
from krunker_market_api.models.item import *
from krunker_market_api.models.ping import *

import aiohttp

from dataclasses import dataclass


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
        krunker_credentials = await _krunker_http_login(email, password)
        # It gives a separate response message that is true/false, subscribe ahead of time
        login_result_message_task = asyncio.create_task(self._sub.subscribe(lambda msg: msg.message_type == "_0", 10, ServerLoginResultMessage))

        await self._sub.request(
            LoginRequest(krunker_credentials.access_token))

        login_result_message = await login_result_message_task
        if not login_result_message.success:
            raise RuntimeError("Login failed")


    async def get_item_market_info(self, item_id: int) -> ItemMarketInfo:
        result = await self._sub.request(MarketInfoRequest(item_id))

        return ItemMarketInfo.from_krunker_message(result)

    async def get_item_sales_history(self, item_id: int) -> List[ItemSalesDay]:
        result = await self._sub.request(ItemSalesHistoryRequest(item_id), timeout=15)
        return ItemSalesDay.from_krunker_message(result)

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

            captcha_result = await self._sub.request(CaptchaSolutionRequest(solution))

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


@dataclass(frozen=True)
class KrunkerLoginResult:
    access_token: str
    login_token: str
    refresh_token: str

async def _krunker_http_login(user: str, password: str):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://krunker.io',
        'priority': 'u=1, i',
        'referer': 'https://krunker.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    json_data = {
        'email': user,
        'password': password,
    }

    async with aiohttp.ClientSession() as session:
        response = await session.post('https://gapi.svc.krunker.io/auth/login/email', headers=headers, json=json_data)
        if response.status != 200:
            raise RuntimeError(f"Login failed, status code: {response.status} {await response.text()}")

        j = await response.json()

    return KrunkerLoginResult(
        access_token=j['data']['access_token'],
        login_token=j['data']['login_token'],
        refresh_token=j['data']['refresh_token'],
    )