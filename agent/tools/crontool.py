from typing import Literal

from agent.cron import CronService, CronJob, CronSchedule

from langchain_core.tools import tool
_service = CronService()

@tool
def add_cronjob(kind: Literal["at", "every"], time_ms: int, name: str) -> CronJob:
    """
    创建并启动一个定时任务（单次执行或周期性执行）。

    Args:
        kind (Literal["at", "every"]): 定时任务的触发类型。
            - "at": 在某个绝对时间点触发一次。
            - "every": 按固定周期循环触发。
        time_ms (int): 时间配置，单位严格为毫秒。
            - 当 kind 为 "at" 时：必须是未来的**绝对时间戳**（例如 Unix 毫秒级时间戳 1690000000000）。
              注意：不要传入相对时间（如 5000），必须计算成具体的时间戳！
            - 当 kind 为 "every" 时：表示执行的间隔时长（例如传入 5000 代表每 5 秒执行一次）。
        name (str): 定时任务的唯一名称标识，用于后续管理、查询或取消任务。

    Returns:
        CronJob: 成功创建的定时任务对象，包含任务状态等详细信息。
    """
    if kind == "at":
        sched = CronSchedule(
            kind="at",
            at_ms=time_ms
        )
    else:
        sched = CronSchedule(
            kind="every",
            every_ms=time_ms
        )

    added = _service.add_job(name, schedule=sched, payload={"version": "1.0"})
    _service.start()

    return added

