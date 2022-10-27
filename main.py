# encoding: utf-8
"""
Universal Parser
"""

import re
import time
from logging import Logger

from category import Category
from core.config import Config
from core.csv_helper import CsvHelper
from core.log_lib import get_logger
from item import Item
from items_list import ItemsList
from paginator import Paginator
from parent_category import ParentCategory
from post_processing import PostProcessing

URL = 'https://zootovary.ru/'

PARENT_CATEGORIES_RULES = [
    {
        'call': 'find_all',
        'args': {
            'name': 'a',
            'class_': re.compile(r'^catalog-menu-'),
            'href': True
        }
    }
]

CHILD_CATEGORIES_RULES = [
    {
        'call': 'find_next',
        'args': {
            'name': 'div',
            'class_': 'popup-items'
        }
    },
    {
        'call': 'find_all',
        'args': {
            'name': 'a',
            'href': True
        },
        'add_url_params': {'pc': 60}  # 60 (max) items per page
    },
]

PAGINATION_RULES = [
    {
        'call': 'find',
        'args': {
            'name': 'div',
            'class_': 'navigation'
        }
    },
    {
        'call': 'find_all',
        'args': {
            'name': 'a',
            'text': re.compile(".*[0-9]+.*"),  # only numeric pages, skip '>>'
            'href': True
        },
        'add_url_params': {'pc': 60}  # 60 (max) items per page
    },
]

ITEMS_LIST_RULES = [
    {
        'call': 'find',
        'args': {
            'name': 'div',
            'class_': 'catalog-section'
        }
    },
    {
        'call': 'find_all',
        'args': {
            'name': 'a',
            'class_': 'name',
            'href': True
        }
    },
]

ITEM_RULES = [
    {
        'call': 'find_all',
        'args': {
            'name': 'tr',
            'class_': 'b-catalog-element-offer'
        }
    },
]

ITEM_CHILD_VALUE_RULES = {
    'price': {
        'call': 'find',
        'args': {
            'name': 'span',
            'class_': 'catalog-price'
        },
        'post_processing': [
            'get_text',
            'parse_all_int',
        ]
    },
    'price_promo': {
        'call': 'find',
        'args': {
            'name': 's',
            'style': 'color:#000000;'
        },
        'post_processing': [
            'get_text',
            'parse_all_int',
        ]
    },
    'sku_status': {
        'call': 'find',
        'args': {
            'name': 'div',
            'class_': 'catalog-item-no-stock'
        },
        'post_processing': [
            'get_text',
            'invert_bool',
            'int'
        ]
    },
    'sku_barcode': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class^="tg-yw"] b[style="color:#c60505;"]',
        },
        'post_processing': [
            'get_text',
        ]
    },
    'sku_article': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class$="b-catalog-element-offer-first-col"] > br + b',
        },
        'post_processing': [
            'get_text',
        ]
    },
    'sku_weight_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class$="b-catalog-element-offer-first-col"] + '
                        'td[class^="tg-yw"] + td[class^="tg-yw"]',
        },
        'post_processing': [
            'get_text',
        ]
    },
    'sku_volume_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class$="b-catalog-element-offer-first-col"] + '
                        'td[class^="tg-yw"] + td[class^="tg-yw"]',
        },
        'post_processing': [
            'get_text',
        ]
    },
    'sku_quantity_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class$="b-catalog-element-offer-first-col"] + '
                        'td[class^="tg-yw"] + td[class^="tg-yw"]',
        },
        'post_processing': [
            'get_text',
        ]
    },
}

ITEM_GLOB_VALUE_RULES = {
    'sku_name': {
        'call': 'select_one',
        'args': {
            'selector': 'div.catalog-element-top > div.catalog-element-right-area > div > h1',
        },
        'post_processing': [
            'get_text',
        ]
    },
    'sku_country': {
        'call': 'select_one',
        'args': {
            'selector': 'div.catalog-element-offer.active > div.catalog-element-offer-left > p',
        },
        'val': {'getattribute': 'text'},
        'post_processing': [
            'get_text',
            'get_clean_country',
        ]
    },
    'sku_images': {
        'call': 'select',
        'args': {
            'selector': 'div[class^="catalog-element-small-picture"] img',
        },
        'val': {'get': 'src'},
        'post_processing': [
            'map_images'
        ]
    },
}


def main(config_: Config):
    csv_helper = CsvHelper(config_)

    parent_categories = ParentCategory(config_, PARENT_CATEGORIES_RULES)
    parent_categories.parse()

    csv_helper.save_data('parent_categories_data.csv', parent_categories.categories_data)

    categories = Category(config_, parent_categories, CHILD_CATEGORIES_RULES)
    categories.parse_all()

    csv_helper.save_data('categories_data.csv', categories.categories_data)
    csv_helper.save_data('sub_categories_data.csv', categories.sub_categories_data)

    cat_pagination = Paginator(config_, categories, PAGINATION_RULES)
    cat_pagination.parse_all()

    csv_helper.save_data('pagination_data.csv', cat_pagination.pagination_data)

    items_list = ItemsList(config_, cat_pagination, ITEMS_LIST_RULES)
    items_list.parse_all()

    csv_helper.save_data('items_list_data.csv', items_list.items_list_data)

    csv_helper.erase_file('items.csv')
    items = Item(
        config_,
        items_list,
        ITEM_RULES,
        ITEM_CHILD_VALUE_RULES,
        ITEM_GLOB_VALUE_RULES,
        PostProcessing,
        'items.csv'
    )
    items.parse_all()

    # csv_helper.save_data('items.csv', items.items_data)


if __name__ == '__main__':

    config = Config(URL)
    logger: Logger = get_logger(config.logs_dir_abs, 'MAIN')

    for attempt in range(config.restart__restart_count):
        try:
            main(config)
        except Exception as ex:
            logger.warning(f'main() process broken by: {str(ex)}')
            logger.info(f'Retry {attempt + 1} from {config.restart__restart_count} '
                        f'after {config.restart__interval_m:1.1f}m sleep')
            time.sleep(config.restart__interval_m * 60)
