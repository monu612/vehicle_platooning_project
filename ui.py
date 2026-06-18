from __future__ import annotations

import csv
import datetime as dt
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import messagebox, ttk
import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from simulation import run_simulation, SimulationResult


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
RESULT_FIELDS = (
    "timestamp",
    "pdr_aco",
    "pdr_base",
    "pdr_greedy",
    "lat_aco",
    "lat_base",
    "lat_greedy",
    "red_aco",
    "red_base",
    "red_greedy",
)

# ---- Color palette ----
BG = "#0a0a14"
CARD = "#13132a"
CARD_BORDER = "#1e1e3a"
ACCENT = "#00d4ff"
ACCENT_DIM = "#0088aa"
GREEN = "#00ff88"
ORANGE = "#ffaa00"
RED = "#ff5577"
WHITE = "#f0f0f5"
DIM = "#888899"
BUTTON_BG = "#1a1a35"
BUTTON_HOVER = "#252550"
SLIDER_TROUGH = "#1a1a35"


def _percent_change(new_value: float, old_value: float, lower_is_better: bool = False) -> str:
    if old_value == 0:
        return "n/a"
    delta = ((old_value - new_value) if lower_is_better else (new_value - old_value)) / old_value
    return f"{delta * 100:+.1f}%"


class Dashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.last_result: SimulationResult | None = None
        self.is_running = False

        self.root.title("Vehicle Platooning — ACO Optimizer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self._configure_style()
        self._build_layout()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=CARD, foreground=DIM,
                        padding=[14, 6], font=("Helvetica", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", BUTTON_BG)],
                  foreground=[("selected", ACCENT)])

        style.configure("TScale", background=BG, foreground=WHITE)
        style.configure("TLabel", background=BG, foreground=WHITE)
        style.configure("TFrame", background=BG)

        style.configure("TProgressbar",
                        background=ACCENT, troughcolor=CARD,
                        borderwidth=0, thickness=6)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        # ---- HEADER ----
        header = tk.Frame(self.root, bg=CARD, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="🚗  Vehicle Platooning — ACO Optimizer",
            font=("Helvetica", 16, "bold"), bg=CARD, fg=ACCENT,
        ).pack(side="left", padx=18, pady=12)

        self.status_label = tk.Label(
            header, text="● Ready", font=("Helvetica", 10), bg=CARD, fg=GREEN,
        )
        self.status_label.pack(side="right", padx=18)

        # ---- BODY: sidebar + main ----
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        self._build_sidebar(body)
        self._build_main(body)

    # ---- Sidebar ----

    def _build_sidebar(self, parent: tk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=CARD, width=260, relief="flat", bd=0,
                           highlightthickness=1, highlightbackground=CARD_BORDER)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)

        # Section title
        tk.Label(
            sidebar, text="⚙  Configuration",
            font=("Helvetica", 12, "bold"), bg=CARD, fg=WHITE,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Separator
        tk.Frame(sidebar, bg=CARD_BORDER, height=1).pack(fill="x", padx=16, pady=4)

        slider_frame = tk.Frame(sidebar, bg=CARD)
        slider_frame.pack(fill="x", padx=16, pady=8)

        self.runs_slider, self.runs_lbl = self._slider(
            slider_frame, "Simulation Runs", 0, 50, 500, 1, 200,
            fmt=lambda v: str(int(float(v))),
            tooltip="Number of iterations the ACO algorithm runs",
        )
        self.fail_slider, self.fail_lbl = self._slider(
            slider_frame, "Link Failure Rate", 1, 0.0, 0.5, 0.05, 0.2,
            fmt=lambda v: f"{float(v):.0%}",
            tooltip="Probability that a link fails each iteration",
        )
        self.cong_slider, self.cong_lbl = self._slider(
            slider_frame, "Congestion Factor", 2, 1.0, 3.0, 0.1, 1.5,
            fmt=lambda v: f"{float(v):.1f}×",
            tooltip="Maximum congestion multiplier applied to edges",
        )

        tk.Frame(sidebar, bg=CARD_BORDER, height=1).pack(fill="x", padx=16, pady=8)

        # Buttons
        btn_frame = tk.Frame(sidebar, bg=CARD)
        btn_frame.pack(fill="x", padx=16, pady=4)

        self.run_btn = self._button(btn_frame, "▶  Run Simulation", self.run_simulation, bg=ACCENT_DIM)
        self._button(btn_frame, "🎬  Animation", self.run_animation)
        self._button(btn_frame, "📊  Export CSV", self.export_csv)
        self._button(btn_frame, "📝  Report", self.generate_report)

        # spacer
        tk.Frame(sidebar, bg=CARD).pack(fill="both", expand=True)

        self._button(btn_frame, "✕  Exit", self.root.quit, bg="#3a1525")

    # ---- Main area ----

    def _build_main(self, parent: tk.Frame) -> None:
        main = tk.Frame(parent, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # ---- Summary cards ----
        cards_frame = tk.Frame(main, bg=BG)
        cards_frame.pack(fill="x", pady=(0, 8))

        self.card_pdr = self._metric_card(cards_frame, "Packet Delivery", "—", "—", 0)
        self.card_lat = self._metric_card(cards_frame, "Avg. Latency", "—", "—", 1)
        self.card_red = self._metric_card(cards_frame, "Avg. Hops", "—", "—", 2)
        self.card_greedy = self._metric_card(cards_frame, "Greedy PDR", "—", "—", 3)

        # Configure equal-width columns
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1, uniform="card")

        # ---- Progress bar ----
        self.progress_bar = ttk.Progressbar(main, mode="indeterminate", style="TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 6))

        # ---- Tabbed notebook ----
        self.notebook = ttk.Notebook(main, style="TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Comparison bars
        tab_compare = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_compare, text="  📊 Comparison  ")
        self.fig_compare = Figure(figsize=(9, 4), dpi=100)
        self.fig_compare.patch.set_facecolor(BG)
        self.canvas_compare = FigureCanvasTkAgg(self.fig_compare, master=tab_compare)
        self.canvas_compare.get_tk_widget().pack(fill="both", expand=True)

        # Tab 2: Convergence
        tab_conv = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_conv, text="  📈 Convergence  ")
        self.fig_conv = Figure(figsize=(9, 4), dpi=100)
        self.fig_conv.patch.set_facecolor(BG)
        self.canvas_conv = FigureCanvasTkAgg(self.fig_conv, master=tab_conv)
        self.canvas_conv.get_tk_widget().pack(fill="both", expand=True)

        # Tab 3: Network topology
        tab_topo = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_topo, text="  🔗 Topology  ")
        self.fig_topo = Figure(figsize=(9, 4), dpi=100)
        self.fig_topo.patch.set_facecolor(BG)
        self.canvas_topo = FigureCanvasTkAgg(self.fig_topo, master=tab_topo)
        self.canvas_topo.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Widget helpers
    # ------------------------------------------------------------------

    def _slider(self, parent, label, row, from_, to, res, initial, fmt, tooltip=""):
        # Label
        lbl = tk.Label(parent, text=label, bg=CARD, fg=DIM, font=("Helvetica", 9))
        lbl.grid(row=row * 2, column=0, sticky="w", pady=(8, 0), columnspan=2)

        # Tooltip on hover
        if tooltip:
            tip_lbl = tk.Label(parent, text=f"ℹ {tooltip}", bg=CARD, fg="#555566",
                               font=("Helvetica", 7), wraplength=220, justify="left")
            tip_lbl.grid(row=row * 2, column=0, sticky="e", pady=(8, 0), columnspan=2)
            tip_lbl.grid_remove()
            lbl.bind("<Enter>", lambda e: tip_lbl.grid())
            lbl.bind("<Leave>", lambda e: tip_lbl.grid_remove())

        # Value display
        val_lbl = tk.Label(parent, text=fmt(initial), bg=CARD, fg=ACCENT,
                           font=("Helvetica", 11, "bold"), width=6, anchor="e")
        val_lbl.grid(row=row * 2 + 1, column=1, padx=(4, 0), sticky="e")

        def on_change(v):
            val_lbl.config(text=fmt(v))

        slider = tk.Scale(
            parent, from_=from_, to=to, resolution=res, orient="horizontal",
            bg=CARD, fg=ACCENT, highlightthickness=0, troughcolor=SLIDER_TROUGH,
            length=160, command=on_change, showvalue=False,
            activebackground=ACCENT_DIM, bd=0,
        )
        slider.set(initial)
        slider.grid(row=row * 2 + 1, column=0, padx=0, pady=(0, 4), sticky="ew")

        return slider, val_lbl

    def _button(self, parent, text, command, bg=BUTTON_BG):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=WHITE, font=("Helvetica", 10, "bold"),
            relief="flat", bd=0, padx=10, pady=8, cursor="hand2",
            activebackground=BUTTON_HOVER, activeforeground=WHITE,
        )
        btn.pack(fill="x", pady=3)
        return btn

    def _metric_card(self, parent, title, value, delta, col):
        """Create a summary metric card."""
        frame = tk.Frame(parent, bg=CARD, relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=CARD_BORDER)
        frame.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)

        tk.Label(frame, text=title, bg=CARD, fg=DIM,
                 font=("Helvetica", 8)).pack(anchor="w", padx=10, pady=(8, 0))

        val_label = tk.Label(frame, text=value, bg=CARD, fg=WHITE,
                             font=("Helvetica", 18, "bold"))
        val_label.pack(anchor="w", padx=10)

        delta_label = tk.Label(frame, text=delta, bg=CARD, fg=GREEN,
                               font=("Helvetica", 9, "bold"))
        delta_label.pack(anchor="w", padx=10, pady=(0, 8))

        return val_label, delta_label

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def run_simulation(self) -> None:
        if self.is_running:
            messagebox.showwarning("Running", "Simulation already in progress.")
            return

        self.is_running = True
        self.run_btn.config(state="disabled", bg="#555555")
        self.progress_bar.start()
        self.status_label.config(text="● Running...", fg=ORANGE)

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
            result = run_simulation(runs, failure_rate, congestion_factor, verbose=False)
        except Exception as exc:
            message = str(exc)
            self.root.after(0, lambda: self._finish_error(message))
        else:
            self.root.after(0, lambda: self._finish_success(result))

    def _finish_success(self, result: SimulationResult) -> None:
        self.last_result = result
        self._update_cards(result)
        self._update_comparison_chart(result)
        self._update_convergence_chart(result)
        self._update_topology_chart()
        self.status_label.config(text="● Complete", fg=GREEN)
        self._reset_running_state()

    def _finish_error(self, message: str) -> None:
        self.status_label.config(text=f"● Error: {message}", fg=RED)
        messagebox.showerror("Error", f"Simulation failed: {message}")
        self._reset_running_state()

    def _reset_running_state(self) -> None:
        self.progress_bar.stop()
        self.run_btn.config(state="normal", bg=ACCENT_DIM)
        self.is_running = False

    # ------------------------------------------------------------------
    # Update displays
    # ------------------------------------------------------------------

    def _update_cards(self, r: SimulationResult) -> None:
        pdr_delta = _percent_change(r.pdr_aco, r.pdr_base)
        lat_delta = _percent_change(r.lat_aco, r.lat_base, lower_is_better=True)
        red_delta = _percent_change(r.red_aco, r.red_base)

        self.card_pdr[0].config(text=f"{r.pdr_aco:.1%}")
        self.card_pdr[1].config(
            text=f"vs Baseline: {pdr_delta}",
            fg=GREEN if r.pdr_aco >= r.pdr_base else RED,
        )

        self.card_lat[0].config(text=f"{r.lat_aco:.2f}")
        self.card_lat[1].config(
            text=f"vs Baseline: {lat_delta}",
            fg=GREEN if r.lat_aco <= r.lat_base else RED,
        )

        self.card_red[0].config(text=f"{r.red_aco:.1f}")
        self.card_red[1].config(
            text=f"vs Baseline: {red_delta}",
            fg=DIM,
        )

        self.card_greedy[0].config(text=f"{r.pdr_greedy:.1%}")
        greedy_delta = _percent_change(r.pdr_aco, r.pdr_greedy)
        self.card_greedy[1].config(
            text=f"ACO vs Greedy: {greedy_delta}",
            fg=GREEN if r.pdr_aco >= r.pdr_greedy else RED,
        )

    def _update_comparison_chart(self, r: SimulationResult) -> None:
        self.fig_compare.clear()
        axes = self.fig_compare.subplots(1, 3)
        self.fig_compare.patch.set_facecolor(BG)

        charts = [
            ("PDR", [r.pdr_aco, r.pdr_base, r.pdr_greedy], (0, 1.15)),
            ("Latency", [r.lat_aco, r.lat_base, r.lat_greedy], None),
            ("Hops", [r.red_aco, r.red_base, r.red_greedy], None),
        ]
        labels = ["ACO", "Shortest\nPath", "Greedy"]
        colors = [ACCENT, ORANGE, RED]

        for ax, (title, values, ylim) in zip(axes, charts):
            ax.set_facecolor(CARD)
            bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.55, zorder=3)
            ax.set_title(title, fontsize=11, color=WHITE, fontweight="bold", pad=8)
            ax.tick_params(colors=DIM, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=0.2, color=CARD_BORDER)
            if ylim:
                ax.set_ylim(*ylim)

            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + max(values) * 0.02,
                        f"{h:.3f}", ha="center", va="bottom",
                        color=WHITE, fontsize=9, fontweight="bold")

        self.fig_compare.tight_layout(pad=2)
        self.canvas_compare.draw()

    def _update_convergence_chart(self, r: SimulationResult) -> None:
        self.fig_conv.clear()
        ax1, ax2 = self.fig_conv.subplots(1, 2)
        self.fig_conv.patch.set_facecolor(BG)

        history = r.history
        if not history:
            self.canvas_conv.draw()
            return

        # Smooth
        window = max(1, len(history) // 20)
        kernel = np.ones(window) / window

        def smooth(data):
            arr = np.array(data, dtype=float)
            return np.convolve(arr, kernel, mode="valid")

        pdr_aco = smooth([h.pdr_aco for h in history])
        pdr_base = smooth([h.pdr_base for h in history])
        pdr_greedy = smooth([h.pdr_greedy for h in history])
        x = np.arange(1, len(pdr_aco) + 1)

        for ax in (ax1, ax2):
            ax.set_facecolor(CARD)
            ax.tick_params(colors=DIM, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(CARD_BORDER)
            ax.grid(axis="y", linestyle="--", alpha=0.2, color=CARD_BORDER)

        # PDR convergence
        ax1.plot(x, pdr_aco, color=ACCENT, linewidth=2, label="ACO")
        ax1.plot(x, pdr_base, color=ORANGE, linewidth=1.5, label="Shortest Path", alpha=0.7)
        ax1.plot(x, pdr_greedy, color=RED, linewidth=1.5, label="Greedy", alpha=0.7)
        ax1.fill_between(x, pdr_aco, alpha=0.1, color=ACCENT)
        ax1.set_title("PDR Over Iterations", fontsize=11, color=WHITE, fontweight="bold")
        ax1.set_xlabel("Iteration", color=DIM, fontsize=9)
        ax1.set_ylabel("PDR", color=DIM, fontsize=9)
        ax1.set_ylim(-0.05, 1.15)
        ax1.legend(facecolor=CARD, edgecolor=CARD_BORDER, labelcolor=WHITE, fontsize=7)

        # Latency convergence
        lat_aco = smooth([h.lat_aco for h in history])
        lat_base = smooth([h.lat_base for h in history])
        lat_greedy = smooth([h.lat_greedy for h in history])
        x2 = np.arange(1, len(lat_aco) + 1)

        ax2.plot(x2, lat_aco, color=ACCENT, linewidth=2, label="ACO")
        ax2.plot(x2, lat_base, color=ORANGE, linewidth=1.5, label="Shortest Path", alpha=0.7)
        ax2.plot(x2, lat_greedy, color=RED, linewidth=1.5, label="Greedy", alpha=0.7)
        ax2.fill_between(x2, lat_aco, alpha=0.1, color=ACCENT)
        ax2.set_title("Latency Over Iterations", fontsize=11, color=WHITE, fontweight="bold")
        ax2.set_xlabel("Iteration", color=DIM, fontsize=9)
        ax2.set_ylabel("Latency", color=DIM, fontsize=9)
        ax2.legend(facecolor=CARD, edgecolor=CARD_BORDER, labelcolor=WHITE, fontsize=7)

        self.fig_conv.tight_layout(pad=2)
        self.canvas_conv.draw()

    def _update_topology_chart(self) -> None:
        """Draw the network topology with pheromone-weighted edges."""
        from network import create_spider_web_topology
        self.fig_topo.clear()
        ax = self.fig_topo.add_subplot(111)
        self.fig_topo.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.axis("off")

        G = create_spider_web_topology(seed=42)
        pos = nx.spring_layout(G, seed=42, k=2)

        # Draw edges
        for u, v in G.edges():
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            weight = G[u][v].get("weight", 1.0)
            ax.plot(x, y, color=ACCENT, linewidth=1.5, alpha=0.4)
            mx, my = (x[0] + x[1]) / 2, (y[0] + y[1]) / 2
            ax.text(mx, my, f"{weight:.1f}", fontsize=7, color=DIM,
                    ha="center", va="center")

        # Draw nodes
        for node in G.nodes():
            x, y = pos[node]
            is_master = node == "M"
            color = GREEN if is_master else ACCENT
            size = 500 if is_master else 350
            ax.scatter(x, y, s=size * 2, color=color, alpha=0.1, zorder=3)
            ax.scatter(x, y, s=size, color=color, alpha=0.9, zorder=5,
                       edgecolors="white", linewidth=1.2)
            ax.text(x, y, node, ha="center", va="center",
                    fontsize=9 if is_master else 7.5,
                    fontweight="bold", color="#000000", zorder=6)

        ax.set_title("Network Topology (Edge Labels = Latency)",
                     fontsize=11, color=WHITE, fontweight="bold", pad=10)

        self.fig_topo.tight_layout()
        self.canvas_topo.draw()

    # ------------------------------------------------------------------
    # Export / Report
    # ------------------------------------------------------------------

    def export_csv(self) -> None:
        if not self.last_result:
            messagebox.showwarning("No Data", "Run simulation first.")
            return

        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "results.csv"
        write_header = not output_file.exists()

        r = self.last_result
        with output_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow({
                "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                "pdr_aco": r.pdr_aco,
                "pdr_base": r.pdr_base,
                "pdr_greedy": r.pdr_greedy,
                "lat_aco": r.lat_aco,
                "lat_base": r.lat_base,
                "lat_greedy": r.lat_greedy,
                "red_aco": r.red_aco,
                "red_base": r.red_base,
                "red_greedy": r.red_greedy,
            })

        self.status_label.config(text=f"● Exported → {output_file.name}", fg=GREEN)

    def generate_report(self) -> None:
        if not self.last_result:
            messagebox.showwarning("No Data", "Run simulation first.")
            return

        r = self.last_result
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "report.txt"

        pdr_d = _percent_change(r.pdr_aco, r.pdr_base)
        lat_d = _percent_change(r.lat_aco, r.lat_base, lower_is_better=True)
        red_d = _percent_change(r.red_aco, r.red_base)

        aco_wins = sum([
            r.pdr_aco > r.pdr_base,
            r.lat_aco < r.lat_base,
        ])
        conclusion = (
            "ACO outperforms both baselines in this run."
            if aco_wins >= 2
            else "ACO improves key metrics versus the baselines."
            if aco_wins >= 1
            else "Results are mixed — consider tuning α, β, ρ parameters."
        )

        report = f"""VEHICLE PLATOONING PERFORMANCE REPORT
Generated: {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

══════════════════════════════════════
PACKET DELIVERY RATE (PDR)
  ACO Algorithm:   {r.pdr_aco:.4f}
  Shortest Path:   {r.pdr_base:.4f}
  Greedy Fwd:      {r.pdr_greedy:.4f}
  ACO vs Baseline: {pdr_d}

LATENCY
  ACO Algorithm:   {r.lat_aco:.4f}
  Shortest Path:   {r.lat_base:.4f}
  Greedy Fwd:      {r.lat_greedy:.4f}
  ACO vs Baseline: {lat_d}

REDUNDANCY (HOP COUNT)
  ACO Algorithm:   {r.red_aco:.4f}
  Shortest Path:   {r.red_base:.4f}
  Greedy Fwd:      {r.red_greedy:.4f}
  ACO vs Baseline: {red_d}

PACKETS
  Sent:              {r.packets_sent}
  Received (ACO):    {r.packets_received_aco}
  Received (Base):   {r.packets_received_baseline}
  Received (Greedy): {r.packets_received_greedy}
══════════════════════════════════════

CONCLUSION
{conclusion}
"""
        output_file.write_text(report, encoding="utf-8")
        self.status_label.config(text=f"● Report → {output_file.name}", fg=GREEN)

    def run_animation(self) -> None:
        try:
            subprocess.Popen([sys.executable, str(BASE_DIR / "vehicle_animation.py")])
            self.status_label.config(text="● Animation started", fg=GREEN)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to start animation: {exc}")
            self.status_label.config(text="● Animation failed", fg=RED)


def main() -> None:
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
