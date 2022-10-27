import random
import time
from datetime import datetime
from logging import Logger

import requests
from requests.adapters import HTTPAdapter

from log_lib import get_logger


class PageLoader:
    _last_request_time: int = 0
    _session = requests.Session()
    logger = None

    def __init__(self):
        if not self.logger:
            self.logger: Logger = get_logger(self._config.logs_dir_abs, 'LOADER')

    def delay_val(self):
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
        PageLoader._session.mount('', HTTPAdapter(max_retries=self._config.max_retries))

        current_time = datetime.utcnow().timestamp()
        current_request_delay = self.delay_val()
        if current_time - PageLoader._last_request_time < current_request_delay:
            sleep_sec = current_request_delay - (current_time - PageLoader._last_request_time)
            time.sleep(sleep_sec)
            self.logger.info(f'Sleep for {sleep_sec} sec')
        PageLoader._last_request_time = current_time

        return PageLoader._session.get(url=url, headers=self._config.headers)
