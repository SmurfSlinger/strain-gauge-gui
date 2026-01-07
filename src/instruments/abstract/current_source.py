from abc import abstractmethod, ABC

from src.instruments.abstract.base_instrument import BaseInstrument

class CurrentSource(ABC, BaseInstrument):      # Current Source
    def __init__(self):
        BaseInstrument.__init__(self)
        self.current = None
        self.output_state = False

    @abstractmethod             # This must be defined in child classes
    def set_current(self, current):
        pass

    @abstractmethod             # This must be defined in child classes
    def set_output(self, state: bool):
        pass

    @abstractmethod             # This must be defined in child classes
    def read(self):
        pass

