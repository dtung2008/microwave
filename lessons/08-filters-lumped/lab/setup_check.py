"""Pre-class environment verification for lecture 8.

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

# smoke test: scipy's prototype referee + an ABCD identity this lab leans on
try:
    import numpy as np
    from scipy.signal import buttap, cheb1ap

    _, p, k = cheb1ap(3, 0.5)
    assert len(p) == 3 and k > 0
    _, p, k = buttap(4)
    assert len(p) == 4
    # series z then shunt y cascade, checked against the closed form at one f
    z, y = 1j * 2.0, 1j * 0.25
    m = np.array([[1, z], [0, 1]]) @ np.array([[1, 0], [y, 1]])
    assert abs(m[0, 0] - (1 + z * y)) < 1e-15 and abs(m[0, 1] - z) < 1e-15
    import skrf
    from skrf.media import DefinedGammaZ0

    med = DefinedGammaZ0(frequency=skrf.Frequency(50, 70, 3, "mhz"), z0=50)
    two = med.inductor(1e-6) ** med.capacitor(7e-12)
    assert two.nports == 2
    print("ok: scipy prototypes + ABCD + skrf lumped-element smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
