import os
import threading
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agent.utils.logger import get_logger

log = get_logger("heartbeat")

@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # action: skip = nothing to do, run = has active tasks
    action: str
    # tasks: Natural-language summary of active tasks (required for run)
    tasks: str | None = None

@tool
def heartbeat_tool(action: str, tasks: str = None) -> tuple[str, str]:
    """
    Report heartbeat decision after reviewing tasks.
    Args:
        action: skip = nothing to do, run = has active tasks
        tasks: Natural-language summary of active tasks (required for run)
    Returns:
        action, tasks
    """
    if not tasks:
        tasks = ""
    return action, tasks


def _get_agent():
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )
    return create_agent(
        model=model,
        system_prompt = "You are a heartbeat agent. Call the heartbeat tool to report your decision.",
        tools=[heartbeat_tool],
        response_format=ToolStrategy(ResponseFormat),
    )

class HeartbeatService:

    def __init__(
            self,
            workspace: Path,
            on_execute: Callable[[str], str] | None,
            on_notify: Callable[[str], str] | None,
            interval_seconds: int = 30 * 60,
            enabled: bool = True
    ):
        self.workspace = workspace
        self.on_execute=on_execute
        self.on_notify=on_notify
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self._running = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self.agent = _get_agent()

    @property
    def heartbeat_file(self) -> Path:
        return self.workspace / "HEARTBEAT.md"

    def _read_heartbeat_file(self) -> str | None:
        if self.heartbeat_file.is_file():
            try:
                return self.heartbeat_file.read_text(encoding="utf-8")
            except Exception as e:
                log.warning(f"Failed to read HEARTBEAT.md, path = {self.heartbeat_file} : {e}")
                return None
        return None

    def _decide(self, content: str) -> ResponseFormat:
        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": f"Review the following HEARTBEAT.md and decide whether there are active tasks.\n\n{content}"}]}
        )
        return response['structured_response']

    def start(self) -> None:
        if not self.enabled:
            log.info("Heartbeat disabled")
            return

        if self._running:
            log.warning("Heartbeat already running")
            return

        self._running = True
        self._thread.run()


    def _run_loop(self) -> None:
        while self._running:
            sleep(self.interval_seconds)
            if self._running:
                self._tick()


    def _tick(self):

        content = self._read_heartbeat_file()
        if not content:
            log.debug("HEARTBEAT.md missing or empty")

        log.info("checking for tasks...")

    def trigger_now(self) -> str | None:

        content = self._read_heartbeat_file()
        if not content:
            log.debug("HEARTBEAT.md missing or empty")

