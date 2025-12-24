from src.instruments.base_instrument import BaseInstrument

class MockSource6221(BaseInstrument):      # Current Source
    def __init__(self):                         # This runs when this class is called/made into an object. Currently, it runs the
        super().__init__("Current Source")      # initializer of the base instrument class, and sets the current to nothing and the output state to off.
        self.current = None
        self.output_state = False

    def set_current(self, current):        # Sets the current to the provided number. Can be a decimal.
        self.current = current

    def set_output(self, state: bool):     # Sets the current output state to on or off (use True/False)
        self.output_state = state

    def read(self):                        # If the output state is 'on' or True, it returns the current 'current' value
        if self.output_state:
            return self.current
        else:
            return None