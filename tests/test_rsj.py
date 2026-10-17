"""Tests for SFQ physics."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pytest


def test_jj_parameters():
    """Standard Nb junction should have plasma freq in tens of GHz."""
    from sfq_sim import JosephsonJunction
    jj = JosephsonJunction(Ic=100e-6, R=10.0, C=1e-13)
    assert 10e9 < jj.f_plasma < 500e9   # 10-500 GHz range
    assert 0.1 < jj.beta_c < 10.0       # underdamped-ish


def test_sfq_energy_scaling():
    """E_SFQ = Ic * Phi_0, scales linearly with Ic."""
    from sfq_sim import sfq_pulse_energy, Phi_0
    assert abs(sfq_pulse_energy(100e-6) - 100e-6 * Phi_0) < 1e-30
    assert abs(sfq_pulse_energy(200e-6) - 2 * sfq_pulse_energy(100e-6)) < 1e-30


def test_switching_time_above_Ic():
    """Above Ic, switching time decreases with bias."""
    from sfq_sim import JosephsonJunction
    jj = JosephsonJunction()
    t_1p5 = jj.switching_time(1.5 * jj.Ic)
    t_2p0 = jj.switching_time(2.0 * jj.Ic)
    assert t_2p0 < t_1p5
    assert t_1p5 > 0


def test_switching_time_below_Ic():
    """Below Ic, switching time is infinite (no switching)."""
    from sfq_sim import JosephsonJunction
    jj = JosephsonJunction()
    assert jj.switching_time(0.5 * jj.Ic) == np.inf


def test_rsj_simulation_runs():
    """RSJ integration produces sensible phase evolution."""
    from sfq_sim import JosephsonJunction
    jj = JosephsonJunction()
    t, phi, dphi, V = jj.simulate(Ib=2 * jj.Ic, t_end=20e-12)
    assert len(t) > 100
    assert np.all(np.isfinite(phi))


def test_jtl_propagation():
    """JTL produces phase slips and propagation delay."""
    from sfq_sim import JTL
    jtl = JTL(n_junctions=5)
    r = jtl.propagate_pulse(t_end=20e-12, initial_kick=2.0)
    assert r["t_one_sfq_s"] > 0
    assert r["max_clock_hz"] > 0


def test_cooling_penalty_beats_cmos_only_in_junction():
    """Junction energy is below CMOS; wall energy with cooling is above."""
    from sfq_sim import sfq_junction_energy, sfq_total_energy
    Ic = 100e-6
    E_junc = sfq_junction_energy(Ic)
    E_wall = sfq_total_energy(Ic, cooling_ratio=500)["E_wall_J"]

    E_cmos = 2.45e-16   # from adiabatic-sim 7nm
    # Junction is far below CMOS
    assert E_junc < E_cmos / 100
    # But wall energy (after cooling) is comparable or higher
    assert E_wall > E_junc * 100


def test_cooling_ratio_ordering():
    """Higher cooling ratio -> higher wall energy."""
    from sfq_sim import sfq_total_energy
    e1 = sfq_total_energy(100e-6, cooling_ratio=500)["E_wall_J"]
    e2 = sfq_total_energy(100e-6, cooling_ratio=1500)["E_wall_J"]
    assert e2 > e1


def test_energy_vs_landauer():
    """SFQ junction energy is many orders above the Landauer limit."""
    from sfq_sim import sfq_junction_energy, k_B
    E_land = k_B * 300 * 0.693
    E_sfq = sfq_junction_energy(100e-6)
    assert E_sfq > E_land * 50     # ~72x above Landauer at 100 uA
