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
    mode: str  # "mock" or "real"
    sample_interval_ms: int
    switch: VisaDeviceCfg
    current_source: VisaDeviceCfg
    voltmeter: VisaDeviceCfg
    default_experiment: ExperimentDefaults
    paths: GuiPaths


def load_config(config_path: str | Path) -> GuiConfig:
    p = Path(config_path)
    data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))

    return GuiConfig(
        mode=str(data.get("mode", "mock")).lower(),
        sample_interval_ms=int(data.get("sample_interval_ms", 250)),
        switch=VisaDeviceCfg(resource_name=data["switch"]["resource_name"]),
        current_source=VisaDeviceCfg(resource_name=data["current_source"]["resource_name"]),
        voltmeter=VisaDeviceCfg(resource_name=data["voltmeter"]["resource_name"]),
        default_experiment=ExperimentDefaults(
            force_channel_pos=int(data["default_experiment"]["force_channel_pos"]),
            force_channel_neg=int(data["default_experiment"]["force_channel_neg"]),
            current_amps=float(data["default_experiment"]["current_amps"]),
        ),
        paths=GuiPaths(
            default_working_directory=str(data.get("paths", {}).get("default_working_directory", "")),
        ),
    )
