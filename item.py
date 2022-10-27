from copy import copy
from datetime import datetime
from typing import Type, Any

import bs4
from bs4 import BeautifulSoup

import data_classes
from core.base_parser import BaseParser
from core.config import Config
from core.csv_helper import CsvHelper
from core.page_loader import PageLoader
from items_list import ItemsList
from post_processing import PostProcessing

PARSER = 'html.parser'


class Item(BaseParser, PageLoader, CsvHelper):
    """
    Collecting Items
    """

    def __init__(
            self,
            config_: 'Config',
            items_list: 'ItemsList',
            item_rules: list[dict],
            item_child_value_rules: dict,
            item_glob_value_rules: dict,
            post_processing: Type['PostProcessing'],
            csv_filename: str | None = None
    ):
        self._config = config_
        self.__items_list = items_list
        self._rules = item_rules
        self._item_child_value_rules = item_child_value_rules
        self._item_glob_value_rules = item_glob_value_rules
        self._post_processing = post_processing
        self.__csv_filename = csv_filename
        self._html: str = ''
        self.__items: list['data_classes.Item'] = []
        BaseParser.__init__(self)
        PageLoader.__init__(self)
        CsvHelper.__init__(self, self._config)

    def _item_parse(self, soup: 'bs4.element.Tag', rules: dict) -> dict[str, Any]:
        """
        Single item parse
        :param soup: Tag
        :param rules: list of item dict rules
        :return: dict with Item fields
        """
        result_item = {}
        for key, rule in rules.items():
            rule_result = self._parse_rule(soup, rule)
            val = copy(rule_result)
            if rule.get('post_processing'):
                for process in rule.get('post_processing'):
                    val = getattr(self._post_processing(val, self._config.base_url), process)
            result_item[key] = val

        return result_item

    def parse_all(self):
        """
        Handle for parser starting
        :return: None
        """
        self.logger.info(f' >>> Starting Items parsing for {len(self.__items_list.items_list_data)} urls')

        for page in self.__items_list.items_list_data:
            self.get_html(page.item_url)
            page_soup = BeautifulSoup(self._html, PARSER)

            # shared item values
            shared_item = dict(
                price_datetime=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                sku_category=f'{page.parent_category}|{page.category}',
                sku_link=page.item_url
            )
            shared_item.update(self._item_parse(page_soup, self._item_glob_value_rules))

            # additional item values
            additional_items = []
            for items_row in self._parse_rules(page_soup):
                current_item = self._item_parse(items_row, self._item_child_value_rules)
                additional_items.append(current_item)

            for item in additional_items:
                item.update(shared_item)  # connect additional items to shared item
                # fix all fields to final result
                item_data = self._post_processing(item, self._config.base_url).line_process()
                self.__items.append(item_data)
                if self.__csv_filename:
                    self.append_data(self.__csv_filename, item_data)
                self.logger.info(f' > {item_data}')

        self.logger.info(f' <<< Items parsing complete. Result total = {len(self.__items)}')

    @property
    def items_data(self) -> list['data_classes.Item']:
        """
        List of dataclasses.
        :return: list of dataclasses
        """
        return list(self.__items)
