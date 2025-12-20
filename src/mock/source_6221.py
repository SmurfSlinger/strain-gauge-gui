from src.instruments.base_instrument import BaseInstrument

class MockSource6221(BaseInstrument):      # Current Source
    def __init__(self):
        super().__init__("Current Source")
        self.current = None
        self.output_state = False

    def set_current(self, current):
        self.current = current

    def set_output(self, state: bool):
        self.output_state = state

    def read(self):
        if self.output_state:
            return self.current
        else:
            return None