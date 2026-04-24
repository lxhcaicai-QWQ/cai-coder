import queue

from agent.bus.events import InMessage, OutMessage


class MessageBus:

    def __init__(self):
        self.inbound: queue.Queue[InMessage] = queue.Queue()
        self.outbound: queue.Queue[OutMessage] = queue.Queue()

    def publish_inbound(self, msg: InMessage) -> None:
        self.inbound.put(msg)

    def consume_inbound(self, timeout: float = None) -> InMessage:
        return self.inbound.get(timeout=timeout)

    def publish_outbound(self, msg: OutMessage) -> None:
        self.outbound.put(msg)

    def consume_outbound(self) -> OutMessage:
        return self.outbound.get()

# Global Event Bus
global_message_bus = MessageBus()