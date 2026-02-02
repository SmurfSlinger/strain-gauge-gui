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

        self._current_amps = 0.0
        self._armed = False

    def begin_constant_current_mode(self, ch_pos: int, ch_neg: int, current_amps: float) -> None:
        # Configure routing ONCE at start
        self.switch.open_all()
        self.switch.close_channel(int(ch_pos))
        self.switch.close_channel(int(ch_neg))

        # Configure source ONCE at start
        self.current_source.set_current(float(current_amps))
        self.current_source.set_output(True)

        self._current_amps = float(current_amps)
        self._armed = True

    def take_sample(self) -> ResistanceResult:
        if not self._armed:
            raise RuntimeError("ExperimentController not armed. Call begin_constant_current_mode() first.")

        v = self.voltmeter.measure_voltage()
        i = self._current_amps
        r = (v / i) if i != 0 else 0.0

        return ResistanceResult(current_amps=i, measured_voltage=v, resistance_ohms=r)

    def stop_outputs(self) -> None:
        # Fast “stop measuring” safety: turn source off
        try:
            self.current_source.set_output(False)
        finally:
            self._armed = False

    def safe_idle(self) -> None:
        # Full “reset hardware” safety: open relays + output off
        try:
            self.current_source.set_output(False)
        except Exception:
            pass
        try:
            self.switch.open_all()
        except Exception:
            pass
        self._armed = False
