from bs4 import BeautifulSoup
from ordered_set import OrderedSet

import data_classes
from core.base_parser import BaseParser
from core.config import Config
from core.page_loader import PageLoader
from paginator import Paginator

PARSER = 'html.parser'


class ItemsList(BaseParser, PageLoader):
    """
    Collect list of urls to site items
    """

    def __init__(
            self,
            config_: 'Config',
            paginator: 'Paginator',
            rules: list[dict]
    ):
        self._config = config_
        self.__paginator = paginator
        self._rules = rules
        self._html: str = ''
        self.__items: OrderedSet['data_classes.Page'] = OrderedSet()
        super().__init__()

    def parse_all(self):
        """
        Handle for parser starting
        :return: None
        """
        self.logger.info(f' >>> Starting Items List parsing for {len(self.__paginator.pagination_data)} pages')

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

        self.logger.info(f' <<< Items List parsing complete. Result total = {len(self.__items)}')

    @property
    def items_list_data(self) -> list['data_classes.ItemList']:
        """
        List of dataclasses.
        :return: list of dataclasses
        """
        return list(self.__items)
