from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg  # adjust to your project

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
        # Flush any stale data in the output buffer before IDN query
        import pyvisa
        import time
        
        self.rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
        self.inst = self.rm.open_resource(self.cfg.resource_name)
        self.inst.timeout = 5000
        
        # Clear errors and flush buffer before doing anything
        self.inst.write("*CLS")
        time.sleep(0.2)  # Give instrument time to clear
        
        # Now do the IDN query cleanly
        self.idn = self.inst.query("*IDN?").strip()
        self.connected = True
        
        if not self._configured:
            # Configure 6487 for continuous voltage measurements
            # Set format to ASCII, reading only
            self.write("FORM:ELEM READ")
            
            # Configure for fast voltage measurements
            # NPLC 0.01 = ~167 microseconds per reading (very fast)
            self.write("NPLC 0.01")
            
            # Disable zero check (allows measurements)
            self.write("SYST:ZCH OFF")
            
            # Use voltage source at 0V (becomes voltmeter)
            self.write("SOUR:VOLT:STAT OFF")  # Turn OFF voltage source
            
            # Clear errors
            self.write("*CLS")
            
            self._configured = True
        
        return self.idn

    def measure_voltage(self) -> float:
        # READ? triggers measurement and returns result
        # This command waits for measurement to complete
        try:
            result = self.query("READ?")
            return float(result.strip())
        except Exception as e:
            # If timeout or error, clear status and try once more
            self.write("*CLS")
            result = self.query("READ?")
            return float(result.strip())

    def measure_current(self) -> float:
        # 6487 uses READ? to get a reading
        return float(self.query("READ?").strip())
    
    def set_voltage(self, volts: float):
        """Set output voltage for voltage-driven measurements."""
        self.write(f"SOUR:VOLT {volts:.12g}")
        self.voltage_volts = volts
    
    def set_voltage_output(self, enabled: bool):
        """Enable/disable voltage source output."""
        self.write("SOUR:VOLT:STAT ON" if enabled else "SOUR:VOLT:STAT OFF")
        self.output_enabled = enabled
