class ExperimentController:
    def __init__(self, switch, current_source, voltage_source):
        self.switch = switch
        self.current_source = current_source
        self.voltage_source = voltage_source

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
        self.switch.close_channel(channel1)
        self.switch.close_channel(channel2)

        self.current_source.set_current(current)
        self.voltage_source.set_voltage(voltage)
        self.current_source.set_output(True)

        value = self.voltage_source.read()

        self.current_source.set_output(False)
        self.switch.open_all()

        return value
