from __future__ import annotations

from typing import Optional

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg  # adjust to your project


class Source6221(BaseInstrument):
    """
    Keithley 6221 AC/DC Current Source (SCPI).
    Minimal control for now:
      - connect()
      - set_current(amps)
      - set_output(True/False)
    """

    DEFAULT_GPIB_ADDR = 12

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: Optional[int] = None):
        super().__init__(cfg)
        self._gpib_addr: int = gpib_addr if gpib_addr is not None else self.DEFAULT_GPIB_ADDR

        # Cached state (optional but useful and safe)
        self.current_amps: Optional[float] = None
        self.output_enabled: Optional[bool] = None

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

    def _scpi_write(self, cmd: str) -> None:
        self._ensure_connected()
        self._select_addr()
        self.write_raw(cmd)

    def _scpi_query(self, cmd: str) -> str:
        self._ensure_connected()
        self._select_addr()
        return self.query_raw(cmd)

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("Source6221 is not connected. Call connect() first.")

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

    def set_current(self, amps: float) -> None:
        """
        Sets DC source current level (does not enable output).
        SCPI: SOUR:CURR <value>
        """
        self._scpi_write(f"SOUR:CURR {amps:.12g}")
        self.current_amps = amps

    def set_output(self, enabled: bool) -> None:
        """
        Enables/disables output.
        SCPI: OUTP ON|OFF
        """
        self._scpi_write("OUTP ON" if enabled else "OUTP OFF")
        self.output_enabled = enabled