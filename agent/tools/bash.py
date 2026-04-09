import os
import platform
import subprocess

def bash(command: str):
    """Execute a bash command and return the output"""

    if platform.system() == "Windows":
        command = command.replace("\\", "/")
        cmd = [os.getenv("GIT_BASH_PATH"), '-c', command]
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout