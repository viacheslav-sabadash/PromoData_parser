from ordered_set import OrderedSet

import data_classes
from core.base_parser import BaseParser
from core.config import Config
from parent_category import ParentCategory


class Category(BaseParser):
    """
    Get collection of sub-categories.
    """

    def __init__(
            self,
            config_: 'Config',
            parent: 'ParentCategory',
            rules: list[dict]
    ):
        self._config = config_
        self.__parent = parent
        self._rules = rules
        self.__categories: OrderedSet['data_classes.Category'] = OrderedSet()
        super(Category, self).__init__()

    def parse_all(self):
        """
        Handle for parser starting
        :return: None
        """
        self.logger.info(f' >>> Starting Categories parsing for {len(self.__parent.categories_data)} parent categories')

        counter = 0
        for parent_cat in self.__parent.categories:
            parent_category = data_classes.Category(
                id=counter,
                name=parent_cat.text,
            )
            self.__categories.append(parent_category)
            counter += 1

            for category in self._parse_rules(parent_cat):
                self.__categories.append(
                    data_classes.Category(
                        id=counter,
                        name=category.text,
                        url=self.abs_url(category.get('href', '')),
                        parent_category_id=parent_category.id,
                        parent_category=parent_cat.text,
                    )
                )
                counter += 1

        self.logger.info(f' <<< Parent Categories parsing complete. Result total = {len(self.__categories)}')

    @property
    def categories_data(self) -> list['data_classes.Category']:
        """
        List of dataclasses.
        :return: list of dataclasses
        """
        return list(self.__categories)

    @property
    def sub_categories_data(self) -> list['data_classes.Category']:
        """
        List of dataclasses without parent categories.
        :return: list of dataclasses
        """
        return list(filter(lambda cat: cat.parent_category_id is not None, self.__categories))
