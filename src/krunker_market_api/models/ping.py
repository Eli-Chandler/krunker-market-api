from krunker_market_api.models.krunker_message import KrunkerMessage


class ClientPongMessage(KrunkerMessage):
    def __init__(self):
        super().__init__(
            "po"
        )


class ServerPingMessage(KrunkerMessage):
    pass


class ServerPingWithLatencyMessage(KrunkerMessage):
    @property
    def latency(self) -> int:
        return self.data[0]
