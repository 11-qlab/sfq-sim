# sfq-sim

Superconducting Single Flux Quantum (SFQ) logic simulator.

## The honest verdict

The claim "SFQ is 1000x more efficient than CMOS" refers only to
junction energy. The full picture:

| Technology | Energy per switch |
|---|---|
| Landauer limit (300 K) | 2.87 zJ |
| Adiabatic CMOS (100 ps) | 2.45 aJ |
| SFQ junction (Ic=100 uA) | 0.21 aJ |
| SFQ wall (pulse tube, 500x) | 103 aJ |
| SFQ wall (dilution, 1500x) | 310 aJ |
| CMOS (7 nm) | 245 aJ |

The junction itself is ~1000x below CMOS. But the 4 K refrigerator
consumes 500-1500x the heat it lifts. Total wall energy ends up
comparable to or worse than CMOS.

## Install

    pip install -e .

## CLI

    sfq-sim jj          # Josephson junction properties
    sfq-sim jtl --n 5   # JTL propagation
    sfq-sim cooling     # Cooling penalty analysis

## Physics

- RSJ model: resistively-shunted junction, RK45 integration
- JTL: Josephson transmission line (coupled JJs)
- Cooling: honest wall-power accounting

## Tests

    pytest tests/ -v

## License

Apache 2.0
