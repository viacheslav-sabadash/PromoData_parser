from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any


class Printable:
    @property
    def fields_to_print(self) -> list[str]:
        """
            List of dataclass fields which NOT marked as field(repr=False).
            Help to print or save only necessary fields.
        """
        return [f.name for f in fields(self.__class__) if f.repr]

    @property
    def to_print_dict(self) -> dict[str, Any]:
        return {key: self.__dict__.get(key, None) for key in self.fields_to_print}


@dataclass(frozen=True, eq=True, order=False, unsafe_hash=False)
class Category(Printable):
    id: int
    name: str
    url: str = field(repr=False, default='')
    parent_category_id: int | None = field(default=None)
    parent_category: str | None = field(repr=False, default='')


@dataclass(frozen=True, eq=True, order=False, unsafe_hash=False)
class Page(Printable):
    uniq_name: str
    url: str
    parent_category_id: int
    parent_category: str | None
    category_id: int
    category: str | None

    # def __hash__(self):
    #     return hash(self.uniq_name)
    #
    # def __eq__(self, other):
    #     return self.uniq_name == other.uniq_name


@dataclass(frozen=True, eq=True, order=False, unsafe_hash=False)
class ItemList(Page):
    item_url: str


@dataclass
class Item(Printable):
    price_datetime: datetime
    sku_name: str
    sku_category: str
    sku_link: str
    price: int = field(default=0)
    price_promo: int | None = field(default=None)
    sku_status: int = field(default=0)
    sku_barcode: str = field(default='')
    sku_article: str = field(default='')
    sku_country: str = field(default='')
    sku_weight_min: int | None = field(default=None)
    sku_volume_min: int | None = field(default=None)
    sku_quantity_min: int | None = field(default=None)
    sku_images: list[str] = field(default_factory=list[str])

    def __eq__(self, other):
        return self.sku_article == other.sku_article and \
              self.sku_barcode == other.sku_barcode
