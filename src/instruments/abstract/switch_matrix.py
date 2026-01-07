from abc import abstractmethod, ABC
from src.instruments.abstract.base_instrument import BaseInstrument


class SwitchMatrix(ABC, BaseInstrument):
    def __init__(self, controller):
        self.controller = controller

    @abstractmethod             # This must be defined in child classes
    def close_channel(self, channel: int):
        pass

    @abstractmethod             # This must be defined in child classes
    def open_channel(self, channel: int):
        pass

    @abstractmethod             # This must be defined in child classes
    def open_all(self):
        pass

    @abstractmethod
    def query(self, command: str):
        pass
