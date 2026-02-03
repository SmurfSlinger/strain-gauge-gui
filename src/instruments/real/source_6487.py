from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg  # adjust to your project

class Source6487(BaseInstrument):
    DEFAULT_GPIB_ADDR = 22

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: int | None = None):
        super().__init__(cfg, name="Source6487")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR

    def measure_voltage(self) -> float:
        # 6487 uses READ? to get a reading (returns voltage in picoammeter mode)
        return float(self.query("READ?").strip())

    def measure_current(self) -> float:
        # 6487 uses READ? to get a reading
        return float(self.query("READ?").strip())
