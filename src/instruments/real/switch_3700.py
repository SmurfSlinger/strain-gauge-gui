
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Set
from pyvisa.errors import VisaIOError

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg


AVAILABLE_CHANNELS = {
    # Bank 1 (Force channels) - connect to MUX 1 OUT
    1001: "Sample 1 - Force (Bank 1)",
    1002: "Sample 2 - Force (Bank 1)",
    1003: "Sample 3 - Force (Bank 1)",
    1004: "Sample 4 - Force (Bank 1)",
    1005: "Sample 5 - Force (Bank 1)",
    1006: "Sample 6 - Force (Bank 1)",
    1007: "Sample 7 - Force (Bank 1)",
    1008: "Sample 8 - Force (Bank 1)",
    1009: "Sample 9 - Force (Bank 1)",
    1010: "Sample 10 - Force (Bank 1)",
    1011: "Sample 11 - Force (Bank 1)",
    1012: "Sample 12 - Force (Bank 1)",
    1013: "Sample 13 - Force (Bank 1)",
    1014: "Sample 14 - Force (Bank 1)",
    1015: "Sample 15 - Force (Bank 1)",
    1016: "Sample 16 - Force (Bank 1)",
    1017: "Sample 17 - Force (Bank 1)",
    1018: "Sample 18 - Force (Bank 1)",
    1019: "Sample 19 - Force (Bank 1)",
    1020: "Sample 20 - Force (Bank 1)",
    # Bank 2 (Sense channels) - connect to MUX 2 OUT
    1021: "Sample 1 - Sense (Bank 2)",
    1022: "Sample 2 - Sense (Bank 2)",
    1023: "Sample 3 - Sense (Bank 2)",
    1024: "Sample 4 - Sense (Bank 2)",
    1025: "Sample 5 - Sense (Bank 2)",
    1026: "Sample 6 - Sense (Bank 2)",
    1027: "Sample 7 - Sense (Bank 2)",
    1028: "Sample 8 - Sense (Bank 2)",
    1029: "Sample 9 - Sense (Bank 2)",
    1030: "Sample 10 - Sense (Bank 2)",
    1031: "Sample 11 - Sense (Bank 2)",
    1032: "Sample 12 - Sense (Bank 2)",
    1033: "Sample 13 - Sense (Bank 2)",
    1034: "Sample 14 - Sense (Bank 2)",
    1035: "Sample 15 - Sense (Bank 2)",
    1036: "Sample 16 - Sense (Bank 2)",
    1037: "Sample 17 - Sense (Bank 2)",
    1038: "Sample 18 - Sense (Bank 2)",
    1039: "Sample 19 - Sense (Bank 2)",
    1040: "Sample 20 - Sense (Bank 2)",
}

def get_channel_choices():
    """
    Returns a dict suitable for GUI selection:
    {channel_number: human_readable_name}
    """
    return dict(AVAILABLE_CHANNELS)


class UnvalidatedChannelError(ValueError):
    pass


@dataclass(frozen=True)
class SwitchState:
    """
    A named safe configuration of routes.

    close_routes: routes that should be CLOSED in this state
    open_routes: routes that should be OPEN in this state
    """
    close_routes: tuple[str, ...] = ()
    open_routes: tuple[str, ...] = ()


