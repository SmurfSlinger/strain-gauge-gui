from src.instruments.base_instrument import BaseInstrument

class MockSource6487(BaseInstrument):       # Voltage Source
    def __init__(self):
        super().__init__("Voltage Source")
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