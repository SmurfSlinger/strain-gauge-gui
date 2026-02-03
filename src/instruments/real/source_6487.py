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
        idn = super().connect()
        
        if not self._configured:
            # Clear errors first, before any configuration
            self.write("*CLS")
            
            # Configure for DC voltage measurement
            self.write("CONF:VOLT:DC")  # Configure for DC voltage
            self.write("VOLT:RANG:AUTO ON")  # Auto-ranging
            self.write("VOLT:NPLC 1")  # Fast integration
            self.write("FORM:ELEM READ")  # Simple reading format
            
            # Clear any errors from configuration
            self.write("*CLS")
            self._configured = True
        
        return idn

    def measure_voltage(self) -> float:
        # 6487 uses READ? to get a reading (returns voltage in picoammeter mode)
        return float(self.query("READ?").strip())

    def measure_current(self) -> float:
        # 6487 uses READ? to get a reading
        return float(self.query("READ?").strip())
