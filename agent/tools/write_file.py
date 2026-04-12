import os

from langchain_core.tools import tool

from agent.utils.common_util import resolve_path


@tool
def write_file(file_path: str, content: str):
    """Write contents to a file"""
    try:
        safe_path = resolve_path(file_path)
    except ValueError as exc:
        return {"success": False, "error": str(exc)}

    parent = os.path.dirname(safe_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(safe_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return {"success": True}