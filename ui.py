import tkinter as tk
from tkinter import ttk
from simulation import run_simulation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import datetime
import subprocess

# Store results globally
last_results = None

# -------------------------
# RUN SIMULATION
# -------------------------
def run_sim():

    global last_results

    runs = runs_slider.get()
    failure = fail_slider.get()
    congestion = cong_slider.get()

    last_results = run_simulation(runs, failure, congestion)

    result_text.set(
        f"PDR: {last_results['pdr_aco']:.2f} vs {last_results['pdr_base']:.2f}\n"
        f"Latency: {last_results['lat_aco']:.2f} vs {last_results['lat_base']:.2f}\n"
        f"Redundancy: {last_results['red_aco']:.2f} vs {last_results['red_base']:.2f}"
    )

    update_graph()

# -------------------------
# GRAPH INSIDE UI
# -------------------------
def update_graph():

    if not last_results:
        return

    fig.clear()
    ax = fig.add_subplot(111)

    labels = ['ACO', 'Baseline']
    values = [last_results['pdr_aco'], last_results['pdr_base']]

    ax.bar(labels, values)
    ax.set_title("PDR Comparison")

    canvas.draw()

# -------------------------
# EXPORT CSV
# -------------------------
def export_csv():

    if not last_results:
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

    result_text.set("Saved to results.csv")

# -------------------------
# GENERATE REPORT
# -------------------------
def generate_report():

    if not last_results:
        return

    report = f"""
VEHICLE PLATOONING REPORT

PDR (ACO): {last_results['pdr_aco']:.3f}
PDR (Baseline): {last_results['pdr_base']:.3f}

Latency (ACO): {last_results['lat_aco']:.3f}
Latency (Baseline): {last_results['lat_base']:.3f}

Redundancy (ACO): {last_results['red_aco']:.3f}
Redundancy (Baseline): {last_results['red_base']:.3f}

Conclusion:
ACO improves reliability under dynamic conditions.
"""

    with open("report.txt", "w") as f:
        f.write(report)

    result_text.set("Report generated: report.txt")

# -------------------------
# RUN ANIMATION
# -------------------------
def run_animation():
    subprocess.Popen(["python", "vehicle_animation.py"])

# -------------------------
# UI SETUP
# -------------------------
root = tk.Tk()
root.title("ACO Vehicle Dashboard")
root.geometry("600x500")

tk.Label(root, text="Vehicle Platooning System", font=("Arial", 16)).pack(pady=10)

# -------------------------
# SLIDERS
# -------------------------
frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Simulation Runs").grid(row=0, column=0)
runs_slider = tk.Scale(frame, from_=50, to=500, orient="horizontal")
runs_slider.set(200)
runs_slider.grid(row=0, column=1)

tk.Label(frame, text="Failure Rate").grid(row=1, column=0)
fail_slider = tk.Scale(frame, from_=0.0, to=0.5, resolution=0.05, orient="horizontal")
fail_slider.set(0.2)
fail_slider.grid(row=1, column=1)

tk.Label(frame, text="Congestion").grid(row=2, column=0)
cong_slider = tk.Scale(frame, from_=1.0, to=3.0, resolution=0.1, orient="horizontal")
cong_slider.set(1.5)
cong_slider.grid(row=2, column=1)

# -------------------------
# BUTTONS
# -------------------------
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Run Simulation", command=run_sim, width=20).grid(row=0, column=0, pady=5)
tk.Button(btn_frame, text="Run Animation", command=run_animation, width=20).grid(row=1, column=0, pady=5)
tk.Button(btn_frame, text="Export CSV", command=export_csv, width=20).grid(row=2, column=0, pady=5)
tk.Button(btn_frame, text="Generate Report", command=generate_report, width=20).grid(row=3, column=0, pady=5)

# -------------------------
# RESULT DISPLAY
# -------------------------
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, font=("Arial", 12)).pack(pady=10)

# -------------------------
# EMBED GRAPH
# -------------------------
fig = plt.Figure(figsize=(4,3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# -------------------------
# EXIT
# -------------------------
tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

root.mainloop()