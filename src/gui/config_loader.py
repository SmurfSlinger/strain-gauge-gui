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
class GuiConfig:
    mode: str
    sample_interval_ms: int
    switch: VisaDeviceCfg
    current_source: VisaDeviceCfg
    voltmeter: VisaDeviceCfg
    allowed_switch_channels: list[int]
    default_experiment: ExperimentDefaults
    paths: GuiPaths



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
    )

