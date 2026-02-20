from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg

class Source6487(BaseInstrument):
    DEFAULT_GPIB_ADDR = 22

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: int | None = None):
        super().__init__(cfg, name="Source6487")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR
        self._configured = False
        self.voltage_volts: float | None = None
        self.output_enabled: bool | None = None

    def connect(self) -> str:
        """Connect and configure the instrument for voltage measurements."""
        import pyvisa
        import time
        
        self.rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
        self.inst = self.rm.open_resource(self.cfg.resource_name)
        self.inst.timeout = 10000  # Longer timeout for 6487
        
        # Clear errors and flush buffer before doing anything
        self.inst.write("*CLS")
        time.sleep(0.2)
        
        # Now do the IDN query cleanly
        self.idn = self.inst.query("*IDN?").strip()
        self.connected = True
        
        if not self._configured:
            # CRITICAL: Proper initialization sequence for 6487
            self.write("*RST")  # Reset to known state
            time.sleep(0.5)
            
            # Configure for voltage measurements (default mode)
            self.write("SOUR:VOLT:STAT OFF")  # Turn OFF voltage source
            self.write("SOUR:VOLT:RANG 50")  # Set voltage source range
            self.write('FUNC "VOLT"')  # Set to voltage measurement mode
            self.write("VOLT:RANG:AUTO ON")  # Auto-range for voltage
            self.write("FORM:ELEM READ")  # Format: reading only
            self.write("SYST:ZCH OFF")  # Disable zero check
            self.write("*CLS")  # Clear errors
            time.sleep(0.3)
            
            self._configured = True
        
        return self.idn

    def measure_voltage(self) -> float:
        """Measure voltage (use when 6487 is in voltmeter mode)."""
        try:
            # INIT initiates measurement, FETC? retrieves result
            self.write("INIT")
            result = self.query("FETC?")
            return float(result.strip())
        except Exception as e:
            # If timeout or error, clear status and try READ? method
            self.write("*CLS")
            result = self.query("READ?")
            return float(result.strip())

    def measure_current(self) -> float:
        """Measure current (use when 6487 is sourcing voltage)."""
        # When sourcing voltage, 6487 measures current simultaneously
        # Just fetch the reading
        try:
            self.write("INIT")
            result = self.query("FETC?")
            return float(result.strip())
        except Exception:
            self.write("*CLS")
            result = self.query("READ?")
            return float(result.strip())
    
    def set_voltage(self, volts: float):
        """Set output voltage for voltage-driven measurements."""
        self.write(f"SOUR:VOLT {volts:.12g}")
        self.voltage_volts = volts
    
    def set_voltage_output(self, enabled: bool):
        """Enable/disable voltage source output."""
        if enabled:
            # When enabling voltage source, switch to current measurement mode
            self.write('FUNC "CURR"')  # Measure current
            self.write("CURR:RANG:AUTO ON")  # Auto-range for current
            self.write("SOUR:VOLT:STAT ON")  # Enable voltage source
        else:
            # When disabling, switch back to voltage measurement mode
            self.write("SOUR:VOLT:STAT OFF")  # Disable voltage source
            self.write('FUNC "VOLT"')  # Measure voltage
            self.write("VOLT:RANG:AUTO ON")  # Auto-range for voltage
        
        self.write("*CLS")
        self.output_enabled = enabled
