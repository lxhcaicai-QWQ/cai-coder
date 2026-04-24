from typing import Literal

from langgraph.prebuilt import ToolRuntime

from agent.bus.bus import global_message_bus
from agent.bus.events import OutMessage
from agent.cron import CronService, CronJob, CronSchedule

from langchain_core.tools import tool

from agent.utils.logger import get_logger

log = get_logger("cron_tool")

def push_message(job:CronJob):
    payload = job.payload
    channel = payload["channel"]
    chat_id = payload["chat_id"]
    message = payload["message"]
    out_message = OutMessage(
        channel=channel,
        chat_id=chat_id,
        content=message,
        metadata={}
    )
    global_message_bus.publish_outbound(out_message)

_service = CronService(on_job=push_message)

@tool
def add_cronjob(
        kind: Literal["at", "every"],
        time_ms: int,
        name: str,
        message: str,
        channel: Literal["feishu", "cli"],
        runtime: ToolRuntime
) -> CronJob:
    """
    创建并启动一个定时任务，任务执行时将通过指定渠道将消息推送到当前会话中。

    Args:
        kind (Literal["at", "every"]): 定时任务的触发类型。
            - "at": 在某个绝对时间点触发一次。
            - "every": 按固定周期循环触发。
        time_ms (int): 时间配置，单位严格为毫秒。
            - 当 kind 为 "at" 时：必须是未来的**绝对时间戳**（如 Unix 毫秒级时间戳 1690000000000）。禁止传入相对时间！
            - 当 kind 为 "every" 时：表示执行的间隔时长（如 5000 代表每 5 秒执行一次）。
        name (str): 定时任务的唯一名称标识，用于后续管理、查询或取消任务。
        message (str): 定时任务触发时需要发送的具体消息内容。请直接填入用户希望发送的完整文本。
        channel (Literal["feishu", "cli"]): 任务触发后的消息推送渠道。
            - "feishu": 推送到飞书。
            - "cli": 推送到本地命令行终端。

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

    configurable = runtime.config.get("configurable") if runtime.config else {}
    chat_id = configurable.get("thread_id")

    payload = {
        "chat_id": chat_id,
        "channel": channel,
        "message": message
    }
    added = _service.add_job(name, schedule=sched, payload=payload)

    log.debug(f"add cron job: {name} message:{message}")

    return added

