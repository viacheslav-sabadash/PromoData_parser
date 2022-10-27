import bs4
from bs4 import BeautifulSoup

import config
import data_classes
from base_parser import BaseParser
from page_loader import PageLoader

PARSER = 'html.parser'


class ParentCategory(BaseParser, PageLoader):
    """
    Loading a collection of parent categories.
    """

    def __init__(
            self,
            config_: 'config.Config',
            rules: list[dict]
    ):
        self._config = config_
        self._rules: list[dict] = rules
        self._html: str = ''
        self.__categories: list['bs4.element.Tag'] = []
        super(ParentCategory, self).__init__()

    def parse(self):
        """
        Handle for parser starting
        :return: None
        """
        self.logger.info(f' > Starting Parent Categories parsing: {self._config.categories} ')

        if not self._html:
            self.get_html(url=self._config.base_url)
        page_soup = BeautifulSoup(self._html, PARSER)
        self.__categories = self._parse_rules(page_soup)
        if self._config.categories:
            self.__categories = list(
                filter(lambda cat: cat.text in self._config.categories, self.__categories)
            )

        self.logger.info(f' < Parent Categories parsing complete. Total = {len(self.__categories)}')

    @property
    def categories(self) -> list['bs4.element.Tag']:
        """
        List of Tag objects to continue parsing with.
        :return: list of tags
        """
        return self.__categories

    @property
    def categories_data(self) -> list['data_classes.Category']:
        """
        List of dataclasses.
        :return: list of dataclasses
        """
        return [
            data_classes.Category(
                id=i,
                name=cat.text,
                url=cat.get('href', '')
            )
            for i, cat in enumerate(self.__categories)
        ]
