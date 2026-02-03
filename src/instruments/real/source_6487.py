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
            # Configure for DC voltage measurement
            self.write("CONF:VOLT:DC")  # Configure for DC voltage
            self.write("VOLT:RANG:AUTO ON")  # Auto-ranging
            self.write("VOLT:NPLC 1")  # Fast integration
            self.write("FORM:ELEM READ")  # Simple reading format
            self.write("*CLS")  # Clear any config errors
            self._configured = True
        
        return self.idn

    def measure_voltage(self) -> float:
        # 6487 uses READ? to get a reading (returns voltage in picoammeter mode)
        return float(self.query("READ?").strip())

    def measure_current(self) -> float:
        # 6487 uses READ? to get a reading
        return float(self.query("READ?").strip())
