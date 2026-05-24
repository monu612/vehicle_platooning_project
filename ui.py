from __future__ import annotations

import csv
import datetime as dt
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import messagebox, ttk
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from simulation import run_simulation


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
RESULT_FIELDS = (
    "timestamp",
    "pdr_aco",
    "pdr_base",
    "lat_aco",
    "lat_base",
    "red_aco",
    "red_base",
)

BG_COLOR = "#0f0f0f"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#00d4ff"
SECONDARY_COLOR = "#1e1e2e"
SUCCESS_COLOR = "#00ff88"
WARNING_COLOR = "#ffaa00"
BUTTON_BG = "#1a1a2e"
BUTTON_HOVER = "#16213e"


def _percent_change(new_value: float, old_value: float, lower_is_better: bool = False) -> str:
    if old_value == 0:
        return "n/a"

    delta = ((old_value - new_value) if lower_is_better else (new_value - old_value)) / old_value
    return f"{delta * 100:+.2f}%"


class Dashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.last_results: dict[str, float] | None = None
        self.is_running = False

        self.root.title("Vehicle Platooning Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)

        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScale", background=BG_COLOR, foreground=FG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
        style.configure("TFrame", background=BG_COLOR)

    def _build_layout(self) -> None:
        header_frame = tk.Frame(self.root, bg=SECONDARY_COLOR, height=60)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="Vehicle Platooning System - ACO Optimization",
            font=("Helvetica", 18, "bold"),
            bg=SECONDARY_COLOR,
            fg=ACCENT_COLOR,
        )
        title_label.pack(pady=15)

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        left_panel = tk.Frame(main_frame, bg=SECONDARY_COLOR, relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", padx=(0, 10))

        tk.Label(
            left_panel,
            text="Configuration",
            font=("Helvetica", 12, "bold"),
            bg=SECONDARY_COLOR,
            fg=ACCENT_COLOR,
        ).pack(pady=10, padx=10)

        slider_frame = tk.Frame(left_panel, bg=SECONDARY_COLOR)
        slider_frame.pack(padx=10, pady=10)

        self.runs_slider, self.runs_value_label = self._create_slider(
            slider_frame,
            label="Simulation Runs",
            row=0,
            from_=50,
            to=500,
            resolution=1,
            initial=200,
            formatter=lambda value: str(int(float(value))),
        )
        self.fail_slider, self.fail_value_label = self._create_slider(
            slider_frame,
            label="Failure Rate",
            row=1,
            from_=0.0,
            to=0.5,
            resolution=0.05,
            initial=0.2,
            formatter=lambda value: f"{float(value):.2f}",
        )
        self.cong_slider, self.cong_value_label = self._create_slider(
            slider_frame,
            label="Congestion Level",
            row=2,
            from_=1.0,
            to=3.0,
            resolution=0.1,
            initial=1.5,
            formatter=lambda value: f"{float(value):.2f}",
        )

        button_frame = tk.Frame(left_panel, bg=SECONDARY_COLOR)
        button_frame.pack(padx=10, pady=15, fill="x")

        self.run_btn = self._create_button(button_frame, "Run Simulation", self.run_simulation)
        self._create_button(button_frame, "Run Animation", self.run_animation)
        self._create_button(button_frame, "Export CSV", self.export_csv)
        self._create_button(button_frame, "Generate Report", self.generate_report)
        self._create_button(button_frame, "Exit", self.root.quit, color="#d32f2f")

        right_panel = tk.Frame(main_frame, bg=BG_COLOR)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            right_panel,
            text="Results",
            font=("Helvetica", 12, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
        ).pack(pady=10)

        self.result_text = tk.StringVar(value="Click 'Run Simulation' to start analyzing.")
        result_display = tk.Label(
            right_panel,
            textvariable=self.result_text,
            font=("Courier", 10),
            bg=SECONDARY_COLOR,
            fg=FG_COLOR,
            justify="left",
            relief="flat",
            wraplength=400,
            padx=15,
            pady=15,
        )
        result_display.pack(fill="both", expand=True, padx=0, pady=10)

        self.progress_bar = ttk.Progressbar(right_panel, mode="indeterminate", length=300)
        self.progress_bar.pack(pady=10, fill="x")

        self.status_label = tk.Label(
            right_panel,
            text="Ready",
            font=("Helvetica", 9),
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
        )
        self.status_label.pack(pady=5)

        self.fig = Figure(figsize=(9, 4), dpi=100)
        self.fig.patch.set_facecolor(BG_COLOR)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=10)

    def _create_slider(
        self,
        parent: tk.Frame,
        label: str,
        row: int,
        from_: float,
        to: float,
        resolution: float,
        initial: float,
        formatter,
    ) -> tuple[tk.Scale, tk.Label]:
        tk.Label(
            parent,
            text=label,
            bg=SECONDARY_COLOR,
            fg=FG_COLOR,
            font=("Helvetica", 10),
        ).grid(row=row, column=0, sticky="w", pady=8)

        value_label = tk.Label(
            parent,
            text=formatter(initial),
            bg=SECONDARY_COLOR,
            fg=ACCENT_COLOR,
            font=("Helvetica", 9, "bold"),
        )
        value_label.grid(row=row, column=2, padx=5)

        def update_value(value: str) -> None:
            value_label.config(text=formatter(float(value)))

        slider = tk.Scale(
            parent,
            from_=from_,
            to=to,
            resolution=resolution,
            orient="horizontal",
            bg=BUTTON_BG,
            fg=ACCENT_COLOR,
            highlightthickness=0,
            troughcolor=BUTTON_BG,
            length=200,
            command=update_value,
        )
        slider.set(initial)
        slider.grid(row=row, column=1, padx=10, pady=8)
        return slider, value_label

    def _create_button(self, parent: tk.Frame, text: str, command, color: str = BUTTON_BG) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=ACCENT_COLOR,
            font=("Helvetica", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            cursor="hand2",
            activebackground=BUTTON_HOVER,
            activeforeground=ACCENT_COLOR,
        )
        button.pack(fill="x", pady=5)
        return button

    def run_simulation(self) -> None:
        if self.is_running:
            messagebox.showwarning("Running", "Simulation already in progress.")
            return

        self.is_running = True
        self.run_btn.config(state="disabled", bg="#555555")
        self.progress_bar.start()
        self.status_label.config(text="Running simulation...", fg=ACCENT_COLOR)

        runs = int(self.runs_slider.get())
        failure_rate = float(self.fail_slider.get())
        congestion_factor = float(self.cong_slider.get())

        thread = threading.Thread(
            target=self._run_worker,
            args=(runs, failure_rate, congestion_factor),
            daemon=True,
        )
        thread.start()

    def _run_worker(self, runs: int, failure_rate: float, congestion_factor: float) -> None:
        try:
            results = run_simulation(runs, failure_rate, congestion_factor, verbose=False)
        except Exception as exc:
            message = str(exc)
            self.root.after(0, lambda: self._finish_error(message))
        else:
            self.root.after(0, lambda: self._finish_success(results))

    def _finish_success(self, results: dict[str, float]) -> None:
        self.last_results = results
        self.result_text.set(self._format_result_text(results))
        self._update_graph()
        self.status_label.config(text="Simulation complete.", fg=SUCCESS_COLOR)
        self._reset_running_state()

    def _finish_error(self, message: str) -> None:
        self.status_label.config(text=f"Error: {message}", fg=WARNING_COLOR)
        messagebox.showerror("Error", f"Simulation failed: {message}")
        self._reset_running_state()

    def _reset_running_state(self) -> None:
        self.progress_bar.stop()
        self.run_btn.config(state="normal", bg=BUTTON_BG)
        self.is_running = False

    def _format_result_text(self, results: dict[str, float]) -> str:
        pdr_delta = _percent_change(results["pdr_aco"], results["pdr_base"])
        latency_delta = _percent_change(results["lat_aco"], results["lat_base"], lower_is_better=True)
        redundancy_delta = _percent_change(results["red_aco"], results["red_base"])

        return (
            f"PDR (Packet Delivery): ACO {results['pdr_aco']:.3f} vs Base {results['pdr_base']:.3f} "
            f"({pdr_delta})\n"
            f"Latency: ACO {results['lat_aco']:.3f} vs Base {results['lat_base']:.3f} "
            f"({latency_delta})\n"
            f"Redundancy: ACO {results['red_aco']:.3f} vs Base {results['red_base']:.3f} "
            f"({redundancy_delta})"
        )

    def _update_graph(self) -> None:
        if not self.last_results:
            return

        self.fig.clear()
        axes = self.fig.subplots(1, 3)
        self.fig.patch.set_facecolor(SECONDARY_COLOR)

        charts = (
            ("PDR", [self.last_results["pdr_aco"], self.last_results["pdr_base"]], (0, 1)),
            ("Latency", [self.last_results["lat_aco"], self.last_results["lat_base"]], None),
            ("Redundancy", [self.last_results["red_aco"], self.last_results["red_base"]], None),
        )

        for axis, (title, values, y_limit) in zip(axes, charts):
            bars = axis.bar(["ACO", "Baseline"], values, color=[ACCENT_COLOR, WARNING_COLOR], edgecolor="white")
            axis.set_title(title, fontsize=10, color=FG_COLOR, fontweight="bold")
            axis.set_facecolor(SECONDARY_COLOR)
            axis.tick_params(colors=FG_COLOR)
            axis.spines["bottom"].set_color(FG_COLOR)
            axis.spines["left"].set_color(FG_COLOR)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
            if y_limit:
                axis.set_ylim(*y_limit)

            for bar in bars:
                height = bar.get_height()
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{height:.2f}",
                    ha="center",
                    va="bottom",
                    color=FG_COLOR,
                    fontsize=9,
                    fontweight="bold",
                )

        self.fig.tight_layout()
        self.canvas.draw()

    def export_csv(self) -> None:
        if not self.last_results:
            messagebox.showwarning("No Data", "Run simulation first.")
            return

        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "results.csv"
        write_header = not output_file.exists()

        with output_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                    "pdr_aco": self.last_results["pdr_aco"],
                    "pdr_base": self.last_results["pdr_base"],
                    "lat_aco": self.last_results["lat_aco"],
                    "lat_base": self.last_results["lat_base"],
                    "red_aco": self.last_results["red_aco"],
                    "red_base": self.last_results["red_base"],
                }
            )

        self.result_text.set(f"Saved to {output_file}")
        self.status_label.config(text="CSV exported successfully.", fg=SUCCESS_COLOR)

    def generate_report(self) -> None:
        if not self.last_results:
            messagebox.showwarning("No Data", "Run simulation first.")
            return

        results = self.last_results
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "report.txt"

        pdr_delta = _percent_change(results["pdr_aco"], results["pdr_base"])
        latency_delta = _percent_change(results["lat_aco"], results["lat_base"], lower_is_better=True)
        redundancy_delta = _percent_change(results["red_aco"], results["red_base"])
        aco_wins = sum(
            [
                results["pdr_aco"] > results["pdr_base"],
                results["lat_aco"] < results["lat_base"],
                results["red_aco"] > results["red_base"],
            ]
        )
        conclusion = (
            "ACO is superior in this run."
            if aco_wins >= 3
            else "ACO improves most metrics in this run."
            if aco_wins >= 2
            else "Results are mixed in this run."
        )

        report = f"""VEHICLE PLATOONING PERFORMANCE REPORT
Generated: {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PACKET DELIVERY RATE (PDR)
  ACO Algorithm: {results["pdr_aco"]:.4f}
  Baseline:      {results["pdr_base"]:.4f}
  Change:        {pdr_delta}

LATENCY
  ACO Algorithm: {results["lat_aco"]:.4f}
  Baseline:      {results["lat_base"]:.4f}
  Change:        {latency_delta}

REDUNDANCY SCORE
  ACO Algorithm: {results["red_aco"]:.4f}
  Baseline:      {results["red_base"]:.4f}
  Change:        {redundancy_delta}

CONCLUSION
{conclusion}
"""
        output_file.write_text(report, encoding="utf-8")
        self.result_text.set(f"Report generated: {output_file}")
        self.status_label.config(text="Report generated successfully.", fg=SUCCESS_COLOR)

    def run_animation(self) -> None:
        try:
            subprocess.Popen([sys.executable, str(BASE_DIR / "vehicle_animation.py")])
            self.status_label.config(text="Animation started.", fg=SUCCESS_COLOR)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to start animation: {exc}")
            self.status_label.config(text="Animation failed to start.", fg=WARNING_COLOR)


def main() -> None:
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
