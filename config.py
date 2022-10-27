import json
import pathlib
from os import path


class Config:

    def __init__(self, base_url: str, config_file_name: str = 'config.json'):
        self.__base_url = base_url
        self.__config_file_name = config_file_name
        self.__config = {}
        self.__load_config_defaults()
        self.__load_config()
        self.__project_dir = pathlib.Path(__file__).parent.resolve()

    def __load_config_defaults(self):
        with open('config_defaults.json') as conf_def:
            self.__config = json.load(conf_def)

    def __load_config(self):
        try:
            with open(self.__config_file_name) as conf:
                config_user = json.load(conf)
        except (FileExistsError, FileNotFoundError):
            pass
        else:
            self.__config.update(config_user)

    @property
    def config(self) -> dict:
        return self.__config

    @property
    def output_directory(self) -> str:
        return self.__config.get('output_directory')

    @property
    def output_directory_abs(self) -> str:
        return path.join(self.__project_dir, self.__config.get('output_directory'))

    @property
    def categories(self) -> list[str]:
        return self.__config.get('categories')

    @property
    def delay_range_s(self) -> int | str:
        return self.__config.get('delay_range_s')

    @property
    def max_retries(self) -> int:
        return self.__config.get('max_retries')

    @property
    def headers(self) -> dict[str, str]:
        return self.__config.get('headers')

    @property
    def logs_dir(self) -> str:
        return self.__config.get('logs_dir')

    @property
    def logs_dir_abs(self) -> str:
        return path.join(self.__project_dir, self.__config.get('logs_dir'))

    @property
    def restart(self) -> dict[str, int | float]:
        return self.__config.get('restart')

    @property
    def restart__restart_count(self) -> int:
        return self.restart.get('restart_count')

    @property
    def restart__interval_m(self) -> float:
        return self.restart.get('interval_m')

    @property
    def base_url(self) -> str:
        return self.__base_url
