import re
from typing import Any

from data_classes import Item


class PostProcessing:

    def __init__(self, value: Any):
        self.value = value

    def line_process(self, item: 'Item'):
        # TODO: change prices if discount
        # TODO: remove unused amounts based on measuring
        pass

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

