# Eye of Agamotto

A desktop system monitor built with Python, PyQt5, Matplotlib, and psutil. It displays CPU, memory, disk, and battery information, graphs recent CPU and memory usage, and lists the busiest processes.

## Features

- Automatic live updates for CPU, memory, disk, and battery information
- A rolling CPU and memory graph
- A configurable warning threshold that highlights high CPU, memory, or disk usage
- Optional desktop notifications when the threshold is reached
- A compact always-on-top mode for essential metrics
- A process table with a confirmation step and safety checks before stopping a process

## Requirements

- Python 3 or newer
- Ubuntu with a graphical desktop session

## Set up and run

Open a terminal in this project folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Activate the virtual environment with `source .venv/bin/activate` before running the app again in a new terminal.

## Project layout

```text
main.py                 Starts the application
app/main_window.py      Builds the window and connects the app components
app/system_monitor.py   Reads system resource and battery information
app/process_manager.py  Lists processes and requests process termination
app/graph.py            Draws CPU and memory history
tests/                  Automated checks for non-graphical app logic
requirements.txt        Lists the Python packages needed by the app
```

