
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Set
from pyvisa.errors import VisaIOError

from src.instruments.abstract.base_instrument import BaseInstrument
from src.gui.config_loader import VisaDeviceCfg


AVAILABLE_CHANNELS = {
    1002: "Verified channel (slot 1 matrix)",
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

<<<<<<< Updated upstream
    def _using_prologix(self) -> bool:
        # Prologix controllers usually appear as ASRLx::INSTR (serial)
        rn = (self.cfg.resource_name or "").upper()
        return rn.startswith("ASRL")

    def _select_addr(self):
        # Only send Prologix commands if we are actually using a Prologix serial adapter
        if self._using_prologix():
            self.write(f"++addr {self.gpib_addr}")

=======
>>>>>>> Stashed changes
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

        # IMPORTANT: channels must be numeric, NOT quoted strings
        self._tsp_write(f"channel.close({ch})")
        self._waitcomplete()

        self.closed_channels.add(ch)

    def open_channel(self, channel: int):
        ch = int(channel)
        self._require_valid(ch)

        self._tsp_write(f"channel.open({ch})")
        self._waitcomplete()

        self.closed_channels.discard(ch)

    def get_channel_state(self, ch: int) -> int | None:
        try:
            resp = self.inst.query(f"print(channel.getstate({int(ch)}))").strip()
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