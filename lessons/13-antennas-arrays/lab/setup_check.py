"""Pre-class environment verification for lecture 13.

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

# smoke test: an 8-element array factor two ways — direct phasor sum vs the
# geometric-series closed form — plus the Chebyshev window this week leans on
try:
    import warnings

    import numpy as np

    warnings.filterwarnings("ignore", message="This window is not suitable")
    from scipy.signal.windows import chebwin

    psi = 0.7                                  # any inter-element phase
    af_sum = abs(np.exp(1j * np.arange(8) * psi).sum())
    af_closed = abs(np.sin(8 * psi / 2) / np.sin(psi / 2))
    assert abs(af_sum - af_closed) < 1e-9
    w = chebwin(16, at=30.0)
    assert w.size == 16 and abs(w.max() - 1.0) < 1e-12
    print("ok: array-factor smoke test (phasor sum = geometric series;"
          " chebwin loads)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
