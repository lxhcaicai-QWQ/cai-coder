from langchain_core.tools import tool

from agent.utils.common_util import resolve_path
from agent.utils.logger import get_logger

logger = get_logger("read_file_tool")


@tool
def read_file(file_path: str):
    """Read the contents of a file"""
    logger.debug(f"读取文件: {file_path}")
    try:
        safe_path = resolve_path(file_path)
    except ValueError as exc:
        logger.warning(f"文件路径解析失败: {file_path} - {exc}")
        return str(exc)

    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.debug(f"文件读取成功: {safe_path} (长度: {len(content)} 字符)")
        return content
    except FileNotFoundError:
        logger.error(f"文件不存在: {safe_path}")
        return f"No such file or directory: '{safe_path}'"
