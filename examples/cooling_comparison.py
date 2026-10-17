"""Compare SFQ total wall energy to CMOS and adiabatic."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sfq_sim import (
    sfq_junction_energy, sfq_total_energy, COOLING_RATIOS,
    k_B,
)


# Reference values (from adiabatic-sim, 7nm CMOS)
E_cmos = 2.45e-16           # 245 aJ
E_adiabatic_100ps = 2.45e-18 # 2.45 aJ
E_landauer = k_B * 300 * 0.693  # 2.87 zJ

Ic = 100e-6
E_junction = sfq_junction_energy(Ic)
E_wall = {name: sfq_total_energy(Ic, ratio)["E_wall_J"]
          for name, ratio in COOLING_RATIOS.items()
          if name != "dilution_10mK"}


print("=== SFQ total energy comparison ===\n")
print(f"{'technology':<30s} {'energy (J)':>16s} {'vs CMOS':>12s}")
print("-" * 62)

rows = [
    ("Landauer limit (300 K)", E_landauer),
    ("Adiabatic (100 ps)", E_adiabatic_100ps),
    ("SFQ junction (Ic=100 uA)", E_junction),
]
for name, E in rows:
    print(f"{name:<30s} {E:>16.3e} {E/E_cmos:>11.4f}x")

for name, E in E_wall.items():
    label = f"SFQ wall ({name})"
    print(f"{label:<30s} {E:>16.3e} {E/E_cmos:>11.4f}x")

print(f"{'CMOS (7nm)':<30s} {E_cmos:>16.3e} {1.0:>11.4f}x")


# Plot
fig, ax = plt.subplots(figsize=(10, 5))

techs = ["Landauer\nlimit", "Adiabatic\n(100 ps)",
         "SFQ\njunction", "SFQ wall\n(pulse tube)",
         "SFQ wall\n(GM)", "SFQ wall\n(dilution)", "CMOS\n(7nm)"]
vals = [E_landauer, E_adiabatic_100ps, E_junction,
        E_wall["pulse_tube_4K"], E_wall["gm_cryocooler_4K"],
        E_wall["dilution_4K"], E_cmos]
colors = ["#2ca02c", "#1f77b4", "#9467bd",
          "#ff7f0e", "#ff7f0e", "#ff7f0e", "#d62728"]

bars = ax.bar(techs, vals, color=colors, edgecolor='black', lw=0.5)
ax.set_yscale("log")
ax.set_ylabel("Energy per switch (J)")
ax.set_title("SFQ wall energy is NOT the same as junction energy")
ax.grid(axis='y', which='both', alpha=0.3)

for bar, val in zip(bars, vals):
    y = bar.get_height() * 1.3
    ax.text(bar.get_x() + bar.get_width()/2, y,
            f"{val:.1e}", ha='center', va='bottom', fontsize=8)

plt.xticks(rotation=15)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "cooling_comparison.png")
plt.savefig(out, dpi=140)
print(f"\nwrote {out}")

print("\nKey insight:")
print("  The junction energy (0.2 aJ) is 1000x below CMOS (245 aJ).")
print("  But the 4 K cooler eats ~500-1500x that energy in wall power.")
print("  Total wall energy ends up comparable to or ABOVE CMOS.")
print()
print("  This is why 'SFQ is 1000x more efficient' is misleading —")
print("  the number refers only to the junction, not the system.")
