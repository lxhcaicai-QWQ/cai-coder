from pathlib import Path

from agent import webapp
from agent.bus.bus import MessageBus
from agent.integration.manager import ChannelManager
from agent.server import AgentLoop
from agent.session import SessionManager
from agent.utils.common_util import get_working_dir
from agent.utils.logger import get_logger

logger = get_logger("main")
working_dir = get_working_dir()

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Cai-Coder 服务启动中...")
    logger.info("=" * 50)

    bus = MessageBus()
    channel_manager = ChannelManager(bus)
    channel_manager.start_all()

    manager = SessionManager(Path(working_dir))
    agent_loop = AgentLoop(bus=bus,session_manager=manager)
    agent_loop.start()

    webapp.start()