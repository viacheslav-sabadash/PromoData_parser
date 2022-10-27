from bs4 import BeautifulSoup
from ordered_set import OrderedSet

import config
import data_classes
from base_parser import BaseParser
from category import Category
from page_loader import PageLoader

PARSER = 'html.parser'


class Paginator(BaseParser, PageLoader):
    """
    Collect list of paginated pages
    """

    def __init__(
            self,
            config_: 'config.Config',
            categories: 'Category',
            rules: list[dict]
    ):
        self._config = config_
        self.__categories = categories
        self._rules = rules
        self._html: str = ''
        self.__pages: OrderedSet['data_classes.Page'] = OrderedSet()
        super(Paginator, self).__init__()

    def parse_all(self):
        """
        Handle for parser starting
        :return: None
        """
        self.logger.info(f' >>> Starting Pagination parsing for {len(self.__categories.categories_data)} categories')

        for category in self.__categories.sub_categories_data:
            self.__pages.add(  # first page
                data_classes.Page(
                    uniq_name=f'{category.parent_category}|{category.name}|1',
                    url=category.url,
                    parent_category_id=category.parent_category_id,
                    parent_category=category.parent_category,
                    category_id=category.id,
                    category=category.name,
                )
            )

            category_url = category.url
            while True:
                self.get_html(category_url)
                page_soup = BeautifulSoup(self._html, PARSER)

                for page in self._parse_rules(page_soup):
                    self.__pages.add(
                        data_classes.Page(
                            uniq_name=f'{category.parent_category}|{category.name}|{page.text}',
                            url=self.abs_url(page.get('href', '')),
                            parent_category_id=category.parent_category_id,
                            parent_category=category.parent_category,
                            category_id=category.id,
                            category=category.name,
                        )
                    )
                    # print(
                    #     '[Paginator]: ',
                    #     f'{category.parent_category}|{category.name}|{page.text}',
                    #     ' -- ',
                    #     self.abs_url(page.get('href', ''))
                    # )

                if self.__pages and category_url == self.__pages[-1].url:  # last same as just parsed
                    break
                else:
                    category_url = self.__pages[-1].url  # last url on page pagination

        self.logger.info(f' <<< Pagination parsing complete. Result total = {len(self.__pages)}')

    @property
    def pagination_data(self) -> list['data_classes.Page']:
        """
        List of dataclasses.
        :return: list of dataclasses
        """
        return list(self.__pages)
