from krunker_market_api.handlers.protocol import _KrunkerMessageHandler
from krunker_market_api.models import KrunkerMessage
from altcha_solver import solve_challenge_async
from pydantic import BaseModel
from typing import Callable, Awaitable, Tuple
import base64
import json
import time
import logging

from krunker_market_api.models.krunker_captcha import KrunkerCaptchaSolution, KrunkerCaptcha


class _CaptchaHandler(_KrunkerMessageHandler):
    CAPTCHA_MESSAGE_TYPE = 'cpt'

    def __init__(self,
                 send_message: Callable[[KrunkerMessage], Awaitable[None]],
                 solve_captcha: Callable[[KrunkerCaptcha], Awaitable[KrunkerCaptchaSolution]]
                 ):
        self._send_message = send_message
        self._solve_captcha = solve_captcha

    async def can_handle_receive(self, message: KrunkerMessage) -> bool:
        return message.message_type == self.CAPTCHA_MESSAGE_TYPE

    async def can_handle_send(self, message: KrunkerMessage) -> bool:
        return False

    async def handle_receive(self, message: KrunkerMessage):
        if not await self.can_handle_receive(message):
            raise ValueError("This handler cannot process the given message.")

        captcha_message = KrunkerCaptcha.from_message(message)
        solution = await self._solve_captcha(captcha_message)

        response_data = {
            "algorithm": solution.algorithm,
            "challenge": solution.challenge,
            "number": solution.number,
            "salt": solution.salt,
            "signature": solution.signature,
            "took": solution.took  # Can probably just make this up but for realism we'll use the actual time
        }

        response_json = json.dumps(response_data, separators=(',', ':'))
        response_b64 = base64.b64encode(response_json.encode()).decode()

        await self._send_message(KrunkerMessage('cptR', [response_b64]))

    async def handle_send(self, message: KrunkerMessage):
        raise ValueError("This handler does not send messages.")

async def solve_captcha(
        captcha: 'KrunkerCaptcha'
) -> 'KrunkerCaptchaSolution':
    start_time = time.time()

    result = await solve_challenge_async(
        algorithm=captcha.algorithm,
        challenge=captcha.challenge,
        salt=captcha.salt,
        max=captcha.maxnumber
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    return KrunkerCaptchaSolution(
        algorithm=captcha.algorithm,
        challenge=captcha.challenge,
        number=result,
        salt=captcha.salt,
        signature=captcha.signature,
        took=elapsed_ms
    )


