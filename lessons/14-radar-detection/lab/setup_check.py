"""Pre-class environment verification for lecture 14.

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

# smoke test: 1e5 Rayleigh draws must reproduce exp(-T^2) at pfa = 1e-2,
# and scipy's noncentral chi-square must agree with the Rayleigh limit.
try:
    import numpy as np
    from scipy.stats import ncx2

    rng = np.random.default_rng(14)
    r = np.hypot(rng.standard_normal(100_000),
                 rng.standard_normal(100_000)) * np.sqrt(0.5)
    t = np.sqrt(np.log(1e2))                    # exact Rayleigh inverse
    meas = np.mean(r > t)
    assert abs(meas - 1e-2) < 3 * np.sqrt(1e-2 * 0.99 / 100_000)
    # Marcum Q with zero signal collapses to the Rayleigh false-alarm rate
    assert abs(ncx2.sf(2 * np.log(1e2), df=2, nc=1e-12) - 1e-2) < 1e-9
    print(f"ok: detection smoke test (measured pfa {meas:.2e} at design"
          " 1e-2; Marcum(0) = Rayleigh)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
