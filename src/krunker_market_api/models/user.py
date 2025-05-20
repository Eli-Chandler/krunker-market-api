from krunker_market_api.models.captcha import KrunkerCaptcha
from krunker_market_api.models.krunker_message import KrunkerMessage


class ClientLoginCaptchaMessage(KrunkerMessage):
    def __init__(self):
        super().__init__(
            "_0",
            [
                0,
                "bCpt",
                "login"
            ]
        )

class ServerLoginCaptchaMessage(KrunkerMessage):
    @property
    def captcha(self):
        return KrunkerCaptcha(
            **self.data[1]
        )

class ClientLoginRequest(KrunkerMessage):
    def __init__(self, email: str, password: str, captcha_solution: str):
        super().__init__(
            'a',
            [
                1,
                [None, password, None, None, None, None, email, None],
                captcha_solution,
                None
            ]
        )
