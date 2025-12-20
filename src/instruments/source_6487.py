from src.instruments.base_instrument import BaseInstrument

class Source6487(BaseInstrument):       # Voltage Source
    def __init__(self):
        BaseInstrument.__init__(self)
        self.voltage = None
        self.output_state = False

    def set_voltage(self, voltage):
        self.voltage = voltage

    def set_output(self, state: bool):
        self.output_state = state

    def read(self):
        if self.output_state:
            return self.voltage
        else:
            return None