import threading

from agent.bus.bus import MessageBus
from agent.integration.base import BaseChannel
from agent.integration.register import discover_all
from agent.utils.logger import get_logger

log = get_logger("channel_manager")

class ChannelManager:

    def __init__(self, bus: MessageBus):
        self.bus = bus
        self.channels: dict[str, BaseChannel] = {}

        self._init_channels()


    def _init_channels(self) -> None:
        for name, base_channel in discover_all(self.bus).items():
            self.channels[name] = base_channel

    def _start_channel(self, name: str, channel: BaseChannel) -> None:
        log.info("start channel {}", name)
        channel.start()


    def start_all(self):
        threading.Thread(target=self._dispatch_outbound, daemon=True).start()

        for name, channel in self.channels.items():
            threading.Thread(target=self._start_channel,args=(name, channel), daemon=True).start()


    def _dispatch_outbound(self) -> None:
        while True:
            msg = self.bus.consume_outbound()

            channel = self.channels.get(msg.channel)
            if channel:
                channel.send(msg)