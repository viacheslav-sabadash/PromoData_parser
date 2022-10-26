from datetime import datetime
from typing import Type, Any

import bs4
from bs4 import BeautifulSoup

import config
import data_classes
from base_parser import BaseParser
from items_list import ItemsList
from page_loader import PageLoader
from post_processing import PostProcessing

PARSER = 'html.parser'


class Item(BaseParser, PageLoader):

    def __init__(
            self,
            config_: 'config.Config',
            items_list: 'ItemsList',
            item_rules: list[dict],
            item_child_value_rules: dict,
            item_glob_value_rules: dict,
            post_processing: Type['PostProcessing']
    ):
        self._config = config_
        self.__items_list = items_list
        self._rules = item_rules
        self._item_child_value_rules = item_child_value_rules
        self._item_glob_value_rules = item_glob_value_rules
        self._post_processing = post_processing
        self._html: str = ''
        self.__items: list['data_classes.Item'] = []

    def _item_parse(self, soup: 'bs4.element.Tag', rules: dict) -> dict[str, Any]:
        result_item = {}
        for key, rule in rules.items():
            rule_result = self._parse_rule(soup, rule)
            if rule_result:
                val = rule_result
                if rule.get('post_processing'):
                    for process in rule.get('post_processing'):
                        val = getattr(self._post_processing(val, self._config.base_url), process)
                result_item[key] = val
            else:
                result_item[key] = None
        return result_item

    # def apply_post_processing(self, rule_result, rule) -> Optional[Any]:
    #     item = {}
    #     if rule_result:
    #         val = rule_result
    #         if rule.get('post_processing'):
    #             for process in rule.get('post_processing'):
    #                 val = getattr(self._post_processing(val), process)
    #
    #     return val

    def parse_all(self):
        for page in self.__items_list.items_list_data:
            self.get_html(page.item_url)
            page_soup = BeautifulSoup(self._html, PARSER)

            # shared item values
            shared_item = dict(price_datetime=datetime.utcnow().strftime("%Y-%d-%m %H:%M:%S"))
            shared_item.update(self._item_parse(page_soup, self._item_glob_value_rules))

            # additional item values
            additional_items = []
            for items_table in self._parse_rules(page_soup):
                current_item = self._item_parse(items_table, self._item_child_value_rules)
                additional_items.append(current_item)

            for item in additional_items:
                item.update(shared_item)    # connect additional items to shared item
                # fix all fields to final result
                item_data = self._post_processing(item, self._config.base_url).line_process()
                self.__items.append(item_data)
                print(item_data)

            # for key, rule in self._item_glob_value_rules.items():
            #     rule_result = self._parse_rule(page_soup, rule)
            #     val = self.apply_post_processing(rule_result, rule)
            #     # if rule_result:
            #     #     val = rule_result
            #     #     if rule.get('post_processing'):
            #     #         for process in rule.get('post_processing'):
            #     #             val = getattr(self._post_processing(val), process)
            #     shared_item[key] = val
            #
            # # additional item values
            # additional_items = []
            #
            # for items_table in self._parse_rules(page_soup):
            #     current_item = {}
            #     for key_, rule_ in self._item_child_value_rules.items():
            #         rule_result = self._parse_rule(items_table, rule)
            #         current_item.update(self._item_parse(rule_result, rule))
            #     additional_items.append(current_item)

    @property
    def items_data(self):
        return list(self.__items)
