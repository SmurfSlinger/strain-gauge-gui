from src.instruments.abstract.base_instrument import BaseInstrument

class MockSource6487(BaseInstrument):
    """Mock Keithley 6487 acting as a voltmeter (Method A)."""

    def __init__(self):
        super().__init__("Keithley 6487 (Voltmeter)")
        self._simulated_voltage: float = 0.0

    def set_simulated_voltage(self, voltage: float) -> None:
        self._simulated_voltage = voltage

    def measure_voltage(self) -> float:
        return self._simulated_voltage
