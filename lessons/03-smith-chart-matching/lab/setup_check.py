"""Pre-class environment verification for lecture 3.

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
                   ("matplotlib", None), ("pandas", None),
                   ("skrf", "1.13.0")]:
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

# optional extra for this lecture (standalone Smith-chart axes); never required
try:
    import pysmithchart
    print(f"ok: pysmithchart {pysmithchart.__version__} (optional)")
except Exception:                                            # noqa: BLE001
    print("note: pysmithchart not installed (optional — skrf draws our charts)")

# smoke test for this lecture: an ideal 50-ohm line medium, a mismatched load,
# a lam/8 line cascade, and the Smith-chart drawing routine
try:
    import numpy as np
    import skrf
    from skrf.media import DefinedGammaZ0
    from skrf.plotting import smith                          # noqa: F401
    from scipy.constants import c

    frq = skrf.Frequency(2.0, 2.8, 11, "ghz")
    med = DefinedGammaZ0(frequency=frq, z0=50, gamma=1j * frq.w / c)
    load = med.load(np.tile((36 - 21j - 50) / (36 - 21j + 50), (11, 1, 1)))
    ntwk = med.line(c / 2.4e9 / 8, unit="m") ** load         # lam/8 at 2.4 GHz
    assert ntwk.nports == 1
    # a line cannot change |Gamma| (lossless): the chart's central promise
    assert np.allclose(np.abs(ntwk.s[:, 0, 0]), 0.285098, atol=1e-6)
    print("ok: skrf DefinedGammaZ0 line cascade smoke test (|Gamma| rotates,"
          " never grows)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
