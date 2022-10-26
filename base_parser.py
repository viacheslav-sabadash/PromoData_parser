from typing import Any, Union, Optional
from urllib.parse import urljoin

import bs4
import requests
from furl import furl


class BaseParser:

    def __init__(self):
        self._html = ''

    def abs_url(self, href: str) -> str:
        return urljoin(self._config.base_url, href)

    def get_html(self, url: str):
        print(f' ---> get_html: {url}')
        response = self.get_page(url=url)
        if response.status_code == 200:
            self._html = response.text
        else:
            raise requests.exceptions.ConnectionError

    def _parse_rules(self, parent_elem: 'bs4.element.Tag') -> Union['bs4.element.Tag', tuple]:
        result = parent_elem
        for rule in self._rules:
            if not result:
                continue
            method = getattr(result, rule.get('call'))
            result = method(**rule.get('args', {}))
            if rule.get('add_url_params'):
                for a in result:
                    if a.get('href'):
                        a['href'] = self._add_url_params(a['href'], rule.get('add_url_params'))
        return result or tuple()

    def _parse_rule(self, parent_elem: 'bs4.element.Tag', rule: dict) -> Optional['bs4.element.Tag']:
        if not parent_elem:
            return None
        method = getattr(parent_elem, rule.get('call'))
        result = method(**rule.get('args', {}))
        if rule.get('add_url_params'):
            for a in result:
                if a.get('href'):
                    a['href'] = self._add_url_params(a['href'], rule.get('add_url_params'))

        return result

    @staticmethod
    def _add_url_params(url: str, params: dict[str, Any]) -> str:
        return furl(url).add(params).url