class Switch3700(BaseInstrument):
    """
    Keithley 3706A / 3700A Series switch mainframe using TSP over GPIB.

    IMPORTANT:
    - This instrument does not support reliable channel/card discovery on your setup.
    - We enforce a strict allow-list (valid_channels) to prevent error 1115.
    - We avoid channel.openall(); we only open channels we previously closed.
    """

    DEFAULT_GPIB_ADDR = 7

    def __init__(
        self,
        cfg: VisaDeviceCfg,
        gpib_addr: int | None = None,
        *,
        valid_channels: Optional[Iterable[int]] = None,
        routes: Optional[Dict[str, int]] = None,
        strict: bool = True,
    ):
        super().__init__(cfg, name="Switch3700")
        self.gpib_addr = gpib_addr or self.DEFAULT_GPIB_ADDR

        # Track only what THIS program closes (safe alternative to channel.openall()).
        self.closed_channels: Set[int] = set()

        # Guardrails
        self.strict = strict
        self.valid_channels: Set[int] = set(valid_channels or [])
        self.routes: Dict[str, int] = dict(routes or {})

        # Optional named states (you can extend later)
        self.states: Dict[str, SwitchState] = {
            "idle": SwitchState(open_routes=tuple(self.routes.keys())),
        }

    # ---------- internal helpers ----------

    def _tsp_write(self, cmd: str):
        self.write(cmd)

    def _tsp_query_value(self, expr: str) -> str:
        """
        Query an expression by printing it.
        Always returns a single-line string suitable for PyVISA query().
        """
        return self.query(f"print({expr})").strip()

    def _waitcomplete(self):
        self._tsp_write("waitcomplete()")

    def _require_valid(self, ch: int):
        if not self.strict:
            return
        if ch not in self.valid_channels:
            raise UnvalidatedChannelError(
                f"Refusing to switch unvalidated channel {ch}. "
                f"Valid channels: {sorted(self.valid_channels)}"
            )

    # ---------- public API ----------

    def connect(self) -> str:
        idn = super().connect()
        # Verify TSP is alive (safe)
        _ = self._tsp_query_value("_VERSION")
        # Clear any leftover errors from previous sessions
        self._tsp_write("errorqueue.clear()")
        return idn

    # ---- topology management ----

    def set_topology(
        self,
        *,
        routes: Optional[Dict[str, int]] = None,
        valid_channels: Optional[Iterable[int]] = None,
        states: Optional[Dict[str, SwitchState]] = None,
    ):
        """
        Allows you to load/replace mapping later without refactoring.
        """
        if routes is not None:
            self.routes = dict(routes)
        if valid_channels is not None:
            self.valid_channels = set(valid_channels)
        if states is not None:
            self.states = dict(states)

        # Keep a default idle state that opens all known routes
        if "idle" not in self.states:
            self.states["idle"] = SwitchState(open_routes=tuple(self.routes.keys()))

    # ---- low-level relay control (channel numbers stay inside this class) ----

    def close_channel(self, channel: int):
        ch = int(channel)
        self._require_valid(ch)

        # IMPORTANT: TSP requires channels as quoted strings
        self._tsp_write(f'channel.close("{ch}")')
        self._waitcomplete()

        self.closed_channels.add(ch)

    def open_channel(self, channel: int):
        ch = int(channel)
        self._require_valid(ch)

        self._tsp_write(f'channel.open("{ch}")')
        self._waitcomplete()

        self.closed_channels.discard(ch)

    def get_channel_state(self, ch: int) -> int | None:
        try:
            resp = self._tsp_query_value(f'channel.getstate("{int(ch)}")')
            if resp == "":
                return None
            return int(resp)
        except Exception:
            return None

    def open_all(self):
        """
        Safe replacement for channel.openall() on your system:
        only opens channels THIS program has closed.
        """
        for ch in list(self.closed_channels):
            # open_channel will also discard from closed_channels
            self.open_channel(ch)
        self.closed_channels.clear()
    
    def open_all_slots(self):
        """
        Open all channels across all slots using TSP command.
        More efficient for internal DMM operations.
        """
        self._tsp_write('channel.open("allslots")')
        self._waitcomplete()
        self.closed_channels.clear()

    # ---- named routes (preferred) ----

    def connect_route(self, name: str):
        if name not in self.routes:
            raise ValueError(f"Unknown route '{name}'. Known: {sorted(self.routes.keys())}")
        self.close_channel(self.routes[name])

    def disconnect_route(self, name: str):
        if name not in self.routes:
            raise ValueError(f"Unknown route '{name}'. Known: {sorted(self.routes.keys())}")
        self.open_channel(self.routes[name])

    def route_state(self, name: str) -> int:
        if name not in self.routes:
            raise ValueError(f"Unknown route '{name}'. Known: {sorted(self.routes.keys())}")
        return self.get_channel_state(self.routes[name])

    # ---- safe states ----

    def apply_state(self, state_name: str):
        """
        Applies a named safe state by opening first, then closing.
        """
        if state_name not in self.states:
            raise ValueError(f"Unknown state '{state_name}'. Known: {sorted(self.states.keys())}")

        state = self.states[state_name]

        # Open first (reduce risk of unintended shorts), then close required routes.
        for r in state.open_routes:
            if r in self.routes:
                self.disconnect_route(r)

        for r in state.close_routes:
            if r in self.routes:
                self.connect_route(r)
    
    # ---- Internal DMM 4-wire resistance measurements ----
    
    def setup_internal_dmm(self, channel: int) -> None:
        """
        Configure the 3706A's internal DMM for 4-wire resistance on a channel.
        Call this ONCE at the start of acquisition.
        
        Args:
            channel: Channel number to measure (e.g., 1001)
        """
        ch = int(channel)
        self._require_valid(ch)
        
        # Open all channels first
        self._tsp_write('channel.open("allslots")')
        self._waitcomplete()
        
        # Configure DMM for 4-wire ohms measurement
        self._tsp_write('dmm.setconfig("slot1","fourwireohms")')
        
        # Close the channel for measurement (leave it closed)
        self._tsp_write(f'channel.close("{ch}")')
        self._waitcomplete()
        
        self.closed_channels.add(ch)
    
    def measure_resistance_internal_dmm(self) -> float:
        """
        Take a single resistance measurement using the configured DMM.
        Must call setup_internal_dmm() first.
        
        Returns:
            Resistance in ohms
        """
        # Just measure with the already-configured DMM and closed channel
        result = self._tsp_query_value('dmm.measure()')
        return float(result)