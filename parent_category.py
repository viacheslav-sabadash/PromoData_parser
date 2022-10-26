from bs4 import BeautifulSoup

import config
import data_classes
from page_loader import PageLoader
from base_parser import BaseParser

PARSER = 'html.parser'


class ParentCategory(BaseParser, PageLoader):

    def __init__(
            self,
            config_: 'config.Config',
            # page_loader_: 'PageLoader',
            rules: list[dict]
    ):
        self._config = config_
        # self._page_loader = page_loader_
        self._rules: list[dict] = rules
        self._html: str = ''
        self.__categories: list['bs4.element.Tag'] = []

    def parse(self):
        if not self._html:
            self.get_html(url=self._config.base_url)
        page_soup = BeautifulSoup(self._html, PARSER)
        self.__categories = self._parse_rules(page_soup)
        if self._config.categories:
            self.__categories = list(
                filter(lambda cat: cat.text in self._config.categories, self.__categories)
            )
        # print(self.__categories)

    @property
    def categories(self) -> list['bs4.element.Tag']:
        return self.__categories

    @property
    def categories_data(self) -> list['data_classes.Category']:
        return [
            data_classes.Category(
                id=i,
                name=cat.text,
                url=cat.get('href', '')
            )
            for i, cat in enumerate(self.__categories)
        ]
