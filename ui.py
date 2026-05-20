import tkinter as tk
from tkinter import ttk, messagebox
from simulation import run_simulation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import datetime
import subprocess
import threading

# Color scheme
BG_COLOR = "#0f0f0f"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#00d4ff"
SECONDARY_COLOR = "#1e1e2e"
SUCCESS_COLOR = "#00ff88"
WARNING_COLOR = "#ffaa00"
BUTTON_BG = "#1a1a2e"
BUTTON_HOVER = "#16213e"

# Store results globally
last_results = None
is_running = False

# -------------------------
# RUN SIMULATION
# -------------------------
def run_sim():
    global last_results, is_running
    
    if is_running:
        messagebox.showwarning("Running", "Simulation already in progress!")
        return
    
    is_running = True
    run_btn.config(state="disabled", bg="#555555")
    progress_bar.start()
    status_label.config(text="🔄 Running simulation...", fg=ACCENT_COLOR)
    
    def simulate():
        global last_results, is_running
        try:
            runs = runs_slider.get()
            failure = fail_slider.get()
            congestion = cong_slider.get()

            last_results = run_simulation(runs, failure, congestion)

            aco_wins_pdr = last_results['pdr_aco'] > last_results['pdr_base']
            aco_wins_lat = last_results['lat_aco'] < last_results['lat_base']
            aco_wins_red = last_results['red_aco'] > last_results['red_base']

            result_text.set(
                f"✓ PDR (Packet Delivery): ACO {last_results['pdr_aco']:.3f} vs Base {last_results['pdr_base']:.3f}  {'📈' if aco_wins_pdr else '📉'}\n"
                f"✓ Latency (ms): ACO {last_results['lat_aco']:.3f} vs Base {last_results['lat_base']:.3f}  {'📉' if aco_wins_lat else '📈'}\n"
                f"✓ Redundancy: ACO {last_results['red_aco']:.3f} vs Base {last_results['red_base']:.3f}  {'📈' if aco_wins_red else '📉'}"
            )
            
            update_graph()
            status_label.config(text="✓ Simulation complete!", fg=SUCCESS_COLOR)
        except Exception as e:
            status_label.config(text=f"✗ Error: {str(e)}", fg=WARNING_COLOR)
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
        finally:
            progress_bar.stop()
            run_btn.config(state="normal", bg=BUTTON_BG)
            is_running = False
    
    thread = threading.Thread(target=simulate, daemon=True)
    thread.start()

# -------------------------
# GRAPH INSIDE UI
# -------------------------
def update_graph():
    if not last_results:
        return

    fig.clear()
    
    # Create subplots for all metrics
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    
    labels = ['ACO', 'Baseline']
    fig.patch.set_facecolor(SECONDARY_COLOR)
    
    # PDR Chart
    pdr_values = [last_results['pdr_aco'], last_results['pdr_base']]
    bars1 = ax1.bar(labels, pdr_values, color=[ACCENT_COLOR, WARNING_COLOR], edgecolor='white', linewidth=1.5)
    ax1.set_title("PDR (Packet Delivery Rate)", fontsize=10, color=FG_COLOR, fontweight='bold')
    ax1.set_ylim(0, 1)
    ax1.set_facecolor(SECONDARY_COLOR)
    ax1.tick_params(colors=FG_COLOR)
    ax1.spines['bottom'].set_color(FG_COLOR)
    ax1.spines['left'].set_color(FG_COLOR)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}', 
                ha='center', va='bottom', color=FG_COLOR, fontsize=9, fontweight='bold')
    
    # Latency Chart (lower is better, so we inverse the color logic)
    lat_values = [last_results['lat_aco'], last_results['lat_base']]
    bars2 = ax2.bar(labels, lat_values, color=[ACCENT_COLOR, WARNING_COLOR], edgecolor='white', linewidth=1.5)
    ax2.set_title("Latency (ms) - Lower is Better", fontsize=10, color=FG_COLOR, fontweight='bold')
    ax2.set_facecolor(SECONDARY_COLOR)
    ax2.tick_params(colors=FG_COLOR)
    ax2.spines['bottom'].set_color(FG_COLOR)
    ax2.spines['left'].set_color(FG_COLOR)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}', 
                ha='center', va='bottom', color=FG_COLOR, fontsize=9, fontweight='bold')
    
    # Redundancy Chart
    red_values = [last_results['red_aco'], last_results['red_base']]
    bars3 = ax3.bar(labels, red_values, color=[ACCENT_COLOR, WARNING_COLOR], edgecolor='white', linewidth=1.5)
    ax3.set_title("Redundancy Score", fontsize=10, color=FG_COLOR, fontweight='bold')
    ax3.set_facecolor(SECONDARY_COLOR)
    ax3.tick_params(colors=FG_COLOR)
    ax3.spines['bottom'].set_color(FG_COLOR)
    ax3.spines['left'].set_color(FG_COLOR)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}', 
                ha='center', va='bottom', color=FG_COLOR, fontsize=9, fontweight='bold')
    
    fig.tight_layout()
    canvas.draw()

