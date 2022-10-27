# Universal Parser

## Installation

```shell
cd [ProjectDir]

mkdir logs
mkdir out

pip install -r requirements.txt
```

## Run

```shell
python main.py
```

## Config

Save custom config values to `config.json` (You can skip default values).
Defaults and config example stored in `config_defaults.json`

### Example config.json

```json
{
  "output_directory": "out",
  "categories": ["Собаки", "Кошки"],
  "delay_range_s": "5-15"
}
```

## Parser rules

### Rules examples

```python
PARENT_CATEGORIES_RULES = [
    {
        'call': 'find_all',
        'args': {
            'name': 'a',
            'class_':  re.compile(r'^catalog-menu-'),
            'href': True
        }
    }
]
```
*`re` module has already been imported in BaseParser 

In this example BeautifulSoup instance run:
```python
find_all(name='a', class_=re.compile(r'^catalog-menu-'))
```


```python
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
```

In this example BeautifulSoup instance run consistently:
```python
find_next(name='div', class_='popup-items').find_all('a', href=True)
```
and if parser find `<a href="...">` tags append to all href,s queries from `add_url_params`
In current example append: `?pc=60` or `&pc=60` depending on whether the current URL 
already has parameters or not.


The rules for goods work in a special way.
First, the general rule is applied, as in the examples above:

```python
ITEM_RULES = [
    {
        'call': 'find_all',
        'args': {
            'name': 'tr',
            'class_': 'b-catalog-element-offer'
        }
    },
]
```

Now we need to have two versions of the rules for the entire product page and for its variations, for example, 
if there are several types of packaging on one page:

```python
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
}

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
}
```

That's not all! Since after receiving the data, there may be different rules 
for adding them to the final data, for example, it is necessary to change 
the columns of the price and discount price, provided there is a second one, 
or to bring the units of measurement to a single value, then a common class of 
post-processing rules in file `post_processing.py` is needed that will take over the implementation of the methods. 
These methods can be used later in the rules with a key `post_processing` 
(already exist in rules examples above).

```python
class PostProcessing(PostProcessingBase):

    def __init__(self, value: Any, base_url: str):
        self.value = value
        self.base_url = base_url

    def line_process(self) -> 'data_classes.Item':  # necessary rule, run for each line of data
        ...

    @property
    def get_text(self) -> str:
        return getattr(self.value, 'text') if hasattr(self.value, 'text') else ''

```
*all methods except `line_process()` must be decorated as `@property`.
*`line_process()` must return dataclass with result fields.

## CsvHelper

CsvHelper class have method `save_data()` to save in to csv file dataclasses list.
This method save only default fields or fields marked with `repr=True`.

### Example

```python
@dataclass(frozen=True, eq=True, order=False, unsafe_hash=False)
class Category(Printable):
    id: int
    name: str
    url: str = field(repr=False, default='')
    parent_category_id: int | None = field(default=None)
    parent_category: str | None = field(repr=False, default='')
```

Instance of dataclass above saved only fields: **id**, **name**, **parent_category_id**.
Fields: **url** and **parent_category** will be ignored as `field(repr=False)`

### Save data line by line

class `Item` can store data to csv file line by line. To activate this need add to Item __init__ csv_filename='[some_file_name.csv]'.
It is also advisable to clean the file before starting `Item`. There is a built-in method `erase_file()` in `CsvHelper` for this:

```python
csv_helper = CsvHelper(config_)
csv_helper.erase_file('items.csv')
```
