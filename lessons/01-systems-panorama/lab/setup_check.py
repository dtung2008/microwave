"""Pre-class environment verification for lecture 1 (and the whole course).

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

# smoke test: build a one-port Network and a dB round trip
try:
    import numpy as np
    import skrf

    freq = skrf.Frequency(1, 10, 11, "ghz")
    ntwk = skrf.Network(frequency=freq,
                        s=np.full((11, 1, 1), 0.5 + 0j), z0=50)
    assert ntwk.nports == 1
    assert abs(10 * np.log10(10 ** (3.0103 / 10)) - 3.0103) < 1e-12
    print("ok: skrf Network smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
