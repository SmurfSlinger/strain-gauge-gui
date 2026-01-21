# src/real/switch3700.py

from __future__ import annotations
from typing import Set

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg


class Switch3700(BaseInstrument):
    DEFAULT_GPIB_ADDR = 7

    def __init__(self, cfg: VisaDeviceCfg, gpib_addr: int | None = None):
        super().__init__(cfg, name="Switch3700")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR
        self.closed_channels: Set[str] = set()

    # ---------- internal helpers ----------

    def _select_addr(self):
        self.write(f"++addr {self.gpib_addr}")

    def _tsp_write(self, cmd: str):
        self._select_addr()
        self.write(cmd)

    def _tsp_query(self, expr: str) -> str:
        self._select_addr()
        return self.query(f"print({expr})")

    # ---------- public API ----------

    def connect(self) -> str:
        idn = super().connect()

        # 3700 identity check via TSP
        self._tsp_query("localnode.model")
        return idn

    def open_all(self):
        self._tsp_write("channel.openall()")
        self.closed_channels.clear()

    def open_channel(self, channel: int | str):
        ch = str(channel)
        self._tsp_write(f'channel.open("{ch}")')
        self.closed_channels.discard(ch)

    def close_channel(self, channel: int | str):
        ch = str(channel)
        self._tsp_write(f'channel.close("{ch}")')
        self.closed_channels.add(ch)
