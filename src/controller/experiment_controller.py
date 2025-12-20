class ExperimentController:
    def __init__(self, switch, current_source, voltage_source):
        self.switch = switch
        self.current_source = current_source
        self.voltage_source = voltage_source

    def run_single_channel_test(self, channel: int, current: float, voltage: float):
        self.switch.open_all()
        self.switch.close_channel(channel)

        self.current_source.set_current(current)
        self.current_source.set_output(True)

        self.voltage_source.set_voltage(voltage)

        value = self.voltage_source.read()

        self.current_source.set_output(False)
        return value
