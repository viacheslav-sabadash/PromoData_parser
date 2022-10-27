import logging
import os
from datetime import datetime
from logging import Formatter, Logger, INFO, DEBUG
from typing import TypeVar

import coloredlogs
from concurrent_log_handler import ConcurrentRotatingFileHandler

L = TypeVar('L', bound=Logger)


def get_logger(log_dir_path: str, logger_name: str = 'main') -> Logger:
    """
    Logger factory.
    :param log_dir_path: path
    :param logger_name: name
    :return: Logger instance
    """
    logger_name = logger_name.removesuffix('.py').replace('.', '_')

    _logger = logging.getLogger(logger_name)

    log_file_name = f'{logger_name}_{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}.log'
    handler = ConcurrentRotatingFileHandler(os.path.join(log_dir_path, log_file_name), "a", 1024 ** 2, 5)

    _logger.setLevel(INFO)

    formatter_str = '%(asctime)s %(levelname)7s [%(name)s]: %(message)s'
    level_style = coloredlogs.parse_encoded_styles(
        'info=green; debug=cyan; warning=yellow; error=red; critical=background=red'
    )
    field_styles = coloredlogs.parse_encoded_styles(
        'asctime=green; levelname=cyan; name=yellow'
    )
    formatter = Formatter(formatter_str)
    handler.setFormatter(formatter)

    coloredlogs.install(
        level=DEBUG,     # INFO or DEBUG or ...
        level_styles=level_style,
        field_styles=field_styles,
        fmt=formatter_str,
        milliseconds=True
    )

    _logger.addHandler(handler)
    return _logger
