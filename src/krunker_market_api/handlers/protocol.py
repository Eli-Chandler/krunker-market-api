from typing import Protocol
from krunker_market_api.models import KrunkerMessage

class _KrunkerMessageHandler(Protocol):
    async def can_handle_receive(self, message: KrunkerMessage) -> bool:
        """Check if the handler can process the given message."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def can_handle_send(self, message: KrunkerMessage) -> bool:
        """Check if the handler can process the given message."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def handle_receive(self, message: KrunkerMessage):
        """Process the received message and return a response."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def handle_send(self, message: KrunkerMessage):
        """Process the message to be sent and return the modified message."""
        raise NotImplementedError("Subclasses must implement this method.")