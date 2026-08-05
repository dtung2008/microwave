"""Pre-class environment verification for lecture 4.

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

# smoke test: this lecture's referee calls — S <-> ABCD round trip and the
# ** cascade operator, on a 2-port the size the homework uses
try:
    import numpy as np
    import skrf
    from skrf.network import a2s, s2a

    freq = skrf.Frequency(1, 3, 11, "ghz")
    s = np.zeros((11, 2, 2), dtype=complex)
    s[:, 0, 1] = s[:, 1, 0] = 0.5          # a x1/2 pad
    s[:, 0, 0] = s[:, 1, 1] = 0.1
    assert np.abs(a2s(s2a(s, z0=50), z0=50) - s).max() < 1e-12
    pad = skrf.Network(frequency=freq, s=s, z0=50)
    two = pad ** pad                        # the cascade operator
    assert two.s.shape == (11, 2, 2)
    print("ok: skrf s2a/a2s round trip + ** cascade smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
