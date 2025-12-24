from abc import abstractmethod, ABC

from src.instruments.base_instrument import BaseInstrument

class VoltageSource(ABC):       # Voltage Source
    def __init__(self):
        BaseInstrument.__init__(self)
        self.voltage = None
        self.output_state = False

    @abstractmethod
    def set_voltage(self, voltage):
        pass

    @abstractmethod
    def set_output(self, state: bool):
        pass

    @abstractmethod
    def read(self):
        pass