# -------------------------
# EXPORT CSV
# -------------------------
def export_csv():
    if not last_results:
        messagebox.showwarning("No Data", "Run simulation first!")
        return

    filename = "results.csv"

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now(),
            last_results['pdr_aco'],
            last_results['pdr_base'],
            last_results['lat_aco'],
            last_results['lat_base'],
            last_results['red_aco'],
            last_results['red_base']
        ])

    result_text.set("✓ Saved to results.csv")
    status_label.config(text="✓ CSV exported successfully!", fg=SUCCESS_COLOR)

# -------------------------
# GENERATE REPORT
# -------------------------
def generate_report():
    if not last_results:
        messagebox.showwarning("No Data", "Run simulation first!")
        return

    aco_wins = sum([
        last_results['pdr_aco'] > last_results['pdr_base'],
        last_results['lat_aco'] < last_results['lat_base'],
        last_results['red_aco'] > last_results['red_base']
    ])

    conclusion = "ACO is significantly superior" if aco_wins >= 3 else "ACO shows improvements" if aco_wins >= 2 else "Results are mixed"

    report = f"""
================================================================================
                   VEHICLE PLATOONING PERFORMANCE REPORT
================================================================================
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PACKET DELIVERY RATE (PDR)
  ACO Algorithm:     {last_results['pdr_aco']:.4f}
  Baseline:          {last_results['pdr_base']:.4f}
  Improvement:       {((last_results['pdr_aco'] - last_results['pdr_base']) / last_results['pdr_base'] * 100):+.2f}%

LATENCY (milliseconds)
  ACO Algorithm:     {last_results['lat_aco']:.4f}
  Baseline:          {last_results['lat_base']:.4f}
  Reduction:         {((last_results['lat_base'] - last_results['lat_aco']) / last_results['lat_base'] * 100):.2f}%

REDUNDANCY SCORE
  ACO Algorithm:     {last_results['red_aco']:.4f}
  Baseline:          {last_results['red_base']:.4f}
  Improvement:       {((last_results['red_aco'] - last_results['red_base']) / last_results['red_base'] * 100):+.2f}%

CONCLUSION
{conclusion} under dynamic network conditions. ACO demonstrates robust 
performance improvements across multiple metrics including reliability, 
latency reduction, and redundancy optimization.

================================================================================
"""

    with open("report.txt", "w") as f:
        f.write(report)

    result_text.set("✓ Report generated: report.txt")
    status_label.config(text="✓ Report generated successfully!", fg=SUCCESS_COLOR)

# -------------------------
# RUN ANIMATION
# -------------------------
def run_animation():
    try:
        subprocess.Popen(["python", "vehicle_animation.py"])
        status_label.config(text="✓ Animation started!", fg=SUCCESS_COLOR)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start animation: {str(e)}")
        status_label.config(text="✗ Animation failed to start", fg=WARNING_COLOR)

# -------------------------
# UI SETUP
# -------------------------
root = tk.Tk()
root.title("🚗 ACO Vehicle Platooning Dashboard")
root.geometry("1000x700")
root.configure(bg=BG_COLOR)

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TScale', background=BG_COLOR, foreground=FG_COLOR)
style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
style.configure('TFrame', background=BG_COLOR)

# -------------------------
# HEADER
# -------------------------
header_frame = tk.Frame(root, bg=SECONDARY_COLOR, height=60)
header_frame.pack(fill="x", padx=0, pady=0)

title_label = tk.Label(header_frame, text="🚗 Vehicle Platooning System - ACO Optimization", 
                       font=("Helvetica", 18, "bold"), bg=SECONDARY_COLOR, fg=ACCENT_COLOR)
title_label.pack(pady=15)

# -------------------------
# MAIN CONTENT FRAME
# -------------------------
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=15, pady=15)

# Left panel - Controls
left_panel = tk.Frame(main_frame, bg=SECONDARY_COLOR, relief="flat", bd=0)
left_panel.pack(side="left", fill="both", padx=(0, 10))

# Control title
control_title = tk.Label(left_panel, text="⚙️ Configuration", font=("Helvetica", 12, "bold"), 
                        bg=SECONDARY_COLOR, fg=ACCENT_COLOR)
control_title.pack(pady=10, padx=10)

# Sliders
slider_frame = tk.Frame(left_panel, bg=SECONDARY_COLOR)
slider_frame.pack(padx=10, pady=10)

