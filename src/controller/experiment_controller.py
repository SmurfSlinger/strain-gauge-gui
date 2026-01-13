from dataclasses import dataclass


@dataclass
class ResistanceResult:
    current_amps: float
    measured_voltage: float
    resistance_ohms: float



class ExperimentController:
    def __init__(self, switch, current_source, voltmeter):
        self.switch = switch
        self.current_source = current_source
        self.voltmeter = voltmeter

    def run_current_driven_resistance(
        self,
        channel_force_pos: int,
        channel_force_neg: int,
        current_amps: float
    ) -> ResistanceResult:
        """
        Perform a simple current-driven resistance measurement.

        - Close two force channels
        - Force a current
        - Measure voltage
        - Compute resistance
        """

        # Route
        self.switch.open_all()
        self.switch.close_channel(channel_force_pos)
        self.switch.close_channel(channel_force_neg)

        # Excite
        self.current_source.set_current(current_amps)
        self.current_source.set_output(True)

        # Measure
        measured_voltage = self.voltmeter.measure_voltage()

        # Cleanup
        self.current_source.set_output(False)
        self.switch.open_all()

        resistance = measured_voltage / current_amps if current_amps != 0 else 0.0

        return ResistanceResult(
            current_amps=current_amps,
            measured_voltage=measured_voltage,
            resistance_ohms=resistance
        )