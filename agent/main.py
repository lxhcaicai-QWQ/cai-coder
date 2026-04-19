from agent import webapp
from agent.bus.bus import MessageBus
from agent.integration.manager import ChannelManager
from agent.server import AgentLoop
from agent.utils.logger import get_logger

logger = get_logger("main")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Cai-Coder 服务启动中...")
    logger.info("=" * 50)

    bus = MessageBus()
    channel_manager = ChannelManager(bus)
    channel_manager.start_all()

    agent_loop = AgentLoop(bus)
    agent_loop.start()

    webapp.start()