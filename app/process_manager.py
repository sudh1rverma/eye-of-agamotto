from dataclasses import dataclass
import os

import psutil


@dataclass(frozen=True)
class ProcessDetails:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    create_time: float


def get_top_processes(limit: int = 25) -> list[ProcessDetails]:
  
    processes = []
    attributes = ["pid", "name", "cpu_percent", "memory_percent", "create_time"]

    for process in psutil.process_iter(attrs=attributes):
        try:
            info = process.info
            if info["cpu_percent"] is None or info["memory_percent"] is None:
                continue

            processes.append(
                ProcessDetails(
                    pid=info["pid"],
                    name=info["name"] or "Unknown",
                    cpu_percent=info["cpu_percent"],
                    memory_percent=info["memory_percent"],
                    create_time=info["create_time"],
                )
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    return sorted(processes, key=lambda item: item.cpu_percent, reverse=True)[:limit]


def terminate_process(pid: int, expected_create_time: float) -> None:
  
    if pid <= 2 or pid == os.getpid():
        raise PermissionError("This process is protected from termination by the app.")

    process = psutil.Process(pid)
    if abs(process.create_time() - expected_create_time) > 0.01:
        raise RuntimeError("That process has changed since the table was refreshed. Refresh and select it again.")

    process.terminate()
    process.wait(timeout=3)
