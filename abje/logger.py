"""日志配置"""

import logging
import sys
from datetime import datetime

logger = logging.getLogger("abje")


def setup_logger(level: int = logging.INFO) -> None:
    """配置日志格式"""
    if logger.handlers:
        return
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)
    logger.setLevel(level)


def format_duration(seconds: float) -> str:
    """格式化耗时"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {secs:.1f}s"
    hours, mins = divmod(minutes, 60)
    return f"{int(hours)}h {int(mins)}m {secs:.1f}s"
