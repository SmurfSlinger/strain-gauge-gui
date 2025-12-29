from abc import abstractmethod, ABC

from src.instruments.abstract.base_instrument import BaseInstrument

class VoltageSource(ABC):       # Voltage Source
    def __init__(self):
        BaseInstrument.__init__(self)
        self.voltage = None
        self.output_state = False

    @abstractmethod             # This must be defined in child classes
    def set_voltage(self, voltage):
        pass

    @abstractmethod             # This must be defined in child classes
    def set_output(self, state: bool):
        pass

    @abstractmethod             # This must be defined in child classes
    def read(self):
        pass