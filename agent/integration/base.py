from typing import Any

from agent.bus.bus import MessageBus
from agent.bus.events import OutMessage, InMessage


class BaseChannel:

    name: str = "base"

    def __init__(self, config: Any, bus: MessageBus):
        self.config = config
        self.bus = bus


    def send(self, msg: OutMessage) -> None:
        """
        Send a message through this channel.
        """
        pass

    def _handle_message(
            self,
            chat_id: str,
            content: str,
            metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Handle an incoming message from the chat platform.
        """
        meta = metadata or {}

        msg = InMessage(
            channel=self.name,
            chat_id = str(chat_id),
            content = content,
            metadata=meta,
        )

        self.bus.publish_inbound(msg)