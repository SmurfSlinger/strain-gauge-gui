from dataclasses import dataclass


@dataclass
class ResistanceResult:
    current_amps: float
    measured_voltage: float
    resistance_ohms: float
    measurement_mode: str  # "current_driven" or "voltage_driven"



class ExperimentController:
    def __init__(self, switch, current_source, voltmeter):
        self.switch = switch
        self.current_source = current_source
        self.voltmeter = voltmeter

        self._current_amps = 0.0
        self._voltage_volts = 0.0
        self._armed = False
        self._mode = "current_driven"  # "current_driven" or "voltage_driven"

    def begin_constant_current_mode(self, ch_pos: int, ch_neg: int, current_amps: float, 
                                    sense_ch_pos: int | None = None, sense_ch_neg: int | None = None) -> None:
        """Current-driven mode: 6221 sources current, 6487 measures voltage."""
        # Configure routing ONCE at start
        self.switch.open_all()
        self.switch.close_channel(int(ch_pos))
        self.switch.close_channel(int(ch_neg))
        
        # For 4-wire measurements, also close sense channels
        if sense_ch_pos is not None:
            self.switch.close_channel(int(sense_ch_pos))
        if sense_ch_neg is not None:
            self.switch.close_channel(int(sense_ch_neg))

        # Configure source ONCE at start
        self.current_source.set_current(float(current_amps))
        self.current_source.set_output(True)

        self._current_amps = float(current_amps)
        self._mode = "current_driven"
        self._armed = True
    
    def begin_constant_voltage_mode(self, ch_pos: int, ch_neg: int, voltage_volts: float,
                                   sense_ch_pos: int | None = None, sense_ch_neg: int | None = None) -> None:
        """Voltage-driven mode: 6487 sources voltage AND measures current."""
        # Configure routing ONCE at start
        self.switch.open_all()
        self.switch.close_channel(int(ch_pos))
        self.switch.close_channel(int(ch_neg))
        
        # For 4-wire measurements, also close sense channels
        if sense_ch_pos is not None:
            self.switch.close_channel(int(sense_ch_pos))
        if sense_ch_neg is not None:
            self.switch.close_channel(int(sense_ch_neg))
        
        # Configure 6487 to source voltage
        self.voltmeter.set_voltage(float(voltage_volts))
        self.voltmeter.set_voltage_output(True)
        
        self._voltage_volts = float(voltage_volts)
        self._mode = "voltage_driven"
        self._armed = True

    def take_sample(self) -> ResistanceResult:
        if not self._armed:
            raise RuntimeError("ExperimentController not armed. Call begin_constant_current/voltage_mode() first.")

        if self._mode == "current_driven":
            # Current-driven: measure voltage, current is known
            v = self.voltmeter.measure_voltage()
            i = self._current_amps
        else:  # voltage_driven
            # Voltage-driven: measure current, voltage is known
            i = self.voltmeter.measure_current()
            v = self._voltage_volts
        
        r = (v / i) if i != 0 else 0.0

        return ResistanceResult(current_amps=i, measured_voltage=v, resistance_ohms=r, measurement_mode=self._mode)

    def stop_outputs(self) -> None:
        # Fast "stop measuring" safety: turn source off
        try:
            if self._mode == "current_driven":
                self.current_source.set_output(False)
            else:  # voltage_driven
                self.voltmeter.set_voltage_output(False)
        finally:
            self._armed = False

    def safe_idle(self) -> None:
        # Full "reset hardware" safety: open relays + output off
        try:
            self.current_source.set_output(False)
        except Exception:
            pass
        try:
            self.voltmeter.set_voltage_output(False)
        except Exception:
            pass
        try:
            self.switch.open_all()
        except Exception:
            pass
        self._armed = False
