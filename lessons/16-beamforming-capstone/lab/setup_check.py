"""Pre-class environment verification for lecture 16 (the capstone).

Run:  python setup_check.py     -> must end with "SETUP OK"

Lecture 16 adds ONE package to the course stack: pyargus (the independent
DOA referee). If it is missing: pip install pyargus
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ok = True

v = sys.version_info
print(f"python {v.major}.{v.minor}.{v.micro}")
if (v.major, v.minor) != (3, 12):
    print("  WARNING: the course pins numpy 1.26.4, which needs Python 3.12"
          " exactly. Install Python 3.12 and recreate your venv.")
    ok = False

for name, want in [("numpy", "1.26.4"), ("scipy", None),
                   ("matplotlib", None), ("skrf", "1.13.0"),
                   ("pyargus", None)]:
    try:
        mod = __import__(name)
        ver = getattr(mod, "__version__", "(no __version__)")
        tag = "" if want in (None, ver) else f"   (course pin is {want})"
        print(f"ok: {name} {ver}{tag}")
        if want not in (None, ver):
            ok = False
    except Exception as e:                                   # noqa: BLE001
        print(f"FAIL: import {name}: {type(e).__name__}: {e}")
        if name == "pyargus":
            print("      lecture 16 needs it: pip install pyargus")
        ok = False

# smoke test: a 4-element snapshot, our beamscan convention vs pyargus
try:
    import numpy as np
    from pyargus import directionEstimation as de

    n, th = 4, 20.0
    a = np.exp(1j * np.pi * np.arange(n) * np.sin(np.radians(th)))
    x = np.outer(a, np.ones(16)) + 0.0j          # noise-free snapshots
    r = de.corr_matrix_estimate(x.T, imp="fast")
    grid = np.arange(-90.0, 90.1, 0.5)
    sv = de.gen_ula_scanning_vectors(np.arange(n) * 0.5, 90.0 - grid)
    pad = np.abs(de.DOA_Bartlett(r, sv))
    assert abs(grid[int(np.argmax(pad))] - th) < 0.5 + 1e-9
    print("ok: pyargus DOA_Bartlett smoke test (peak at +20 deg)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
