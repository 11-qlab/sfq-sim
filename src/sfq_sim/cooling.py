"""Cooling penalty for SFQ logic.

SFQ circuits operate at 4 K, requiring a dilution refrigerator
or a pulse-tube cooler.  This analysis computes the total
energy per switch including the cooling overhead.

Reference:
  - Room-temperature wall power / 4 K cooling power ratio for a
    modern cryocooler is roughly 1000:1 (Carnot + practical losses)
  - Dilution refrigerators: ~1500:1
  - Pulse tube coolers:   ~500:1

For comparison against the adiabatic-sim package:
  - SFQ junction energy:   ~0.1 aJ per switch (Ic * Phi_0)
  - CMOS switching:        ~245 aJ per switch
  - Adiabatic (100 ps):    ~2.45 aJ per switch
  - Landauer limit:        ~2.87 zJ per switch
"""
from __future__ import annotations
from .rsj import JosephsonJunction, Phi_0, k_B


# Cooling efficiency (wall power / heat lifted at operating temp)
COOLING_RATIOS = {
    "pulse_tube_4K":     500,     # moderate for 4 K single-stage
    "gm_cryocooler_4K":  800,
    "dilution_4K":       1500,
    "dilution_10mK":    50000,    # for quantum computing, not SFQ
}


def sfq_junction_energy(Ic=100e-6):
    """Energy dissipated at the junction per SFQ switch: Ic * Phi_0."""
    return Ic * Phi_0


def sfq_total_energy(Ic=100e-6, cooling_ratio=500):
    """Total wall energy per switch including cooling.

    The junction dissipates Ic*Phi_0 at 4 K.  The refrigerator
    consumes cooling_ratio times this in wall power.
    """
    E_junction = sfq_junction_energy(Ic)
    E_wall = E_junction * cooling_ratio
    return {
        "E_junction_J": E_junction,
        "E_wall_J": E_wall,
        "cooling_ratio": cooling_ratio,
    }


def compare_to_cmos(Ic=100e-6, cooling_ratio=500,
                    E_cmos=2.45e-16):
    """Compare SFQ total wall energy to a CMOS switch at 245 aJ.

    E_cmos = 2.45e-16 J (from adiabatic-sim, 7nm CMOS).
    """
    result = sfq_total_energy(Ic, cooling_ratio)
    result["E_cmos_J"] = E_cmos
    result["ratio_sfq_over_cmos"] = result["E_wall_J"] / E_cmos
    return result


if __name__ == "__main__":
    print("=== SFQ cooling penalty ===\n")

    Ic = 100e-6
    E_j = sfq_junction_energy(Ic)
    print(f"Junction energy at Ic = {Ic*1e6:.0f} uA: {E_j*1e18:.2f} aJ")
    print()

    print("Cooling ratios (wall power / heat lifted at 4 K):")
    for name, ratio in COOLING_RATIOS.items():
        print(f"  {name:20s}  {ratio:>6d}:1")
    print()

    print("Total wall energy per switch including cooling:")
    print(f"{'cooling':>20s} {'E_junction':>12s} {'E_wall':>12s} "
          f"{'vs CMOS (245 aJ)':>18s}")
    print("-" * 66)
    E_cmos = 2.45e-16
    for name, ratio in COOLING_RATIOS.items():
        if name == "dilution_10mK":
            continue   # not applicable to SFQ
        r = compare_to_cmos(Ic, ratio)
        print(f"{name:>20s} {r['E_junction_J']*1e18:>10.2f} aJ "
              f"{r['E_wall_J']*1e18:>10.2f} aJ "
              f"{r['ratio_sfq_over_cmos']:>18.2f}x")
    print()

    print("Interpretation:")
    print("  The junction itself is ~1000x more efficient than CMOS.")
    print("  But the 4 K refrigerator costs ~500-1500x the heat it lifts.")
    print("  Net: SFQ total wall energy is comparable to or WORSE than CMOS")
    print("  when cooling is included honestly.")

    print()
    print("=== Landauer comparison ===")
    E_land = k_B * 300 * 0.693   # room temperature
    print(f"  Landauer (300 K): {E_land*1e21:.2f} zJ")
    print(f"  SFQ junction:     {E_j*1e18:.2f} aJ = {E_j/E_land:.0f}x Landauer")
    print(f"  SFQ total (wall): {sfq_total_energy(Ic, 500)['E_wall_J']*1e18:.2f} aJ")
