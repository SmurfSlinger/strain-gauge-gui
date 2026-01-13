from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QThread, Signal

from src.controller.experiment_controller import ExperimentController, ResistanceResult


@dataclass(frozen=True)
class Sample:
    t_seconds: float
    current_amps: float
    voltage_v: float
    resistance_ohms: float

    # Right-side fields (placeholders until you integrate DAQ/strain)
    load_lbs: float = 0.0
    extension_in: float = 0.0
    strain_1: float = 0.0
    strain_2: float = 0.0


class AcquisitionThread(QThread):
    sample_ready = Signal(object)   # Sample
    status = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        controller: ExperimentController,
        force_ch_pos: int,
        force_ch_neg: int,
        current_amps: float,
        interval_ms: int,
        parent=None,
    ):
        super().__init__(parent)
        self._controller = controller
        self._force_ch_pos = force_ch_pos
        self._force_ch_neg = force_ch_neg
        self._current_amps = current_amps
        self._interval_ms = max(50, int(interval_ms))
        self._running = False
        self._t0: Optional[float] = None

    def update_params(self, force_ch_pos: int, force_ch_neg: int, current_amps: float) -> None:
        self._force_ch_pos = int(force_ch_pos)
        self._force_ch_neg = int(force_ch_neg)
        self._current_amps = float(current_amps)

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        self._running = True
        self._t0 = time.perf_counter()
        self.status.emit("Running")

        try:
            while self._running:
                t_now = time.perf_counter()
                t = t_now - (self._t0 or t_now)

                # Uses your controller method (single measurement per tick)
                rr: ResistanceResult = self._controller.run_current_driven_resistance(
                    channel_force_pos=self._force_ch_pos,
                    channel_force_neg=self._force_ch_neg,
                    current_amps=self._current_amps,
                )

                s = Sample(
                    t_seconds=t,
                    current_amps=rr.current_amps,
                    voltage_v=rr.measured_voltage,
                    resistance_ohms=rr.resistance_ohms,
                )
                self.sample_ready.emit(s)

                # sleep remaining time
                elapsed_ms = (time.perf_counter() - t_now) * 1000.0
                wait_ms = self._interval_ms - elapsed_ms
                if wait_ms > 0:
                    time.sleep(wait_ms / 1000.0)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.status.emit("Stopped")
