"""Resistively Shunted Junction (RSJ) model.

The canonical model for a Josephson junction (JJ):

    I = Ic sin(phi) + V/R + C dV/dt          (current conservation)
    dphi/dt = 2e V / hbar                    (Josephson relation)

Combined into a single 2nd-order ODE in phi:

    (hbar C / 2e) d^2 phi/dt^2
    + (hbar / 2eR) d phi/dt
    + Ic sin(phi)
    = Ib

Two dimensionless parameters control the dynamics:

    Stewart-McCumber: beta_c = 2*pi*Ic*R^2*C / Phi_0
    Plasma frequency: omega_p = sqrt(2*pi*Ic / (Phi_0 * C))

beta_c >> 1 : underdamped (hysteretic, used in RSFQ)
beta_c ~ 1  : critically damped
beta_c << 1 : overdamped (used in SFQ with external shunt)

Physical constants:
    Phi_0 = h/(2e) = 2.0678e-15 Wb  (flux quantum)
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp


# Physical constants
Phi_0 = 2.067833848e-15   # Wb
hbar = 1.054571817e-34    # J*s
e_charge = 1.602176634e-19
k_B = 1.380649e-23


# ============================================================
# Junctions
# ============================================================
class JosephsonJunction:
    """A single Josephson junction with RSJ dynamics.

    Defaults are typical Nb/AlO_x/Nb junction parameters
    (Nb = niobium, AlO_x = aluminum oxide barrier).

    Ic  = critical current
    R   = normal-state resistance
    C   = junction capacitance
    """

    def __init__(self, Ic=100e-6, R=10.0, C=1e-13):
        self.Ic = Ic    # A
        self.R = R      # Ohm
        self.C = C      # F

        # Derived
        self.beta_c = 2 * np.pi * Ic * R**2 * C / Phi_0
        self.omega_p = np.sqrt(2 * np.pi * Ic / (Phi_0 * C))
        self.f_plasma = self.omega_p / (2 * np.pi)
        self.E_SFQ = Ic * Phi_0   # energy per SFQ pulse (J)

    def __repr__(self):
        return (f"JJ(Ic={self.Ic*1e6:.0f}uA, R={self.R:.1f}Ohm, "
                f"C={self.C*1e15:.0f}fF, "
                f"beta_c={self.beta_c:.2f}, "
                f"f_p={self.f_plasma*1e9:.1f}GHz, "
                f"E={self.E_SFQ*1e19:.3f}aJ)")

    def rsj_rhs(self, t, y, Ib):
        """Right-hand side of the RSJ 2nd-order ODE.

        y = [phi, dphi/dt]
        """
        phi, dphi = y
        Ic, R, C = self.Ic, self.R, self.C

        # d^2 phi / dt^2 = (2e/(hbar C)) * (Ib - Ic sin(phi) - (hbar/(2eR)) dphi/dt)
        d2phi = (2 * e_charge / (hbar * C)) * (
            Ib - Ic * np.sin(phi) - (hbar / (2 * e_charge * R)) * dphi
        )
        return [dphi, d2phi]

    def simulate(self, Ib, t_end, phi_0=0.0, dphi_0=0.0, n_points=2000):
        """Integrate the RSJ equations for a constant bias Ib.

        Returns (t, phi, dphi_dt, V) where V = (hbar/(2e)) dphi/dt.
        """
        t_eval = np.linspace(0, t_end, n_points)
        sol = solve_ivp(
            lambda t, y: self.rsj_rhs(t, y, Ib),
            [0, t_end],
            [phi_0, dphi_0],
            t_eval=t_eval,
            method="RK45",
            rtol=1e-8,
            atol=1e-10,
        )
        phi = sol.y[0]
        dphi = sol.y[1]
        V = (hbar / (2 * e_charge)) * dphi
        return sol.t, phi, dphi, V

    def switching_time(self, Ib, phi_0=0.0):
        """Estimate time for phase to advance by 2*pi (one SFQ) at bias Ib.

        Rough formula: t_sw ~ 2*pi / (omega_p * sqrt((Ib/Ic)^2 - 1))
        valid for Ib > Ic.
        """
        if Ib <= self.Ic:
            return np.inf
        return 2 * np.pi / (self.omega_p * np.sqrt((Ib / self.Ic) ** 2 - 1))

    def plasma_time(self):
        """1/omega_p in seconds."""
        return 1.0 / self.omega_p


# ============================================================
# SFQ pulse properties
# ============================================================
def sfq_pulse_energy(Ic):
    """Energy per SFQ pulse: Ic * Phi_0."""
    return Ic * Phi_0


def sfq_pulse_area(V, t):
    """Integral of voltage over time -- should equal Phi_0 for one SFQ."""
    return np.trapezoid(V, t)


def sfq_voltage_pulse(t, t_peak, V_peak, width):
    """Approximate SFQ voltage pulse shape: a Gaussian.

    In reality SFQ pulses are asymmetric solitons, but the
    Gaussian is adequate for energy and area accounting.
    """
    return V_peak * np.exp(-((t - t_peak) / width) ** 2)


# ============================================================
# Typical parameters from literature
# ============================================================
# HYPRES / SeeQC Nb 1 kA/cm^2 process
NB_1KA = JosephsonJunction(Ic=100e-6, R=10.0, C=1e-13)

# ISTEC / AIST Nb 10 kA/cm^2 (higher Jc, smaller junctions)
NB_10KA = JosephsonJunction(Ic=250e-6, R=4.0, C=4e-14)

# MIT Lincoln Lab SFQ5ee (used in the 2019 1.7 GHz 8-bit ALU)
MITLL_SFQ5EE = JosephsonJunction(Ic=100e-6, R=8.0, C=1.5e-13)


if __name__ == "__main__":
    print("=== SFQ Josephson junction models ===\n")

    for name, jj in [("Nb 1kA (HYPRES)", NB_1KA),
                     ("Nb 10kA (ISTEC)", NB_10KA),
                     ("MIT-LL SFQ5ee", MITLL_SFQ5EE)]:
        print(f"{name}:")
        print(f"  {jj}")
        print(f"  Switching time (Ib=2Ic): {jj.switching_time(2*jj.Ic)*1e12:.1f} ps")
        print(f"  Plasma period: {jj.plasma_time()*1e12:.1f} ps")
        print(f"  Max clock (2/plasma period): {1/(2*jj.plasma_time())/1e9:.1f} GHz")
        print()

    print("=== SFQ pulse energy ===")
    for Ic in (50e-6, 100e-6, 250e-6):
        E = sfq_pulse_energy(Ic)
        print(f"  Ic = {Ic*1e6:.0f} uA -> E = {E*1e18:.2f} aJ")
