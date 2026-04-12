from pathlib import Path

from langchain_core.tools import tool

from agent.utils.common_util import resolve_path


@tool
def ls(path: str):
    """List files and directories in a given path"""
    try:
        safe_path = resolve_path(path)
    except ValueError as exc:
        return str(exc)

    p = Path(safe_path)

    if not p.exists():
        return f"ls: '{path}' is not exist"

    if p.is_file():
        return p.name

    filelist = []
    for item in sorted(p.iterdir()):
        suffix = '/' if item.is_dir() else ''
        filelist.append(f"{item.name}{suffix}")
    return filelist
