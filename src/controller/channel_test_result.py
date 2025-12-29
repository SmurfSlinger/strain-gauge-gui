from dataclasses import dataclass


@dataclass
class ChannelTestResult:
    channel1: int
    channel2: int
    current: float
    set_voltage: float
    measured_voltage: float