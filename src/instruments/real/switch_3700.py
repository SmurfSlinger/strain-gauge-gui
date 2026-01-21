# src/real/switch3700.py

from __future__ import annotations
from typing import Set

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg


# src/real/switch3700.py

class Switch3700(BaseInstrument):
    """
    Keithley Series 3700/3700A Switch System.
    Switching operations use TSP channel.* calls (not SCPI route subsystem).
    """

    DEFAULT_GPIB_ADDR = 7

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: Optional[int] = None):
        super().__init__(cfg)
        self._gpib_addr: int = gpib_addr if gpib_addr is not None else self.DEFAULT_GPIB_ADDR

        # Software state (requested)
        self.closed_channels: Set[str] = set()

        # Idempotency / safety
        self._connected: bool = False

    # -----------------------
    # Base I/O plumbing
    # -----------------------

    def _select_addr(self) -> None:
        """
        Select the target instrument on the serial/GPIB bridge.

        If you're using a Prologix-style adapter: ++addr <n>
        If not, replace this with your bridge's addressing mechanism.
        """
        self.write_raw(f"++addr {self._gpib_addr}")

    def write_raw(self, cmd: str) -> None:
        """
        Write to the VISA session. Uses BaseInstrument helper if available.
        """
        if hasattr(super(), "write"):
            super().write(cmd)  # type: ignore[misc]
            return
        # Fallback if BaseInstrument exposes _inst
        self._inst.write(cmd)  # type: ignore[attr-defined]

    def query_raw(self, cmd: str) -> str:
        """
        Query the VISA session. Uses BaseInstrument helper if available.
        """
        if hasattr(super(), "query"):
            return super().query(cmd)  # type: ignore[misc]
        return self._inst.query(cmd)  # type: ignore[attr-defined]

    def _tsp_write(self, line: str) -> None:
        self._ensure_connected()
        self._select_addr()
        self.write_raw(line)

    def _tsp_query(self, expr: str) -> str:
        """
        Evaluate a TSP expression via print(...). Returns the printed string.
        """
        self._ensure_connected()
        self._select_addr()
        return self.query_raw(f"print({expr})")

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("Switch3700 is not connected. Call connect() first.")

    # -----------------------
    # Public API
    # -----------------------

    def connect(self) -> None:
        """
        Connect to VISA resource and verify instrument responsiveness.
        Safe to call repeatedly.
        """
        if self._connected:
            return

        super().connect()

        # Address + sanity check (non-destructive)
        self._select_addr()

        # Prefer TSP identity check (works in the 3700A family)
        _ = self._tsp_query("localnode.model")

        self._connected = True

    def disconnect(self) -> None:
        """
        Safe to call repeatedly.
        """
        if not self._connected:
            return
        try:
            super().disconnect()
        finally:
            self._connected = False

    def open_all(self) -> None:
        """
        Open all channels (TSP).
        """
        self._tsp_write("channel.openall()")
        self.closed_channels.clear()

    def open_channel(self, channel: int | str) -> None:
        """
        Open a specific channel (e.g., 1101).
        """
        ch = str(channel)
        self._tsp_write(f'channel.open("{ch}")')
        self.closed_channels.discard(ch)

    def close_channel(self, channel: int | str) -> None:
        """
        Close a specific channel (e.g., 1101).
        """
        ch = str(channel)
        self._tsp_write(f'channel.close("{ch}")')
        self.closed_channels.add(ch)

    def is_channel_closed(self, channel: int | str) -> bool:
        """
        Purely software state (requested). No instrument query.
        """
        return str(channel) in self.closed_channels