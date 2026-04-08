import subprocess

def bash(command: str):
    """Execute a bash command and return the output"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout