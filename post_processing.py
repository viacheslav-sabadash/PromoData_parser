import re
from abc import ABCMeta, abstractmethod
from typing import Any
from urllib.parse import urljoin

import data_classes


class PostProcessingBase(metaclass=ABCMeta):
    """
    We must implement at least line_process() method in PostProcessing
    """

    @abstractmethod
    def line_process(self):
        ...

    @abstractmethod
    def get_text(self):
        ...

    @staticmethod
    def parse_first_int_(val: str) -> int:
        try:
            result = re.findall(r'\d+', val)[0]
        except IndexError:
            result = 0
        return result

    @staticmethod
    def parse_first_int(val) -> int:
        val = str(val)
        try:
            result = re.findall(r'\d+', val)[0]
        except IndexError:
            result = 0
        return result

    @staticmethod
    def convert_weight(val) -> int:
        val = str(val)
        if re.findall(r'г|g', val, re.IGNORECASE):
            return PostProcessingBase.parse_first_int_(val)
        elif re.findall(r'кг|kg', val, re.IGNORECASE):
            return PostProcessingBase.parse_first_int_(val) * 1000
        elif re.findall(r'мг|mg', val, re.IGNORECASE):
            return PostProcessingBase.parse_first_int_(val) // 1000
        else:
            return None

    @staticmethod
    def convert_volume(val) -> int:
        val = str(val)
        if re.findall(r'л|lir', val, re.IGNORECASE):
            return PostProcessingBase.parse_first_int_(val) // 1000
        elif re.findall(r'мл|mil|ml', val, re.IGNORECASE):
            return PostProcessingBase.parse_first_int_(val)
        else:
            return None

    @staticmethod
    def convert_amount(val) -> int:
        val = str(val)
        if re.findall(r'\D', val.strip(), re.IGNORECASE) or not val:
            return None
        return PostProcessing.parse_first_int_(val)


class PostProcessing(PostProcessingBase):

    def __init__(self, value: Any, base_url: str):
        self.value = value
        self.base_url = base_url

    def line_process(self) -> 'data_classes.Item':
        """
        Final fields processing. For example, swap some fields or remove unnecessary.
        :return:
        """

        # need to change prices when price_promo exist
        if self.value.get('price_promo', '') and self.value.get('price', ''):
            price = self.value.get('price_promo', '')
            price_promo = self.value.get('price', '')
        else:
            price = self.value.get('price', '')
            price_promo = None

        return data_classes.Item(
            price_datetime=self.value.get('price_datetime', ''),
            sku_name=self.value.get('sku_name', ''),
            sku_category=self.value.get('sku_category', ''),
            sku_link=self.value.get('sku_link', ''),
            price=price,
            price_promo=price_promo,
            sku_status=self.value.get('sku_status', ''),
            sku_barcode=self.value.get('sku_barcode', ''),
            sku_article=self.value.get('sku_article', ''),
            sku_country=self.value.get('sku_country', ''),
            sku_weight_min=PostProcessing.convert_weight(self.value.get('sku_weight_min', '')),
            sku_volume_min=PostProcessing.convert_volume(self.value.get('sku_volume_min', '')),
            sku_quantity_min=PostProcessing.convert_amount(self.value.get('sku_quantity_min', '')),
            sku_images=self.value.get('sku_images', ''),
        )

    @property
    def get_text(self) -> str:
        """
        Return tag text if 'text' attribute exist, else return empty string
        :return: tag.text
        """
        return getattr(self.value, 'text') if hasattr(self.value, 'text') else ''

    @property
    def parse_first_int(self) -> int:
        val = str(self.value)
        try:
            result = re.findall(r'\d+', val)[0]
        except IndexError:
            result = 0
        return result

    @property
    def bool(self) -> bool:
        return bool(self.value)

    @property
    def int(self) -> int:
        return int(self.value)

    @property
    def get_clean_country(self) -> str:
        try:
            result = self.value.split(':')[1].strip()
        except IndexError:
            result = ''
        return result

    @property
    def map_images(self) -> list[str]:
        return list(
            map(
                lambda im: urljoin(im.get('src'), self.base_url) if im.get('src') else '',
                self.value
            )
        )
