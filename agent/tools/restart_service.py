import os
import sys
import threading
import time

from langchain_core.tools import tool


@tool
def restart_service(delay_seconds: int = 3):
    """Restart the service gracefully.

    Args:
        delay_seconds: Delay before restart in seconds (default: 3).

    Returns:
        str: Message indicating restart is in progress.
    """
    def delayed_restart():
        """Execute restart after delay."""
        time.sleep(delay_seconds)
        print("正在重启服务...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # Execute restart in background thread
    thread = threading.Thread(target=delayed_restart, daemon=True)
    thread.start()

    return f"服务将在 {delay_seconds} 秒后重启..."
