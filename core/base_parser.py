import re
from logging import Logger
from typing import Any, Union, Optional
from urllib.parse import urljoin

import bs4
import requests
from furl import furl

from .log_lib import get_logger


class BaseParser:
    """
    All parsing works here.
    """
    logger = None

    def __init__(self):
        self._html = ''
        if not self.logger:
            self.logger: Logger = get_logger(self._config.logs_dir_abs, 'PARSER')

    def abs_url(self, href: str) -> str:
        """
        Absolute path.
        :param href: absolute or relative path
        :return: path
        """
        return urljoin(self._config.base_url, href)

    def get_html(self, url: str):
        """
        Get remote page html code.
        :param url: url to downloaded page
        :return: html code
        """
        self.logger.info(f' ---> GET: {url}')
        response = self.get_page(url=url)
        if response.status_code == 200:
            self._html = response.text
        else:
            raise requests.exceptions.ConnectionError

    def _parse_rules(self, parent_elem: 'bs4.element.Tag') -> Union['bs4.element.Tag', tuple]:
        """
        Apply list of parsing rules.
        :param parent_elem: Tags
        :return: result Tags or empty tuple
        """
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
        """
        Single rule apply.
        :param parent_elem: Tag
        :param rule: rule dict
        :return: Tag or None
        """
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
        """
        Append additional request params to URL. For example:
        Add q=bar {'q': 'bar'} for https://google.com/?f=foo.
        Result https://google.com/?f=foo&q=bar.
        :param url: base URL part
        :param params: dict like {'param': value}
        :return: merged full URL
        """
        return furl(url).add(params).url
