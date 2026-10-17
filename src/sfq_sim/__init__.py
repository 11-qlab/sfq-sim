"""SFQ (Single Flux Quantum) logic simulator.

Physics model:
  - Josephson junction (RSJ equations)
  - Josephson transmission line (coupled JJs)
  - Cooling penalty analysis (wall energy vs junction energy)

The honest verdict: SFQ's junction energy is ~1000x below CMOS,
but the 4 K refrigerator costs ~500-1500x the heat it lifts, so
total wall energy is comparable to or worse than CMOS.
"""
from .rsj import (
    JosephsonJunction,
    sfq_pulse_energy,
    sfq_voltage_pulse,
    NB_1KA, NB_10KA, MITLL_SFQ5EE,
    Phi_0, k_B,
)
from .jtl import JTL
from .cooling import (
    sfq_junction_energy,
    sfq_total_energy,
    compare_to_cmos,
    COOLING_RATIOS,
)

__version__ = "0.1.0"
__all__ = [
    "JosephsonJunction",
    "sfq_pulse_energy",
    "sfq_voltage_pulse",
    "NB_1KA", "NB_10KA", "MITLL_SFQ5EE",
    "Phi_0", "k_B",
    "JTL",
    "sfq_junction_energy",
    "sfq_total_energy",
    "compare_to_cmos",
    "COOLING_RATIOS",
]
