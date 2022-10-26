from typing import Any, Union
from urllib.parse import urljoin

import requests
from furl import furl


class BaseParser:

    def __init__(self):
        self._html = ''

    def abs_url(self, href: str) -> str:
        return urljoin(self._config.base_url, href)

    def get_html(self, url: str):
        print(f' --- get_html: {url}')
        response = self.get_page(url=url)
        if response.status_code == 200:
            self._html = response.text
        else:
            raise requests.exceptions.ConnectionError

    def _parse_rules(self, parent_cat: 'bs4.element.Tag') -> Union['bs4.element.Tag', tuple]:
        result = parent_cat
        for rule in self._rules:
            if not result:
                continue
            method = getattr(result, rule.get('call'))
            result = method(**rule.get('args', {}))
            if rule.get('add_url_params'):
                # for a in result.find_all('a', href=True):
                for a in result:
                    if a.get('href'):
                        a['href'] = self._add_url_params(a['href'], rule.get('add_url_params'))
        return result or tuple()

    @staticmethod
    def _add_url_params(url: str, params: dict[str, Any]) -> str:
        return furl(url).add(params).url
