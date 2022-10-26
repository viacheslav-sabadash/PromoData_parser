import random
import time
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter


class PageLoader:
    _last_request_time: int = 0
    _session = requests.Session()

    # def __init__(self, config: 'Config'):
    #     self.__config = config
    #     self.__session = requests.Session()
    #     self.__session.mount('', HTTPAdapter(max_retries=self.__config.max_retries))

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
            time.sleep(current_request_delay - (current_time - PageLoader._last_request_time))
        PageLoader._last_request_time = current_time
        return PageLoader._session.get(url=url, headers=self._config.headers)
