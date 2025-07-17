from krunker_market_api.models.captcha import KrunkerCaptcha
from krunker_market_api.models.krunker_message import KrunkerMessage, KrunkerRequest

from dataclasses import dataclass


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

class LoginRequest(KrunkerRequest["LoginResponse"]):
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
    def response_type(self) -> type["LoginResponse"]:
        return LoginResponse

class LoginResponse(KrunkerMessage):
    @property
    def id(self) -> int:
        return self.data[1]

    @property
    def username(self) -> str:
        return self.data[2]


@dataclass(frozen=True)
class LoggedInDetails:
    username: str
    id: int

    @classmethod
    def from_message(cls, message: "LoginResponse") -> "LoggedInDetails":
        return cls(message.username, message.id)

class LoginResultResponse(KrunkerMessage):
    @property
    def success(self) -> bool:
        return self.data[1]