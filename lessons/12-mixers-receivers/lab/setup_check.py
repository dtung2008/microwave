"""Pre-class environment verification for lecture 12.

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

# smoke test: a mixer in four lines — cos*cos must FFT to sum & difference
try:
    import numpy as np
    from scipy.signal import welch                           # noqa: F401

    t = np.arange(4096) / 4096.0
    y = np.cos(2 * np.pi * 700 * t) * np.cos(2 * np.pi * 500 * t)
    a = np.abs(np.fft.rfft(y)) / 2048.0
    assert abs(a[200] - 0.5) < 1e-9 and abs(a[1200] - 0.5) < 1e-9
    assert np.sort(a)[-3] < 1e-9        # ...and nothing else
    print("ok: mixer smoke test (cos*cos -> exactly sum and difference)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
