import re
from abc import ABCMeta, abstractmethod
from typing import Any

from data_classes import Item


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


class PostProcessing(PostProcessingBase):

    def __init__(self, value: Any):
        self.value = value

    def line_process(self, item: 'Item'):
        # TODO: change prices if discount
        # TODO: remove unused amounts based on measuring
        pass

    @property
    def get_text(self) -> str:
        """
        Return tag text if 'text' attribute exist, else return empty string
        :return: tag.text
        """
        return getattr(self.value, 'text') if hasattr(self.value, 'text') else ''

    @property
    def parse_first_int(self):
        try:
            result = re.findall(r'\d+', self.value)[0]
        except IndexError:
            result = 0
        return result

    @property
    def bool(self):
        return bool(self.value)

    @property
    def int(self):
        return int(self.value)

    @property
    def convert_amount(self):
        return self.value

    @property
    def get_clean_country(self):
        try:
            result = self.value.split(':')[1].strip()
        except IndexError:
            result = ''
        return result

    @property
    def map_images(self):
        # TODO: abs_path
        return list(map(lambda im: im.get('src'), self.value))
