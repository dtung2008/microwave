"""Pre-class environment verification for lecture 11.

Run:  python setup_check.py     -> must end with "SETUP OK"

Also checks (without failing) whether you have downloaded the vendor .s2p —
HOMEWORK.md step 0. Everything runs without it, on the synthetic demo device.
"""
import sys
from pathlib import Path

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

# smoke test: the lecture-11 API surface — stability, circles, max gain
try:
    import numpy as np
    import skrf

    freq = skrf.Frequency(1, 4, 4, "ghz")
    s = np.zeros((4, 2, 2), dtype=complex)
    s[:, 0, 0] = 0.5
    s[:, 1, 0] = 2.0
    s[:, 0, 1] = 0.1
    s[:, 1, 1] = 0.3
    nt = skrf.Network(frequency=freq, s=s, z0=50)
    k = nt.stability                      # Rollett K, the module-1 referee
    assert k.shape == (4,)
    loci = nt[0].stability_circle(target_port=1, npoints=11)
    assert loci.shape[0] == 11
    g = nt.max_gain                       # MAG/MSG, the module-2 referee
    assert np.all(g > 0)
    print("ok: skrf stability / stability_circle / max_gain smoke test"
          f" (K = {k[0]:.3f})")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

# the vendor file (informational only — never a failure)
from_here = Path(__file__).resolve().parent
vendor = from_here / "PGA-103+_5V_Plus25DegC.s2p"
if vendor.exists():
    print(f"ok: vendor file present ({vendor.name})")
else:
    print(f"note: {vendor.name} not found — HOMEWORK.md step 0 tells you how"
          " to download it; until then the lab uses the synthetic demo device.")

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
