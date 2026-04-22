import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from agent.utils.logger import get_logger

log = get_logger("cron_service")

# ================= Data Models ================

@dataclass
class CronSchedule:
    kind: str  # "every" (periodic execution) or "at" (one-time execution)
    every_ms: int = 0  # interval in milliseconds for periodic execution
    at_ms: int = 0  # absolute timestamp (in milliseconds) for one-time execution

@dataclass
class CronJobState:
    next_run_at_ms: int | None = None
    last_run_at_ms: int | None = None
    last_status: str | None = None
    last_error: str | None = None

@dataclass
class CronJob:
    id: str = field(default_factory=lambda :str(uuid.uuid4())[:8])
    name: str = "",
    enabled: bool = True,
    schedule: CronSchedule = field(default_factory=CronSchedule)
    state: CronJobState = field(default_factory=CronJobState)
    payload: Any = None


def _now_ms() -> int:
    """Get the current time in milliseconds timestamp"""
    return int(time.time() * 1000)

def _compute_next_run(schedule: CronSchedule, now_ms: int) -> int | None:
    """Calculate the absolute timestamp for the next execution"""
    if schedule.kind == "every":
       if schedule.every_ms <= 0:
           return None
       return now_ms + schedule.every_ms
    elif schedule.kind == "at":
        # If the execution time has passed, return None to indicate no further execution
        return schedule.at_ms if schedule.at_ms > now_ms else None
    return None

class CronService:

    def __init__(
            self,
            on_job: Callable[[CronJob], None] | None = None,
            max_sleep_ms: int = 300_000
    ):
        self.on_job = on_job
        self.max_sleep_ms = max_sleep_ms

        self._jobs: list[CronJob] = []
        self._lock = threading.Lock()  # 保护 _jobs 列表的线程安全

        self._running = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()  # Used to wake up sleep and stop threads


    def start(self):
        """Start background scheduled thread"""
        if self._running:
            return
        self._running = True
        self._stop_event.clear()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        log.info("Cron service started.")

    def _run_loop(self):
        """Main loop of the background thread: dynamic sleep + triggered execution"""


    def _get_next_wake_ms(self):

        with self._lock:
            times = [
                job.state.next_run_at_ms for job in self._jobs
                if job.enabled and job.state.next_run_at_ms
            ]
            return min(times) if times else None


    # ========== 公开的增删改查 API ==========
    def add_job(self, name: str, schedule: CronSchedule, payload: Any=None) -> CronJob:

        job = CronJob(
            name=name,
            schedule=schedule,
            payload=payload,
            state=CronJobState(
                next_run_at_ms=_compute_next_run(schedule, _now_ms())
            )
        )

        with self._lock:
            self._jobs.append(job)

        return job