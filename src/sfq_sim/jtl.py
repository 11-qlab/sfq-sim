"""Josephson Transmission Line (JTL).

A JTL is a chain of Josephson junctions coupled by inductors.
SFQ pulses propagate ballistically along the chain, each
junction firing in sequence as the pulse passes.

The pulse velocity and the maximum clock rate are set by
the plasma frequency and the inductive coupling.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from .rsj import JosephsonJunction, Phi_0, hbar, e_charge


class JTL:
    """Chain of N coupled Josephson junctions."""

    def __init__(self, n_junctions=5, Ic=100e-6, R=10.0, C=1e-13,
                 L_coupling=2e-12):
        self.N = n_junctions
        self.jj = JosephsonJunction(Ic=Ic, R=R, C=C)
        self.L_c = L_coupling   # H, coupling inductance

        # Effective plasma frequency of the JTL (reduced from single JJ)
        self.omega_jtl = self.jj.omega_p / np.sqrt(
            1 + Phi_0 / (2 * np.pi * Ic * L_coupling)
        )

    def __repr__(self):
        return (f"JTL(N={self.N}, Ic={self.jj.Ic*1e6:.0f}uA, "
                f"L={self.L_c*1e12:.1f}pH, "
                f"f_jtl={self.omega_jtl/(2*np.pi)/1e9:.1f}GHz)")

    def propagate_pulse(self, t_end, initial_kick=2.0, n_points=3000):
        """Inject a single SFQ pulse at one end and watch it propagate.

        Simplified model: each junction is independently biased
        just below Ic; the incoming pulse pushes it over threshold.
        We track the phase of junction 0 triggered by initial_kick.
        """
        # This is a simplified single-junction tracking of pulse
        # propagation timing.  Each junction fires once the
        # preceding one has moved its phase by ~2*pi.
        t, phi, dphi, V = self.jj.simulate(
            Ib=self.jj.Ic * initial_kick,
            t_end=t_end,
            n_points=n_points,
        )
        # Detect phase slips
        phase_slips = np.floor(phi / (2 * np.pi))
        n_slips = int(phase_slips[-1] - phase_slips[0])

        # Timing: the width of one SFQ is ~ plasma period
        t_sfq = self.jj.plasma_time()

        # Pulse propagation velocity: one junction per SFQ period
        v_jtl = 1.0 / t_sfq   # junctions per second

        # Delay through the full JTL
        t_propagation = self.N * t_sfq

        return {
            "time": t,
            "phase": phi,
            "voltage": V,
            "n_phase_slips": n_slips,
            "t_one_sfq_s": t_sfq,
            "v_jtl_junctions_per_s": v_jtl,
            "t_propagation_s": t_propagation,
            "max_clock_hz": 1.0 / (2 * t_propagation),
        }


if __name__ == "__main__":
    print("=== Josephson Transmission Line ===\n")

    for n in (3, 5, 10, 20):
        jtl = JTL(n_junctions=n)
        result = jtl.propagate_pulse(t_end=20e-12, initial_kick=2.0)
        print(f"{jtl}")
        print(f"  Phase slips: {result['n_phase_slips']}")
        print(f"  Time per SFQ: {result['t_one_sfq_s']*1e12:.1f} ps")
        print(f"  Propagation (N={n}): {result['t_propagation_s']*1e12:.1f} ps")
        print(f"  Max clock: {result['max_clock_hz']/1e9:.1f} GHz")
        print()
