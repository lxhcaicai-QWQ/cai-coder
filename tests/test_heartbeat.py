import time

from agent.heartbeat.heatbeat import HeartbeatService

HEART_BEAT_MD = """
# Heartbeat Tasks

This file is checked every 30 minutes by your nanobot agent.
Add tasks below that you want the agent to work on periodically.

If this file has no tasks (only headers and comments), the agent will skip the heartbeat.

## Active Tasks

<!-- Add your periodic tasks below this line -->
{active_tasks}

## Completed

<!-- Move completed tasks here or delete them -->
{completed_tasks}

"""

def test_heartbeat_decide_run(tmp_path) -> None:
    content = HEART_BEAT_MD.format(
        active_tasks='Write a mobile phone report',
        completed_tasks='Check network status'
    )
    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=None,
        on_notify=None
    )
    response = service._decide(content)
    assert response.action == "run"
    print(response)


def test_heartbeat_decide_no_todo(tmp_path) -> None:
    content = HEART_BEAT_MD.format(
        active_tasks='',
        completed_tasks="""
        Write a mobile phone report
        Check network status
        """
    )
    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=None,
        on_notify=None
    )
    response = service._decide(content)
    assert response.action == "skip"
    assert not response.tasks
    print(response)

def test_read_heartbeat_file(tmp_path):

    file = tmp_path / "HEARTBEAT.md"
    file.write_text(HEART_BEAT_MD)

    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=None,
        on_notify=None
    )
    response = service._read_heartbeat_file()
    assert response == HEART_BEAT_MD
    print(response)


def test_trigger_now(tmp_path):
    file = tmp_path / "HEARTBEAT.md"
    content = HEART_BEAT_MD.format(
        active_tasks='Write a mobile phone report',
        completed_tasks='Check network status'
    )
    file.write_text(content)

    def func_execute(text: str) -> str:
        return "func_execute:" + text

    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=func_execute,
        on_notify=None
    )

    response = service.trigger_now()
    assert "func_execute:" in response


def test_tick(tmp_path):
    file = tmp_path / "HEARTBEAT.md"
    content = HEART_BEAT_MD.format(
        active_tasks='Write a mobile phone report',
        completed_tasks='Check network status'
    )
    file.write_text(content)

    def func_execute(text: str) -> str:
        return "func_execute:" + text

    def func_notify(text: str) -> str:
        return "func_notify:" + text

    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=func_execute,
        on_notify=func_notify
    )
    service._tick()


def test_heartbeat_all(tmp_path):
    file = tmp_path / "HEARTBEAT.md"
    content = HEART_BEAT_MD.format(
        active_tasks='Write a mobile phone report',
        completed_tasks='Check network status'
    )
    file.write_text(content)
    def func_execute(text: str) -> str:
        return "func_execute:" + text

    def func_notify(text: str) -> str:
        return "func_notify:" + text

    service = HeartbeatService(
        workspace=tmp_path,
        interval_seconds=5,
        on_execute=func_execute,
        on_notify=func_notify
    )
    service.start()
    time.sleep(10)
    print("done")