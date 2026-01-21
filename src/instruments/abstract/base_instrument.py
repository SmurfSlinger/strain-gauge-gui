# src/instruments/base_instrument.py

import pyvisa
from typing import Optional

from src.gui.config_loader import VisaDeviceCfg


class BaseInstrument:
    """
    Base class for all real instruments.
    Handles VISA lifecycle only.
    """

    def __init__(self, cfg: VisaDeviceCfg, name: str):
        self.cfg = cfg
        self.name = name

        self.rm: Optional[pyvisa.ResourceManager] = None
        self.inst: Optional[pyvisa.resources.Resource] = None

        self.connected: bool = False
        self.idn: Optional[str] = None

    def connect(self) -> str:
        """
        Open VISA connection and verify communication.
        Safe to call repeatedly.
        """
        if self.connected:
            return self.idn or ""

        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.cfg.resource_name)

        # Conservative default timeout (ms)
        self.inst.timeout = 5000

        # Standard identity query (safe for all Keithley instruments)
        self.idn = self.inst.query("*IDN?").strip()

        self.connected = True
        return self.idn

    def disconnect(self):
        if self.inst:
            try:
                self.inst.close()
            except Exception:
                pass

        self.inst = None
        self.connected = False

    # -------- low-level helpers --------

    def write(self, cmd: str):
        if not self.connected or not self.inst:
            raise RuntimeError(f"{self.name} not connected")
        self.inst.write(cmd)

    def query(self, cmd: str) -> str:
        if not self.connected or not self.inst:
            raise RuntimeError(f"{self.name} not connected")
        return self.inst.query(cmd)