from abc import abstractmethod, ABC

from src.instruments.base_instrument import BaseInstrument

class CurrentSource(ABC):      # Current Source
    def __init__(self):
        BaseInstrument.__init__(self)
        self.current = None
        self.output_state = False

    @abstractmethod
    def set_current(self, current):
        pass

    @abstractmethod
    def set_output(self, state: bool):
        pass

    @abstractmethod
    def read(self):
        pass

