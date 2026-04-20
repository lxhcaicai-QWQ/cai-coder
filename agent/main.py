from pathlib import Path

from agent import webapp
from agent.bus.bus import MessageBus
from agent.bus.events import OutMessage
from agent.heartbeat.heatbeat import HeartbeatService
from agent.integration.manager import ChannelManager
from agent.server import AgentLoop, get_agent
from agent.session import SessionManager
from agent.utils.common_util import get_working_dir
from agent.utils.logger import get_logger

logger = get_logger("main")
working_dir = get_working_dir()
direct_agent = get_agent()

def gateway():

    session_manager = SessionManager(Path(working_dir))

    bus = MessageBus()
    channel_manager = ChannelManager(bus)
    channel_manager.start_all()


    def _get_heartbeat_target() -> tuple[str,str]:
        sessions = session_manager.list_sessions()
        if not list:
            return "cli", "skip"
        for item in sessions:
            key = item.key
            channel, chat_id = key.split(":",1)
            return channel, chat_id

        return "cli", "skip"

    def on_heartbeat_execute(content: str)->str:
        config = {"configurable": {"thread_id": "heart_beat"}}
        response = direct_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            },
            config=config
        )

        return response["messages"][-1].content

    def on_heartbeat_notify(content: str)->str:
        channel, chat_id = _get_heartbeat_target()
        msg = OutMessage(
            channel=channel,
            chat_id=chat_id,
            content=content,
            metadata={}
        )
        bus.publish_outbound(msg)
        return "done"


    heartbeat = HeartbeatService(
        workspace=Path(working_dir),
        interval_seconds=60,
        on_execute=on_heartbeat_execute,
        on_notify=on_heartbeat_notify
    )


    agent_loop = AgentLoop(bus=bus,session_manager=session_manager)
    agent_loop.start()
    heartbeat.start()





def run():
    logger.info("=" * 50)
    logger.info("Cai-Coder 服务启动中...")
    logger.info("=" * 50)

    gateway()

    webapp.start()



if __name__ == "__main__":
    run()