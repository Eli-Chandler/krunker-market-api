from pydantic import BaseModel
from krunker_market_api.models.krunker_message import KrunkerMessage


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
