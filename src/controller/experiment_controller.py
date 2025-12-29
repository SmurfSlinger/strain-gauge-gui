from src.controller.resistance_measurement_mode import ResistanceMeasurementMode


from src.controller.resistance_measurement_mode import ResistanceMeasurementMode
from src.controller.resistance_result import ResistanceResult

class ExperimentController:
    def __init__(self, switch, current_source, voltage_source):
        self.switch = switch
        self.current_source = current_source
        self.voltage_source = voltage_source

    def run_resistance_test(self, channel1: int, channel2: int, current: float, voltage: float):
        self.switch.open_all()
        try:
            self.switch.close_channel(channel1)
            self.switch.close_channel(channel2)

            self.current_source.set_current(current)
            self.current_source.set_output(True)

            # If you’re using the 6487 as a measurement endpoint, you may not need set_voltage at all
            # Keep it only if your experiment truly applies a bias voltage via 6487:
            self.voltage_source.set_voltage(voltage)
            self.voltage_source.set_output(True)

            measured_v = self.voltage_source.read()

            resistance = measured_v / current if current != 0 else None

            return ResistanceResult(
                mode="current_driven",
                channel1=channel1,
                channel2=channel2,
                set_current_amps=current,
                set_voltage_volts=voltage,
                measured_voltage_volts=measured_v,
                resistance_ohms=resistance,
            )
        finally:
            self.current_source.set_output(False)
            self.voltage_source.set_output(False)
            self.switch.open_all()

    def run_channel_test(self, channel1: int, channel2: int, current: float, voltage: float):
        """
           Runs a double-channel test by:
           - Selecting the two switch channels
           - Sourcing a fixed current
           - Applying a target voltage
           - Reading back the measured voltage from the source

           Note:
               Voltage source is used as the measurement point in this experiment
               (mocked behavior during offline development).
           """

        self.switch.open_all()
        try:
            self.switch.close_channel(channel1)
            self.switch.close_channel(channel2)

            self.current_source.set_current(current)
            self.voltage_source.set_voltage(voltage)

            self.current_source.set_output(True)
            self.voltage_source.set_output(True)

            value = self.voltage_source.read()
            return value
        finally:
            self.current_source.set_output(False)
            self.voltage_source.set_output(False)
            self.switch.open_all()


