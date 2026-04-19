from time import sleep

from agent.bus.bus import MessageBus
from agent.bus.events import OutMessage
from agent.integration.base import BaseChannel
from agent.integration.manager import ChannelManager
from agent.server import AgentLoop
from agent.utils.logger import get_logger

log = get_logger("test_agent_loop")

class MockChannel(BaseChannel):
    name = "mock"

    def send(self, msg: OutMessage) -> None:
        content = msg.content
        chat_id = msg.chat_id

        assert msg.channel == self.name

        log.info(f"[发送回复] chat_id={chat_id}, reply={content[:100]}...")


    def start(self) -> None:
        log.info(f"start mock channel...")
        pass

def _make_channel(bus: MessageBus):
    return MockChannel(bus)

def _make_agent_loop(bus: MessageBus, channel: BaseChannel):
    channel_manager = ChannelManager(bus)
    channel_manager.channels["mock"] = channel

    channel_manager.start_one("mock")
    loop = AgentLoop(bus)
    return loop


def test_agent_loop():
    bus = MessageBus()
    mock_channel = _make_channel(bus)

    agentloop = _make_agent_loop(bus, mock_channel)
    agentloop.start()

    mock_channel._handle_message(
        chat_id="chat_id",
        content="What can you do?",
        metadata= {
            "messages": "How's the weather in Shenzhen?"
        }
    )

    sleep(5)

