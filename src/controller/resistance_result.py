from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class ResistanceResult:
    mode: Literal["current_driven", "voltage_driven"]
    channel1: int
    channel2: int

    set_current_amps: Optional[float] = None
    set_voltage_volts: Optional[float] = None

    measured_voltage_volts: Optional[float] = None
    measured_current_amps: Optional[float] = None

    resistance_ohms: Optional[float] = None
