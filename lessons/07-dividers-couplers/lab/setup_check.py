"""Pre-class environment verification for lecture 7.

Run:  python setup_check.py     -> must end with "SETUP OK"
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ok = True

# Python 3.12 exactly (numpy 1.26.4 has no wheels for 3.13+)
v = sys.version_info
print(f"python {v.major}.{v.minor}.{v.micro}")
if (v.major, v.minor) != (3, 12):
    print("  WARNING: the course pins numpy 1.26.4, which needs Python 3.12"
          " exactly. Install Python 3.12 and recreate your venv.")
    ok = False

for name, want in [("numpy", "1.26.4"), ("scipy", None),
                   ("matplotlib", None), ("skrf", "1.13.0")]:
    try:
        mod = __import__(name)
        ver = getattr(mod, "__version__", "?")
        tag = "" if want in (None, ver) else f"   (course pin is {want})"
        print(f"ok: {name} {ver}{tag}")
        if want not in (None, ver):
            ok = False
    except Exception as e:                                   # noqa: BLE001
        print(f"FAIL: import {name}: {type(e).__name__}: {e}")
        ok = False

# smoke test: this lecture's machinery — skrf Circuit with a 3-way junction,
# ideal-TEM media lines, and media.resistor: a tiny Wilkinson at 10 GHz
try:
    import numpy as np
    import skrf
    from scipy.constants import c
    from skrf.circuit import Circuit
    from skrf.media import DefinedGammaZ0

    freq = skrf.Frequency(5, 15, 11, "ghz")      # 11 points; f[5] = 10 GHz
    med = DefinedGammaZ0(frequency=freq, z0=50, gamma=1j * freq.w / c)
    d_qw = 0.25 * c / 10.0e9                     # quarter wave at 10 GHz, m
    p1 = Circuit.Port(freq, name="port1", z0=50)
    p2 = Circuit.Port(freq, name="port2", z0=50)
    p3 = Circuit.Port(freq, name="port3", z0=50)
    la = med.line(d_qw, unit="m", z0=50 * np.sqrt(2), name="arm_a")
    lb = med.line(d_qw, unit="m", z0=50 * np.sqrt(2), name="arm_b")
    rr = med.resistor(100.0, name="r_iso")
    wilk = Circuit([[(p1, 0), (la, 0), (lb, 0)],
                    [(p2, 0), (la, 1), (rr, 0)],
                    [(p3, 0), (lb, 1), (rr, 1)]]).network
    assert wilk.nports == 3
    assert abs(wilk.s[5, 1, 0] - (-1j / np.sqrt(2))) < 1e-12   # -3.01 dB, -90 deg
    assert abs(wilk.s[5, 0, 0]) < 1e-12                        # matched input
    assert abs(wilk.s[5, 2, 1]) < 1e-12                        # isolated outputs
    print("ok: skrf Circuit smoke test (a Wilkinson in nine lines)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
