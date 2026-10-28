from dataclasses import dataclass
import os
from typing import Optional

import psutil


@dataclass(frozen=True)
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    battery_percent: Optional[float]
    battery_plugged_in: Optional[bool]


def read_system_metrics() -> SystemMetrics:
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage(os.path.abspath(os.sep)).percent

    try:
        battery = psutil.sensors_battery()
    except (AttributeError, NotImplementedError, OSError, psutil.Error):
        battery = None

    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        battery_percent=battery.percent if battery else None,
        battery_plugged_in=battery.power_plugged if battery else None,
    )
