import logging
import coloredlogs
import os
from logging.handlers import TimedRotatingFileHandler

BASE_LOG_DIR = "logs"   # 相对运行目录


# 彩色输出样式
field_styles = {
    'asctime': {'color': 'cyan'},
    'levelname': {'bold': True, 'color': 'white'},
    'name': {'color': 'magenta'},
}

level_styles = {
    'debug': {'color': 'blue'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'bold': True, 'color': 'white', 'background': 'red'},
}


def create_handler(path: str, level: int):
    """
    创建每天自动分割、保留30天的 Handler。
    """
    handler = TimedRotatingFileHandler(
        filename=path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
        utc=False
    )
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    return handler


def get_logger(module_name: str) -> logging.Logger:
    """
    每个模块：
    logs/<module_name>/
        - <module_name>.log  (所有 level)
        - debug.log
        - info.log
        - error.log
        都按天分割、保留30天
    """

    logger = logging.getLogger(module_name)

    # 避免重复加载 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    safe_name = module_name.replace(".", "_")
    module_dir = os.path.join(BASE_LOG_DIR, safe_name)
    os.makedirs(module_dir, exist_ok=True)

    # 主日志（所有级别）
    main_log = os.path.join(module_dir, f"{safe_name}.log")
    logger.addHandler(create_handler(main_log, logging.DEBUG))

    # debug.log
    debug_log = os.path.join(module_dir, "debug.log")
    logger.addHandler(create_handler(debug_log, logging.DEBUG))

    # info.log
    info_log = os.path.join(module_dir, "info.log")
    logger.addHandler(create_handler(info_log, logging.INFO))

    # error.log
    error_log = os.path.join(module_dir, "error.log")
    logger.addHandler(create_handler(error_log, logging.ERROR))

    # 控制台彩色输出
    coloredlogs.install(
        level="DEBUG",
        logger=logger,
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level_styles=level_styles,
        field_styles=field_styles
    )

    return logger
