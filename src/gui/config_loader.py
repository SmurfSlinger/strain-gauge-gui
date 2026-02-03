from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VisaDeviceCfg:
    resource_name: str


@dataclass(frozen=True)
class ExperimentDefaults:
    force_channel_pos: int
    force_channel_neg: int
    current_amps: float


@dataclass(frozen=True)
class GuiPaths:
    default_working_directory: str


@dataclass(frozen=True)
class MeasurementCase:
    name: str
    force_channel_pos: int
    force_channel_neg: int
    wire_mode: str = "2-wire"  # "2-wire" or "4-wire"
    sense_channel_pos: int | None = None  # For 4-wire measurements
    sense_channel_neg: int | None = None  # For 4-wire measurements
    
    def is_4_wire(self) -> bool:
        return self.wire_mode == "4-wire"
    
    def get_all_channels(self) -> list[int]:
        """Returns all channels used by this case."""
        channels = [self.force_channel_pos, self.force_channel_neg]
        if self.is_4_wire() and self.sense_channel_pos and self.sense_channel_neg:
            channels.extend([self.sense_channel_pos, self.sense_channel_neg])
        return channels


@dataclass(frozen=True)
class MultiplexingConfig:
    enabled: bool
    auto_cycle: bool
    readings_per_case: int
    dwell_time_ms: int


@dataclass(frozen=True)
class GuiConfig:
    mode: str
    sample_interval_ms: int
    switch: VisaDeviceCfg
    current_source: VisaDeviceCfg
    voltmeter: VisaDeviceCfg
    allowed_switch_channels: list[int]
    default_experiment: ExperimentDefaults
    paths: GuiPaths
    measurement_cases: list[MeasurementCase]
    multiplexing: MultiplexingConfig



def load_config(path: Path) -> GuiConfig:
    raw = json.loads(path.read_text())

    return GuiConfig(
        mode=raw["mode"],
        sample_interval_ms=raw["sample_interval_ms"],
        switch=VisaDeviceCfg(**raw["switch"]),
        current_source=VisaDeviceCfg(**raw["current_source"]),
        voltmeter=VisaDeviceCfg(**raw["voltmeter"]),
        allowed_switch_channels=raw["allowed_switch_channels"],
        default_experiment=ExperimentDefaults(**raw["default_experiment"]),
        paths=GuiPaths(**raw["paths"]),
        measurement_cases=[
            MeasurementCase(
                name=case["name"],
                force_channel_pos=case["force_channel_pos"],
                force_channel_neg=case["force_channel_neg"],
                wire_mode=case.get("wire_mode", "2-wire"),
                sense_channel_pos=case.get("sense_channel_pos"),
                sense_channel_neg=case.get("sense_channel_neg")
            )
            for case in raw.get("measurement_cases", [])
        ],
        multiplexing=MultiplexingConfig(**raw.get("multiplexing", {
            "enabled": False,
            "auto_cycle": False,
            "readings_per_case": 10,
            "dwell_time_ms": 100
        })),
    )

