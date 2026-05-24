# Vehicle Platooning Project

ACO-based simulation for routing messages through a vehicle platoon network under changing latency, reliability, congestion, and link failures.

## Quick Start

```bash
python3 run.py
```

This creates a local `.venv`, installs required dependencies, and opens the dashboard. It works from Windows, macOS, and Linux when Python 3.10 or later is installed.

Run the terminal simulation:

```bash
python3 run.py simulation --runs 200 --failure-rate 0.2 --congestion-factor 1.5 --seed 42
```

Generate plots into `output/`:

```bash
python3 run.py plots
```

Run the animation:

```bash
python3 run.py animation
```

Run the tests:

```bash
python3 run.py test
```

## Manual Setup

For development or use of the installed CLI commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
vehicle-platooning-sim --runs 200 --seed 42
```

On Windows activation is `.venv\Scripts\activate`.

## Notes

Generated files are written to `output/` and are ignored by git. The dashboard and animation require Tkinter; if it is unavailable in your Python installation, the terminal simulation and plot generation still run.
