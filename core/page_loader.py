import random
import time
from datetime import datetime
from logging import Logger

import requests
from requests.adapters import HTTPAdapter

from .log_lib import get_logger


class PageLoader:
    """
    Page loader with http
    """

    _last_request_time: int = 0
    _session = requests.Session()

    def __init__(self):
        PageLoader._session.mount('', HTTPAdapter(max_retries=self._config.max_retries))
        self.logger: Logger = get_logger(self._config.logs_dir_abs)
        # super().__init__()

    def delay_val(self):
        """
        Parsing delay value for different config values like:
        1-3 - random between 1 and 3
        10 - simple 10
        :return: int value
        """
        if isinstance(self._config.delay_range_s, int):
            return self._config.delay_range_s
        result = 0
        try:
            min_s, max_s = self._config.delay_range_s.split('-')
            result = random.randint(int(min_s), int(max_s))
        except ValueError:
            try:
                result = int(self._configdelay_range_s)
            except ValueError:
                pass
        return result

    def get_page(self, url: str) -> 'requests.Response':
        """
        Get page from remote server
        :param url: URL
        :return: requests.Response instance
        """
        current_time = datetime.utcnow().timestamp()
        current_request_delay = self.delay_val()
        if current_time - PageLoader._last_request_time < current_request_delay:
            sleep_sec = current_request_delay - (current_time - PageLoader._last_request_time)
            self.logger.info(f'Sleep for {sleep_sec} sec')
            time.sleep(sleep_sec)
        PageLoader._last_request_time = current_time

        return PageLoader._session.get(url=url, headers=self._config.headers)
