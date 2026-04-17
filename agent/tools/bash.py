import os
import platform
import subprocess

from langchain_core.tools import tool

from agent.utils.common_util import get_working_dir
from agent.utils.logger import get_logger

logger = get_logger("bash_tool")

DEFAULT_TIMEOUT = 300  # 5 minutes


@tool
def bash(command: str, timeout: int = DEFAULT_TIMEOUT):
    """Execute a bash command and return the output.

    Args:
        command: The bash command to execute.
        timeout: Maximum execution time in seconds (default: 300).
    """
    working_dir = get_working_dir()
    logger.debug(f"执行 bash 命令: {command[:100]}... (超时: {timeout}s)")

    try:
        if platform.system() == "Windows":
            command = command.replace("\\", "/")
            cmd = [os.getenv("GIT_BASH_PATH"), '-c', command]
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
            )
    except subprocess.TimeoutExpired:
        logger.warning(f"命令超时: {command[:100]}... (超时时间: {timeout}s)")
        return f"Error: Command timed out after {timeout} seconds: {command}"

    output = result.stdout
    if result.returncode != 0 and result.stderr:
        output += f"\nSTDERR: {result.stderr}"
        logger.warning(f"命令执行失败: {command[:100]}... (退出码: {result.returncode})")
    elif result.returncode != 0:
        output += f"\nExit code: {result.returncode}"
        logger.warning(f"命令执行返回非零退出码: {command[:100]}... (退出码: {result.returncode})")
    else:
        logger.debug(f"命令执行成功: {command[:100]}...")

    return output
