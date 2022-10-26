from bs4 import BeautifulSoup
from ordered_set import OrderedSet

import config
import data_classes
from base_parser import BaseParser
from page_loader import PageLoader
from paginator import Paginator

PARSER = 'html.parser'


class ItemsList(BaseParser, PageLoader):

    def __init__(
            self,
            config_: 'config.Config',
            paginator: 'Paginator',
            rules: list[dict]
    ):
        self._config = config_
        self.__paginator = paginator
        self._rules = rules
        self._html: str = ''
        self.__items: OrderedSet['data_classes.Page'] = OrderedSet()

    def parse_all(self):
        for page in self.__paginator.pagination_data:
            self.get_html(page.url)
            page_soup = BeautifulSoup(self._html, PARSER)
            for item in self._parse_rules(page_soup):
                self.__items.append(
                    data_classes.ItemList(
                        item_url=self.abs_url(item.get('href', '')),
                        **page.__dict__
                    )
                )

    @property
    def items_list_data(self) -> list['data_classes.ItemList']:
        return list(self.__items)
