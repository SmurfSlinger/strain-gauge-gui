from src.instruments.abstract.base_instrument import BaseInstrument

class MockSource6487:
    def __init__(self, switch=None, current_source=None):
        self.switch = switch
        self.current_source = current_source
        self.simulated_resistance = 120.0  # ohms

    def measure_voltage(self) -> float:
        if not self.current_source or not self.current_source.output_state:
            return 0.0

        if self.switch and not self.switch.closed_channels:
            return 0.0

        return self.current_source.current * self.simulated_resistance
