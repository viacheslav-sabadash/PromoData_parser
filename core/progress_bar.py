import enlighten


class ProgressBar:

    def __init__(self):
        self.__manager = enlighten.get_manager()
        self.total_bar = self.__manager.counter(total=100, desc='Total', unit='progress')
        self.current_bar = None

    def update_total(self, value: int):
        self.total_bar.update(value)

    def init_current(self, total=100, desc: str = 'Total', unit: str = 'progress'):
        self.current_bar = self.__manager.counter(total=total, desc=desc, unit=unit)

    def update_current(self, value: int | None = None):
        if value:
            self.current_bar.update(value)
        else:
            self.current_bar.update()
