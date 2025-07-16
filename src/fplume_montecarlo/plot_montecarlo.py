"""
Generates a summary plot for all .column files in COLUMN_FILES_DIR, sorted by MER.

The plot consists of two subplots:
    - Top: A boxplot showing the distribution of column heights from Monte Carlo simulations,
      with radar-observed column heights overlaid as scatter points.
    - Bottom: A bar chart showing MER values with a secondary axis plotting the ECDF percentile
      of the radar observation within the Monte Carlo distribution.
"""
# --- Import packages
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from fplume_montecarlo.config import PROJ_ROOT, ERUPTIONS_FILE, COLUMN_FILES_DIR, PLOTS_DIR
from fplume_montecarlo.utilities import load_events, load_config

CONFIG = load_config(PROJ_ROOT / "config.yaml")

# ---Load volcano features
VOLCANO = CONFIG["volcano"]  # This is now a Volcano object

# ---Load event metadata
events = load_events(ERUPTIONS_FILE, code=None)
event_map = {
    f"{int(e['year'])}_{int(e['month']):02}_{int(e['day']):02}_{int(e['hour']):02}": e
    for e in events
}

# ---Read and Combine Simulation Data
combined_data = []

for filename in sorted(os.listdir(COLUMN_FILES_DIR)):
    # ---Select all .comunn files
    if filename.endswith(".column"):
        try:
            date_str = filename.split(".")[0]
            event = event_map.get(date_str)
            if not event:
                print(f"Skipped {filename}: No matching event")
                continue

            file_path = os.path.join(COLUMN_FILES_DIR, filename)
            with open(file_path, "r") as file:
                # ---Retrieve column heights from .column files
                values = [float(val) for line in file for val in line.strip().split()]
                values = np.array(values) + VOLCANO.height                              # Add height of the volcano

            # ---Retrieve radar-based MER and column height from event metadata
            radar_value = event.get("h")
            mer_value = event.get("mer")
            if radar_value is None or mer_value is None:
                print(f"Skipped {filename}: Missing radar or MER data")
                continue
            
            # ---Combine weather radar data and Montecarlo simulation data
            combined_data.append({
                "date": datetime.strptime(date_str, "%Y_%m_%d_%H"),
                "values": values,
                "radar_value": radar_value,
                "mer": mer_value,
            })

        except Exception as e:
            print(f"Skipped {filename}: {e}")

# ---Sort by MER
combined_data.sort(key=lambda x: x["mer"])

# ---Prepare for Plotting
boxplot_data = []
boxplot_labels = []
positions = []
scatter_x = []
scatter_y = []

for idx, entry in enumerate(combined_data):
    boxplot_data.append(entry["values"])
    boxplot_labels.append(entry["date"].strftime("%Y-%m-%d-%H"))
    positions.append(idx + 1)
    scatter_x.append(idx + 1)
    scatter_y.append(entry["radar_value"])

# ---Compute Custom Box Stats
def custom_boxplot_stats(values):
    q1 = np.percentile(values, 1)
    q25 = np.percentile(values, 25)
    q50 = np.percentile(values, 50)
    q75 = np.percentile(values, 75)
    q99 = np.percentile(values, 99)
    return {
        "whislo": q1,
        "q1": q25,
        "med": q50,
        "q3": q75,
        "whishi": q99
    }

custom_stats = []
for values in boxplot_data:
    stats = custom_boxplot_stats(values)
    custom_stats.append([
        stats['whislo'], stats['q1'], stats['med'], stats['q3'], stats['whishi']
    ])

# ---Compute ECDF Percentiles including uncertainty
ecdf_percentiles = []
for entry in combined_data:
    values = entry['values']
    radar_value = entry['radar_value']
    sorted_vals = np.sort(values)
    n = len(sorted_vals)

    low = np.searchsorted(sorted_vals, radar_value - 300, side='right') / n
    mid = np.searchsorted(sorted_vals, radar_value, side='right') / n
    high = np.searchsorted(sorted_vals, radar_value + 300, side='right') / n

    ecdf_percentiles.append({
        'date': entry['date'],
        'radar_value': radar_value,
        'percentile': mid,
        'low': low,
        'high': high
    })

# ---Print ECDF Percentile Table
print(f"{'Date':<20} {'Radar Value':>12} {'ECDF Percentile':>18} {'Range':>18}")
for e in ecdf_percentiles:
    print(f"{e['date'].strftime('%Y-%m-%d %H:%M'): <20} {e['radar_value']:>12.1f} "
          f"{e['percentile']*100:>17.1f}%  [{e['low']*100:.1f}% – {e['high']*100:.1f}%]")

# --- Plot
fig, (ax1, ax2, ax3) = plt.subplots(
    3, 1, figsize=(12, 16), sharex=True,
    gridspec_kw={'height_ratios': [1.2, 0.8, 0.8]}
)

# --- Top Plot: Boxplot with radar measurements
ax1.bxp([{
    'med': s[2],
    'q1': s[1],
    'q3': s[3],
    'whislo': s[0],
    'whishi': s[4],
    'fliers': []
} for s in custom_stats],
    positions=positions,
    showfliers=False,
    patch_artist=False,
    boxprops=dict(color='black'),
    medianprops=dict(color='darkblue'),
    whiskerprops=dict(color='black'),
    capprops=dict(color='black')
)

ax1.errorbar(
    scatter_x, scatter_y, yerr=300,
    fmt='o', color='red', label='H radar',
    capsize=4, zorder=3, markersize=3
)
ax1.set_ylabel("Height (m)", fontsize=14)
ax1.grid(True)
ax1.set_ylim([4000, 16001])
ax1.legend(fontsize=12)
ax1.tick_params(axis='x', which='both', labelbottom=False)

# --- Middle Plot: ECDF Percentiles (with radar uncertainty)
percentiles = [e['percentile'] * 100 for e in ecdf_percentiles]     # convert to %
percentile_errors = [
    [(e['percentile'] - e['low']) * 100, (e['high'] - e['percentile']) * 100]
    for e in ecdf_percentiles
]
percentile_errors = np.array(percentile_errors).T  # shape: (2, N)

ax2.errorbar(
    positions, percentiles,
    yerr=percentile_errors,
    fmt='o', color='red', label='ECDF Percentile',
    capsize=4, markersize=3
)
ax2.set_ylabel("ECDF Percentile (%)", fontsize=14, color='red')
ax2.set_ylim([0, 100.1])
ax2.tick_params(axis='y', labelcolor='red', labelsize=12)
ax2.grid(True, linestyle='--', linewidth=0.5)
ax2.legend(fontsize=12)
ax2.tick_params(axis='x', which='both', labelbottom=False)

# --- Bottom Plot: MER (log scale)
mer_values = [entry['mer'] for entry in combined_data]
ax3.bar(positions, mer_values, color='skyblue', label='MER [kg/s]')
ax3.set_yscale('log')
ax3.set_ylabel("MER [kg/s]", fontsize=14, color='blue')
ax3.set_ylim([1e4, 1e7])
ax3.tick_params(axis='y', labelcolor='blue', labelsize=12)
ax3.set_xticks(positions)
ax3.set_xticklabels(boxplot_labels, rotation=90, fontsize=10)
ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
ax3.legend(fontsize=12)

# --- Save plot
fig.tight_layout()
plt.savefig(PLOTS_DIR / "box_plot_Montecarlo_FPLUME.png", dpi=300, bbox_inches='tight')
