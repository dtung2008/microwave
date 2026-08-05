"""Pre-class environment verification for lecture 5.

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

# optional: fdtd powers hour 3's below-cutoff demo; the lab runs without it
try:
    import fdtd
    print(f"ok: fdtd {fdtd.__version__} (optional field demo available)")
except Exception:                                            # noqa: BLE001
    print("note: fdtd not installed — optional; hour 3's cell 3.5 will skip."
          " To see the demo: pip install fdtd")

# smoke test: this lecture's referee calls — MLine and RectangularWaveguide
try:
    import numpy as np
    import skrf
    from skrf.media import MLine, RectangularWaveguide
    from scipy.constants import c

    freq = skrf.Frequency(8, 12, 5, "ghz")
    ml = MLine(frequency=freq, w=1.1e-3, h=0.508e-3, t=35e-6, ep_r=3.48,
               tand=0.0037, rho=1.68e-8, model="hammerstadjensen",
               disp="kirschningjansen", f_epr_tand=10e9)
    z0 = float(ml.z0_characteristic.real[2])
    assert 45.0 < z0 < 55.0, f"MLine z0 = {z0}"
    wg = RectangularWaveguide(frequency=freq, a=22.86e-3, b=10.16e-3)
    assert abs(wg.f_cutoff - c / (2 * 22.86e-3)) < 1.0, "WR-90 cutoff"
    print("ok: skrf MLine + RectangularWaveguide smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
