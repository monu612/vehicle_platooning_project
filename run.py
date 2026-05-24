from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import venv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / ".venv"
STAMP_FILE = VENV_DIR / ".project-installed"
PROJECT_FILE = BASE_DIR / "pyproject.toml"


def _venv_python() -> Path:
    scripts_dir = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return VENV_DIR / scripts_dir / executable


def _project_digest() -> str:
    return hashlib.sha256(PROJECT_FILE.read_bytes()).hexdigest()


def _environment_is_ready(python: Path) -> bool:
    if not python.exists() or not STAMP_FILE.exists():
        return False

    if STAMP_FILE.read_text(encoding="utf-8").strip() != _project_digest():
        return False

    check = subprocess.run(
        [str(python), "-c", "import matplotlib, networkx, pytest"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    return check.returncode == 0


def ensure_environment() -> Path:
    python = _venv_python()

    if not python.exists():
        print("Creating local Python environment in .venv...")
        venv.create(VENV_DIR, with_pip=True)

    if not _environment_is_ready(python):
        print("Installing project dependencies...")
        subprocess.run(
            [str(python), "-m", "pip", "install", "-e", ".[dev]"],
            cwd=BASE_DIR,
            check=True,
        )
        STAMP_FILE.write_text(_project_digest(), encoding="utf-8")

    return python


def _check_tkinter(python: Path) -> bool:
    result = subprocess.run(
        [str(python), "-c", "import tkinter"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True

    print(
        "This Python installation does not include Tkinter, which is required "
        "for the dashboard and animation.",
        file=sys.stderr,
    )
    print("Run `python run.py simulation` for the terminal version.", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up and run the vehicle platooning project.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="ui",
        choices=("ui", "simulation", "plots", "animation", "test", "setup"),
        help="Application component to start. The dashboard is the default.",
    )
    parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Optional arguments forwarded to the selected component.",
    )
    args = parser.parse_args()

    try:
        python = ensure_environment()
    except subprocess.CalledProcessError as exc:
        print(f"Dependency installation failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode

    if args.mode == "setup":
        print("Environment is ready.")
        return 0

    if args.mode in {"ui", "animation"} and not _check_tkinter(python):
        return 1

    command = {
        "ui": [str(python), str(BASE_DIR / "ui.py")],
        "simulation": [str(python), str(BASE_DIR / "simulation.py")],
        "plots": [str(python), str(BASE_DIR / "final_plots.py")],
        "animation": [str(python), str(BASE_DIR / "vehicle_animation.py")],
        "test": [str(python), "-m", "pytest"],
    }[args.mode]

    return subprocess.run([*command, *args.arguments], cwd=BASE_DIR).returncode


if __name__ == "__main__":
    raise SystemExit(main())
