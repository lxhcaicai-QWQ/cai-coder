import os
import platform
import subprocess

from langchain_core.tools import tool

from agent.utils.common_util import find_project_root

DEFAULT_TIMEOUT = 300  # 5 minutes


def _get_working_dir() -> str:
    """Get the working directory from env or fallback to project root."""
    env_dir = os.getenv("WORKING_DIR")
    if env_dir:
        return str(os.path.abspath(env_dir))
    return str(find_project_root())


@tool
def bash(command: str, timeout: int = DEFAULT_TIMEOUT):
    """Execute a bash command and return the output.

    Args:
        command: The bash command to execute.
        timeout: Maximum execution time in seconds (default: 300).
    """
    working_dir = _get_working_dir()

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
        return f"Error: Command timed out after {timeout} seconds: {command}"

    output = result.stdout
    if result.returncode != 0 and result.stderr:
        output += f"\nSTDERR: {result.stderr}"
    if result.returncode != 0:
        output += f"\nExit code: {result.returncode}"

    return output
