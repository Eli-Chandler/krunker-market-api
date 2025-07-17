from krunker_market_api.models.captcha import KrunkerCaptcha
from krunker_market_api.models.krunker_message import KrunkerMessage, KrunkerRequest, T


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
#
#
# class ClientLoginRequest(KrunkerMessage):
#     def __init__(self, email: str, password: str, captcha_solution: str):
#         super().__init__(
#             'a',
#             [
#                 1,
#                 [None, password, None, None, None, None, email, None],
#                 captcha_solution,
#                 None
#             ]
#         )

# [
#     "_0",
#     0,
#     "login",
#     "eJ..."
# ]

class LoginRequest(KrunkerRequest):
    def __init__(self, login_token: str):
        super().__init__(
            message_type="_0",
            data=[
                0, "login", login_token
            ]
        )

    def matches(self, message: "KrunkerMessage") -> bool:
        return message.message_type == "a" and len(message.data) >= 1 and message.data[0] == 0

    @property
    def response_type(self) -> type[None]:
        return None


class ServerLoginResultMessage(KrunkerMessage):
    @property
    def success(self) -> bool:
        return self.data[1]