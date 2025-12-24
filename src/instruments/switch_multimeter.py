from abc import abstractmethod, ABC

from src.instruments.base_instrument import BaseInstrument

class SwitchMultimeter(ABC):
    @abstractmethod
    def close_channel(self, channel: int):
        pass

    @abstractmethod
    def open_channel(self, channel: int):
        pass

    @abstractmethod
    def open_all(self):
        pass