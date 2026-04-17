import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "cai-coder",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回一个配置好的日志记录器。

    Args:
        name: 日志记录器名称
        level: 日志级别 (logging.DEBUG, logging.INFO, etc.)
        log_file: 可选的日志文件路径
        format_string: 可选的自定义格式字符串

    Returns:
        配置好的日志记录器
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    # 创建格式化器
    formatter = logging.Formatter(format_string)

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 清除现有的处理器（避免重复添加）
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 默认日志记录器
default_logger = setup_logger()


def get_logger(name: str = "cai-coder") -> logging.Logger:
    """
    获取一个日志记录器。

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)
