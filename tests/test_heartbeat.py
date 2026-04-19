from agent.heartbeat.heatbeat import HeartbeatService

def test_agent_descide(tmp_path) -> None:
    content = """
# Heartbeat Tasks

This file is checked every 30 minutes by your nanobot agent.
Add tasks below that you want the agent to work on periodically.

If this file has no tasks (only headers and comments), the agent will skip the heartbeat.

## Active Tasks

<!-- Add your periodic tasks below this line -->
Write a mobile phone report

## Completed
Check network status

<!-- Move completed tasks here or delete them -->
    """
    service = HeartbeatService(
        workspace=tmp_path,
        on_execute=None,
        on_notify=None
    )
    response = service._decide(content)
    print(response)

