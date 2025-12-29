from src.instruments.abstract.base_instrument import BaseInstrument

class MockSource6487(BaseInstrument):       # Voltage Source
    def __init__(self, switch, current_source):                         # This runs when this class is called/made into an object. Currently, it runs the
        super().__init__("Voltage Source") # parent initializer, sets the current voltage to nothing, and sets the output state to off.
        self._switch = switch
        self._current_source = current_source
        self.voltage = None
        self.output_state = False

    def set_voltage(self, voltage):             # Sets the object's voltage to the provided value, can be a decimal.
        self.voltage = voltage

    def set_output(self, state: bool):          # Sets the output state to the provided value, True/False (on or off).
        self.output_state = state

    def read(self):                             # If output is on, it returns the current voltage. Otherwise, returns 0.0
        if not self._current_source.output_enabled:
            return 0.0

        if not self._switch.closed_channels:
            return 0.0

        return self.voltage