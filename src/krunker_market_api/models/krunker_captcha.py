import base64
import json
import logging

from altcha_solver import solve_challenge_async
from pydantic import BaseModel
import time
from krunker_market_api.models.messages.krunker_message import KrunkerMessage


class KrunkerCaptcha(BaseModel):
    algorithm: str
    challenge: str
    maxnumber: int
    salt: str
    signature: str

    @classmethod
    def from_message(cls, message: KrunkerMessage) -> 'KrunkerCaptcha':
        return cls(**message.data[0])


class KrunkerCaptchaSolution(BaseModel):
    algorithm: str
    challenge: str
    number: int
    salt: str
    signature: str
    took: int


async def solve_captcha(
        captcha: 'KrunkerCaptcha'
) -> str:
    start_time = time.time()

    result = await solve_challenge_async(
        algorithm=captcha.algorithm,
        challenge=captcha.challenge,
        salt=captcha.salt,
        max=captcha.maxnumber
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    response_data = {
        "algorithm": captcha.algorithm,
        "challenge": captcha.challenge,
        "number": result,
        "salt": captcha.salt,
        "signature": captcha.signature,
        "took": elapsed_ms  # Can probably just make this up but for realism we'll use the actual time
    }

    logging.debug(f"Captcha solved: {response_data}")

    response_json = json.dumps(response_data, separators=(',', ':'))
    response_b64 = base64.b64encode(response_json.encode()).decode()
    return response_b64
