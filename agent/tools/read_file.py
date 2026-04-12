from langchain_core.tools import tool

from agent.utils.common_util import resolve_path


@tool
def read_file(file_path: str):
    """Read the contents of a file"""
    try:
        safe_path = resolve_path(file_path)
    except ValueError as exc:
        return str(exc)

    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"No such file or directory: '{safe_path}'"
