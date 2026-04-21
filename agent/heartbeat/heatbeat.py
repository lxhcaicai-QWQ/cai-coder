import os
import threading
import time

from pathlib import Path
from typing import Callable, Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.utils.logger import get_logger

log = get_logger("heart_beat")

class HeartBeatResult(BaseModel):
    """Action items extracted from heartbeat"""
    action: Literal["run", "skip"]  = Field(description="skip = nothing to do, run = has active tasks")
    tasks: str = Field(description="natural-language summary of active tasks (required for run), leave it blank if there are no tasks to do")


def _get_agent():
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )
    return create_agent(
        model=model,
        system_prompt = "You are a heartbeat agent.",
        tools=[],
        response_format=ToolStrategy(
            schema=HeartBeatResult,
            tool_message_content="Action item captured and added to heart beat result!"
        ),
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
        """Read heartbeat file"""
        if self.heartbeat_file.is_file():
            try:
                return self.heartbeat_file.read_text(encoding="utf-8")
            except Exception as e:
                log.warning(f"Failed to read HEARTBEAT.md, path = {self.heartbeat_file} : {e}")
                return None
        return None

    def _decide(self, content: str) -> HeartBeatResult:
        """llm decides whether to execute the task"""
        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": f"Review the following HEARTBEAT.md and decide whether there are active tasks.\n\n{content}"}]}
        )
        return response['structured_response']

    def start(self) -> None:
        """Start scheduled heartbeat task"""
        if not self.enabled:
            log.info("Heartbeat disabled")
            return

        if self._running:
            log.warning("Heartbeat already running")
            return

        self._running = True
        self._thread.start()


    def _run_loop(self) -> None:
        """Trigger a task once on a scheduled loop"""
        while self._running:
            time.sleep(self.interval_seconds)
            if self._running:
                self._tick()


    def _tick(self):
        """Execute a heartbeat task once"""
        content = self._read_heartbeat_file()
        if not content:
            log.debug("HEARTBEAT.md missing or empty")

        log.info("Heartbeat: checking for tasks...")

        try:
            decision = self._decide(content)
            action = decision.action
            tasks= decision.tasks

            if action != "run":
                log.info("Heartbeat_ok (nothing to report)")
                return

            log.info("Heartbeat: executing task...")
            if self.on_execute:
                log.debug(f"Heartbeat: start executing tasks({tasks})")

                response = self.on_execute(tasks)
                log.info("Heartbeat: tasks completed, pushing response")
                if self.on_notify:
                    log.debug(f"Heartbeat: notify tasks responses({response})")
                    self.on_notify(response)
                else:
                    log.info("Heartbeat: do not push results after evaluation")
        except Exception:
            log.exception("Heartbeat: execution failed")



    def trigger_now(self) -> str | None:
        """Trigger a heartbeat"""
        content = self._read_heartbeat_file()
        if not content:
            return None

        decision = self._decide(content)
        action = decision.action
        tasks = decision.tasks

        if action != "run" or not self.on_execute:
            return None
        return self.on_execute(tasks)



