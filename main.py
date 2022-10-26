import re

from category import Category
from config import Config
from csv_helper import CsvHelper
from item import Item
from items_list import ItemsList
from page_loader import PageLoader
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
            'parse_first_int',
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
            'parse_first_int',
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
            'bool',
            'int'
        ]
    },
    'sku_article': {
        'call': 'select_one',
        'args': {
            'selector': 'td[class^="tg-yw"] b[style="color:#c60505;"]',
        },
    },
    'sku_weight_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td + td + td > b + br > b',
        },
        'post_processing': [
            'get_text',
            'convert_amount',
        ]
    },
    'sku_volume_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td + td + td > b + br > b',
        },
        'post_processing': [
            'get_text',
            'convert_amount',
        ]
    },
    'sku_quantity_min': {
        'call': 'select_one',
        'args': {
            'selector': 'td + td + td > b + br > b',
        },
        'post_processing': [
            'get_text',
            'convert_amount',
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

config = Config(URL)
# page_loader = PageLoader(config)
csv_helper = CsvHelper(config)


# parent_categories = ParentCategory(config, PARENT_CATEGORIES_RULES)
# parent_categories.parse()
# print(parent_categories.categories)
#
# csv_helper.save_data('parent_categories_data.csv', parent_categories.categories_data)
#
# categories = Category(config, parent_categories, CHILD_CATEGORIES_RULES)
# categories.parse_all()
# print(categories.categories_data)
#
# csv_helper.save_data('categories_data.csv', categories.categories_data)
# csv_helper.save_data('sub_categories_data.csv', categories.sub_categories_data)
#
# cat_pagination = Paginator(config, categories, PAGINATION_RULES)
# cat_pagination.parse_all()
# print(cat_pagination.pagination_data)
#
# csv_helper.save_data('pagination_data.csv', cat_pagination.pagination_data)

# Tmp:
import data_classes
class PaginatorFake:
    data = [
        data_classes.Page(
            uniq_name="Собаки|Корм сухой|1",
            url="https://zootovary.ru/catalog/tovary-i-korma-dlya-sobak/korm-sukhoy/?pc=60",
            parent_category_id=0,
            parent_category="Собаки",
            category_id=1,
            category="Корм сухой",
        ),
        data_classes.Page(
            uniq_name="Собаки|Корм сухой|2",
            url="https://zootovary.ru/catalog/tovary-i-korma-dlya-sobak/korm-sukhoy/?pc=60&PAGEN_1=2&pc=60",
            parent_category_id="0",
            parent_category="Собаки",
            category_id="1",
            category="Корм сухой",
        )
    ]

    @property
    def pagination_data(self) -> list['data_classes.Page']:
        return list(self.data)

cat_pagination = PaginatorFake()
print(cat_pagination.pagination_data)
# /Tmp

items_list = ItemsList(config, cat_pagination, ITEMS_LIST_RULES)
items_list.parse_all()
print(items_list.items_list_data[:200])

csv_helper.save_data('items_list_data.csv', items_list.items_list_data)

items = Item(config, items_list, ITEM_RULES, ITEM_CHILD_VALUE_RULES, ITEM_GLOB_VALUE_RULES, PostProcessing)
items.parse_all()
print(items_list.items_data)

csv_helper.save_data('items.csv', items_list.items_data)