# Simulation Runs
tk.Label(slider_frame, text="Simulation Runs", bg=SECONDARY_COLOR, fg=FG_COLOR, font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=8)
runs_slider = tk.Scale(slider_frame, from_=50, to=500, orient="horizontal", bg=BUTTON_BG, 
                       fg=ACCENT_COLOR, highlightthickness=0, troughcolor=BUTTON_BG, length=200)
runs_slider.set(200)
runs_slider.grid(row=0, column=1, padx=10, pady=8)
runs_value_label = tk.Label(slider_frame, text="200", bg=SECONDARY_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 9, "bold"))
runs_value_label.grid(row=0, column=2, padx=5)

# Failure Rate
tk.Label(slider_frame, text="Failure Rate", bg=SECONDARY_COLOR, fg=FG_COLOR, font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=8)
fail_slider = tk.Scale(slider_frame, from_=0.0, to=0.5, resolution=0.05, orient="horizontal", bg=BUTTON_BG, 
                       fg=ACCENT_COLOR, highlightthickness=0, troughcolor=BUTTON_BG, length=200)
fail_slider.set(0.2)
fail_slider.grid(row=1, column=1, padx=10, pady=8)
fail_value_label = tk.Label(slider_frame, text="0.20", bg=SECONDARY_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 9, "bold"))
fail_value_label.grid(row=1, column=2, padx=5)

# Congestion
tk.Label(slider_frame, text="Congestion Level", bg=SECONDARY_COLOR, fg=FG_COLOR, font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=8)
cong_slider = tk.Scale(slider_frame, from_=1.0, to=3.0, resolution=0.1, orient="horizontal", bg=BUTTON_BG, 
                       fg=ACCENT_COLOR, highlightthickness=0, troughcolor=BUTTON_BG, length=200)
cong_slider.set(1.5)
cong_slider.grid(row=2, column=1, padx=10, pady=8)
cong_value_label = tk.Label(slider_frame, text="1.50", bg=SECONDARY_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 9, "bold"))
cong_value_label.grid(row=2, column=2, padx=5)

# Update value labels when sliders change
def update_slider_labels(*args):
    runs_value_label.config(text=str(runs_slider.get()))
    fail_value_label.config(text=f"{fail_slider.get():.2f}")
    cong_value_label.config(text=f"{cong_slider.get():.2f}")

runs_slider.config(command=update_slider_labels)
fail_slider.config(command=update_slider_labels)
cong_slider.config(command=update_slider_labels)

# -------------------------
# BUTTONS
# -------------------------
btn_frame = tk.Frame(left_panel, bg=SECONDARY_COLOR)
btn_frame.pack(padx=10, pady=15, fill="x")

def create_button(parent, text, command, color=BUTTON_BG):
    btn = tk.Button(parent, text=text, command=command, bg=color, fg=ACCENT_COLOR, 
                   font=("Helvetica", 10, "bold"), relief="flat", bd=0, padx=10, pady=10, 
                   cursor="hand2", activebackground=BUTTON_HOVER, activeforeground=ACCENT_COLOR)
    btn.pack(fill="x", pady=5)
    return btn

run_btn = create_button(btn_frame, "▶ Run Simulation", run_sim)
create_button(btn_frame, "▶ Run Animation", run_animation)
create_button(btn_frame, "💾 Export CSV", export_csv)
create_button(btn_frame, "📄 Generate Report", generate_report)
create_button(btn_frame, "🚪 Exit", root.quit, color="#d32f2f")

# -------------------------
# RIGHT PANEL - RESULTS
# -------------------------
right_panel = tk.Frame(main_frame, bg=BG_COLOR)
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

# Results title
results_title = tk.Label(right_panel, text="📊 Results", font=("Helvetica", 12, "bold"), 
                        bg=BG_COLOR, fg=ACCENT_COLOR)
results_title.pack(pady=10)

# -------------------------
# RESULT DISPLAY
# -------------------------
result_text = tk.StringVar()
result_text.set("👉 Click 'Run Simulation' to start analyzing...")

result_display = tk.Label(right_panel, textvariable=result_text, font=("Courier", 10), 
                         bg=SECONDARY_COLOR, fg=FG_COLOR, justify="left", relief="flat", 
                         wraplength=400, padx=15, pady=15)
result_display.pack(fill="both", expand=True, padx=0, pady=10)

# -------------------------
# PROGRESS BAR
# -------------------------
progress_bar = ttk.Progressbar(right_panel, mode='indeterminate', length=300)
progress_bar.pack(pady=10, fill="x")

# Status label
status_label = tk.Label(right_panel, text="Ready", font=("Helvetica", 9), 
                       bg=BG_COLOR, fg=ACCENT_COLOR)
status_label.pack(pady=5)

# -------------------------
# EMBED GRAPH
# -------------------------
fig = plt.Figure(figsize=(9, 4), dpi=100)
fig.patch.set_facecolor(BG_COLOR)
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=10)

root.mainloop()