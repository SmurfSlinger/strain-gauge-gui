from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg  # adjust to your project


class Source6487(BaseInstrument):
    """
    Keithley 6487 Picoammeter / Voltage Source (SCPI).
    For now it's your measurement device:
      - connect()
      - measure_voltage()
      - (optional) measure_current()
    """

    DEFAULT_GPIB_ADDR = 22

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: Optional[int] = None):
        super().__init__(cfg)
        self._gpib_addr: int = gpib_addr if gpib_addr is not None else self.DEFAULT_GPIB_ADDR
        self._connected: bool = False

    # -----------------------
    # Base I/O plumbing
    # -----------------------

    def _select_addr(self) -> None:
        self.write_raw(f"++addr {self._gpib_addr}")

    def write_raw(self, cmd: str) -> None:
        if hasattr(super(), "write"):
            super().write(cmd)  # type: ignore[misc]
            return
        self._inst.write(cmd)  # type: ignore[attr-defined]

    def query_raw(self, cmd: str) -> str:
        if hasattr(super(), "query"):
            return super().query(cmd)  # type: ignore[misc]
        return self._inst.query(cmd)  # type: ignore[attr-defined]

    def _scpi_query(self, cmd: str) -> str:
        self._ensure_connected()
        self._select_addr()
        return self.query_raw(cmd)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("Source6487 is not connected. Call connect() first.")

    # -----------------------
    # Public API
    # -----------------------

    def connect(self) -> None:
        """
        Safe to call repeatedly.
        """
        if self._connected:
            return

        super().connect()
        self._select_addr()

        # Identity check (non-destructive)
        _ = self.query_raw("*IDN?")

        self._connected = True

    def disconnect(self) -> None:
        if not self._connected:
            return
        try:
            super().disconnect()
        finally:
            self._connected = False

    def measure_voltage(self) -> float:
        """
        One-shot voltage measurement.
        SCPI: MEAS:VOLT?
        """
        resp = self._scpi_query("MEAS:VOLT?")
        return float(resp.strip())

    def measure_current(self) -> float:
        """
        One-shot current measurement.
        SCPI: MEAS:CURR?
        """
        resp = self._scpi_query("MEAS:CURR?")
        return float(resp.strip())