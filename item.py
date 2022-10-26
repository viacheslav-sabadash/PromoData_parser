from bs4 import BeautifulSoup
from ordered_set import OrderedSet

import config
import data_classes
from base_parser import BaseParser
from items_list import ItemsList

PARSER = 'html.parser'


class Item(BaseParser):

    def __init__(
            self,
            config_: 'config.Config',
            items_list: 'ItemsList',
            rules: list[dict]
    ):
        self._config = config_
        self.__items_list = items_list
        self._rules = rules
        self._html: str = ''
        self.__items: OrderedSet['data_classes.Page'] = OrderedSet()

    def parse_all(self):
        for page in self.__items_list.items_list_data:
            self.get_html(page.url)
            page_soup = BeautifulSoup(self._html, PARSER)
            for item in self._parse_rules(page_soup):
                self.__items.append(
                    data_classes.ItemList(
                        item_url=item.url,
                        **page.__dict__
                    )
                )

    @property
    def items_list_data(self):
        return list(self.__items)
