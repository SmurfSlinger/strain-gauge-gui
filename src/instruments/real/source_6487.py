from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg  # adjust to your project

class Source6487(BaseInstrument):
    DEFAULT_GPIB_ADDR = 22

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: int | None = None):
        super().__init__(cfg, name="Source6487")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR

    def _select_addr(self):
        self.write(f"++addr {self.gpib_addr}")

    def measure_voltage(self) -> float:
        self._select_addr()
        return float(self.query("MEAS:VOLT?").strip())

    def measure_current(self) -> float:
        self._select_addr()
        return float(self.query("MEAS:CURR?").strip())
