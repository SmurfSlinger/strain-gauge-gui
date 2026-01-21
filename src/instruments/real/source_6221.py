from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg


class Source6221(BaseInstrument):
    DEFAULT_GPIB_ADDR = 12

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: int | None = None):
        super().__init__(cfg, name="Source6221")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR
        self.current_amps: float | None = None
        self.output_enabled: bool | None = None

    def _select_addr(self):
        self.write(f"++addr {self.gpib_addr}")

    def set_current(self, amps: float):
        self._select_addr()
        self.write(f"SOUR:CURR {amps:.12g}")
        self.current_amps = amps

    def set_output(self, enabled: bool):
        self._select_addr()
        self.write("OUTP ON" if enabled else "OUTP OFF")
        self.output_enabled = enabled