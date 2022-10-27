import csv
import os
from logging import Logger
from os import path
from typing import Any

from .config import Config
from .log_lib import get_logger


class CsvHelper:
    """
    Save data to csv
    """
    logger = None

    def __init__(self, config_: 'Config'):
        self._config = config_
        if not self.logger:
            self.logger: Logger = get_logger(self._config.logs_dir_abs, 'CSV')

    def _path(self, filename: str):
        """
        Absolute path maker
        :param filename: filename
        :return: Absolute path
        """
        return path.join(self._config.output_directory_abs, filename)

    def erase_file(self, file_name: str):
        with open(self._path(file_name), 'w') as csvfile:
            csvfile.write('')

    def save_data(self, file_name: str, data: list):
        """
        Save dataclass list to csv file
        :param file_name: filename of csv file
        :param data: list of dataclasses with repr=True fields to select it for save
        :return: None
        """
        if len(data) == 0 or not hasattr(data[0], 'fields_to_print'):
            return
        with open(self._path(file_name), 'w') as csvfile:
            fieldnames = data[0].fields_to_print
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')

            writer.writeheader()
            for row in data:
                writer.writerow(row.to_print_dict)

        self.logger.info(f'Saved {file_name}')

    def append_data(self, file_name: str, data_class: Any):
        file_exist = False
        if os.path.exists(self._path(file_name)):
            file_exist = True

        with open(self._path(file_name), 'a') as csvfile:
            fieldnames = data_class.fields_to_print
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            if not file_exist:
                writer.writeheader()
            writer.writerow(data_class.to_print_dict)

        self.logger.info(f'Appended line to {file_name}')