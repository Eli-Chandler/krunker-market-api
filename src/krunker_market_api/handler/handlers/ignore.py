from krunker_market_api.handler.protocol import _KrunkerMessageHandlerProtocol
from krunker_market_api.models import KrunkerMessage


class _IgnoreHandler(_KrunkerMessageHandlerProtocol):
    _MESSAGE_TYPES = ['cntry', 'news']

    async def can_handle_receive(self, message: KrunkerMessage) -> bool:
        return message.message_type in self._MESSAGE_TYPES

    async def can_handle_send(self, message: KrunkerMessage) -> bool:
        return False

    async def handle_receive(self, message: KrunkerMessage):
        if not await self.can_handle_receive(message):
            raise ValueError("This handler cannot process the given message.")

        # Do nothing

    async def handle_send(self, message: KrunkerMessage):
        if not await self.can_handle_send(message):
            raise ValueError("This handler cannot process the given message.")


