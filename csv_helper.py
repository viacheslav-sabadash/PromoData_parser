import csv
from os import path

import config


class CsvHelper:
    def __init__(self, config_: 'config.Config'):
        self.__config = config_

    def _path(self, filename: str):
        return path.join(self.__config.output_directory_abs, filename)

    def save_data(self, file_name: str, data: list):
        if len(data) == 0 or not hasattr(data[0], 'fields_to_print'):
            return
        with open(self._path(file_name), 'w') as csvfile:
            fieldnames = data[0].fields_to_print
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')

            writer.writeheader()
            for row in data:
                writer.writerow(row.to_print_dict)
