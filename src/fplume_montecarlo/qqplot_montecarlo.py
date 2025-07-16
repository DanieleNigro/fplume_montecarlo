import os
import numpy as np
import matplotlib.pyplot as plt
from fplume_montecarlo.config import ERUPTIONS_FILE, COLUMN_FILES_DIR, PLOTS_DIR
from fplume_montecarlo.utilities import load_events


# --- Load event metadata
events = load_events(ERUPTIONS_FILE, code=None)
event_map = {
    f"{int(e['year'])}_{int(e['month']):02}_{int(e['day']):02}_{int(e['hour']):02}": e
    for e in events
}

# --- Read and combine data
combined_data = []


for filename in sorted(os.listdir(COLUMN_FILES_DIR)):
    if filename.endswith(".column"):
        try:
            date_str = filename.split(".")[0]
            event = event_map.get(date_str)
            if not event:
                continue

            file_path = os.path.join(COLUMN_FILES_DIR, filename)
            with open(file_path, "r") as file:
                values = [float(val) for line in file for val in line.strip().split()]
                values = np.array(values) + 3350  # Add Etna height

            radar_value = event.get("h")
            mer_value = event.get("mer")
            if radar_value is None or mer_value is None:
                continue

            combined_data.append({
                "mer": mer_value,
                "values": values,
                "radar_value": radar_value,
            })

        except Exception:
            continue

# --- Compute ECDF percentiles with radar uncertainty (±300 m)
for entry in combined_data:
    values = np.sort(entry['values'])
    n = len(values)
    radar = entry['radar_value']

    low = np.searchsorted(values, radar - 300, side='right') / n
    mid = np.searchsorted(values, radar, side='right') / n
    high = np.searchsorted(values, radar + 300, side='right') / n

    entry.update({
        "ecdf_low": low,
        "ecdf_mid": mid,
        "ecdf_high": high,
    })

# --- Split data by MER threshold
threshold = 1e6
low_mer_group = [e for e in combined_data if e["mer"] < threshold]
high_mer_group = [e for e in combined_data if e["mer"] >= threshold]

# --- Function to prepare QQ plot data
def prepare_qq_data(group):
    percentiles = np.array([e["ecdf_mid"] for e in group])
    low_bounds = np.array([e["ecdf_low"] for e in group])
    high_bounds = np.array([e["ecdf_high"] for e in group])
    sorted_idx = np.argsort(percentiles)

    sorted_percentiles = percentiles[sorted_idx]
    sorted_lows = low_bounds[sorted_idx]
    sorted_highs = high_bounds[sorted_idx]

    theoretical_quantiles = np.linspace(0, 1, len(sorted_percentiles), endpoint=False) + 0.5 / len(sorted_percentiles)

    return theoretical_quantiles, sorted_percentiles, sorted_lows, sorted_highs

# --- Plot QQ plots for both groups
fig, axs = plt.subplots(1, 2, figsize=(12, 6), sharey=True)

# Plot for low MER
q_theo_low, p_mid_low, p_lo_low, p_hi_low = prepare_qq_data(low_mer_group)
axs[0].errorbar(q_theo_low, p_mid_low, yerr=[p_mid_low - p_lo_low, p_hi_low - p_mid_low],
                fmt='o', capsize=4, color='blue', markersize=4, label="Low MER")
axs[0].plot([0, 1], [0, 1], 'r--', label="1:1 line")
axs[0].set_title("QQ Plot - MER < 8e5", fontsize=13)
axs[0].set_xlabel("Theoretical Quantiles", fontsize=12)
axs[0].set_ylabel("Observed ECDF Percentiles", fontsize=12)
axs[0].grid(True)
axs[0].legend()

# Plot for high MER
q_theo_high, p_mid_high, p_lo_high, p_hi_high = prepare_qq_data(high_mer_group)
axs[1].errorbar(q_theo_high, p_mid_high, yerr=[p_mid_high - p_lo_high, p_hi_high - p_mid_high],
                fmt='o', capsize=4, color='green', markersize=4, label="High MER")
axs[1].plot([0, 1], [0, 1], 'r--', label="1:1 line")
axs[1].set_title("QQ Plot - MER ≥ 8e5", fontsize=13)
axs[1].set_xlabel("Theoretical Quantiles", fontsize=12)
axs[1].grid(True)
axs[1].legend()

plt.suptitle("QQ Plots of ECDF Percentiles with Radar Uncertainty", fontsize=15)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(PLOTS_DIR / "qq_plot_split_by_mer.png", dpi=300)

# --- ECDF Percentile vs MER Plot (with uncertainty as vertical error bars)
mers = [entry["mer"] for entry in combined_data]
ecdf_mids = [entry["ecdf_mid"] for entry in combined_data]
ecdf_lows = [entry["ecdf_low"] for entry in combined_data]
ecdf_highs = [entry["ecdf_high"] for entry in combined_data]

ecdf_errors = np.array([
    [mid - low, high - mid]
    for mid, low, high in zip(ecdf_mids, ecdf_lows, ecdf_highs)
]).T  # shape (2, N)

plt.figure(figsize=(8, 5))
plt.axhline(0.5, color='grey', linestyle='--', label="Median (50th percentile)", zorder=1)
plt.errorbar(
    mers, ecdf_mids, yerr=ecdf_errors,
    fmt='o', color='blue', alpha=0.7, capsize=4, markersize=4, zorder=2
)
plt.xlim([1e4, 1e7])
plt.xscale('log')
plt.xlabel("MER (kg/s) [log scale]", fontsize=12)
plt.ylabel("ECDF Percentile of Radar Observation", fontsize=12)
plt.title("Radar Height Percentile vs MER (with Uncertainty)", fontsize=14)
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "percentile_vs_mer_with_uncertainty.png", dpi=300)
