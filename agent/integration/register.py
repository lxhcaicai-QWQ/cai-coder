from agent.bus.bus import MessageBus
from agent.integration.base import BaseChannel
from agent.integration.feishu.bot import FeishuChannel


def discover_all(bus: MessageBus) -> dict[str, BaseChannel]:
    channels: dict[str, BaseChannel] = {
        "feishu": FeishuChannel(bus),
    }

    return channels