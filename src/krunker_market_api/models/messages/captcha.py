from krunker_market_api.models.krunker_captcha import KrunkerCaptcha
from krunker_market_api.models.messages.krunker_message import KrunkerMessage


class ServerCaptchaMessage(KrunkerMessage):
    @property
    def captcha(self) -> KrunkerCaptcha:
        return KrunkerCaptcha(**self.data[0])

class ClientCaptchaSolutionMessage(KrunkerMessage):
    def __init__(self, solution: str):
        super().__init__('cptR', [solution])

class ServerCaptchaResultMessage(KrunkerMessage):
    @property
    def success(self) -> bool:
        return self.data[0]