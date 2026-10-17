"""Command-line interface for sfq-sim."""
import argparse
import json
import sys
from .rsj import (
    JosephsonJunction, sfq_pulse_energy,
    NB_1KA, NB_10KA, MITLL_SFQ5EE,
)
from .jtl import JTL
from .cooling import (
    sfq_junction_energy, sfq_total_energy, compare_to_cmos,
    COOLING_RATIOS,
)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="sfq-sim",
        description="SFQ Josephson junction and cooling simulator",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- jj subcommand ---
    pj = sub.add_parser("jj", help="Josephson junction properties")
    pj.add_argument("--Ic", type=float, default=100e-6,
                    help="Critical current (A)")
    pj.add_argument("--R", type=float, default=10.0,
                    help="Normal resistance (Ohm)")
    pj.add_argument("--C", type=float, default=1e-13,
                    help="Junction capacitance (F)")
    pj.add_argument("--json", action="store_true")

    # --- jtl subcommand ---
    pt = sub.add_parser("jtl", help="JTL propagation")
    pt.add_argument("--n", type=int, default=5,
                    help="Number of junctions")
    pt.add_argument("--t_end", type=float, default=20e-12,
                    help="Simulation time (s)")

    # --- cooling subcommand ---
    pc = sub.add_parser("cooling", help="Cooling penalty analysis")
    pc.add_argument("--Ic", type=float, default=100e-6,
                    help="Critical current (A)")
    pc.add_argument("--E_cmos", type=float, default=2.45e-16,
                    help="CMOS energy per switch (J)")
    pc.add_argument("--json", action="store_true")

    args = p.parse_args(argv)

    if args.cmd == "jj":
        jj = JosephsonJunction(Ic=args.Ic, R=args.R, C=args.C)
        info = {
            "Ic_A": jj.Ic,
            "R_Ohm": jj.R,
            "C_F": jj.C,
            "beta_c": jj.beta_c,
            "plasma_frequency_Hz": jj.f_plasma,
            "switching_time_at_2Ic_s": jj.switching_time(2 * jj.Ic),
            "E_SFQ_J": jj.E_SFQ,
        }
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Josephson junction:")
            print(f"  Ic       = {jj.Ic*1e6:.0f} uA")
            print(f"  R        = {jj.R:.1f} Ohm")
            print(f"  C        = {jj.C*1e15:.1f} fF")
            print(f"  beta_c   = {jj.beta_c:.3f}")
            print(f"  f_p      = {jj.f_plasma/1e9:.1f} GHz")
            print(f"  t_sw     = {jj.switching_time(2*jj.Ic)*1e12:.1f} ps (Ib=2Ic)")
            print(f"  E_SFQ    = {jj.E_SFQ*1e18:.3f} aJ")
        return 0

    if args.cmd == "jtl":
        jtl = JTL(n_junctions=args.n)
        r = jtl.propagate_pulse(t_end=args.t_end, initial_kick=2.0)
        print(f"{jtl}")
        print(f"  Phase slips   : {r['n_phase_slips']}")
        print(f"  Time per SFQ  : {r['t_one_sfq_s']*1e12:.1f} ps")
        print(f"  Propagation   : {r['t_propagation_s']*1e12:.1f} ps")
        print(f"  Max clock     : {r['max_clock_hz']/1e9:.1f} GHz")
        return 0

    if args.cmd == "cooling":
        print(f"Ic = {args.Ic*1e6:.0f} uA, "
              f"E_junction = {sfq_junction_energy(args.Ic)*1e18:.2f} aJ\n")
        print(f"{'cooling':>20s} {'E_wall':>12s} {'vs CMOS':>12s}")
        print("-" * 50)
        for name, ratio in COOLING_RATIOS.items():
            if name == "dilution_10mK":
                continue
            r = compare_to_cmos(args.Ic, ratio, args.E_cmos)
            print(f"{name:>20s} {r['E_wall_J']*1e18:>10.2f} aJ "
                  f"{r['ratio_sfq_over_cmos']:>11.2f}x")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
