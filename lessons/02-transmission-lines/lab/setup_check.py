"""Pre-class environment verification for lecture 2.

Run:  python setup_check.py     -> must end with "SETUP OK"

Same environment as lecture 1; the smoke test now exercises the two skrf
media this lecture leans on (DistributedCircuit, DefinedGammaZ0).
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

# smoke test: this lecture's two referee media, on a 50-ohm RLGC cell
try:
    import numpy as np
    import skrf
    from skrf.media import DefinedGammaZ0, DistributedCircuit

    fr = skrf.Frequency(2, 3, 11, "ghz")
    med = DistributedCircuit(frequency=fr, R=10.0, L=250e-9,
                             G=4.5e-4, C=100e-12)
    assert abs(med.z0[0].real - 50.0) < 0.01        # sqrt(L/C) = 50
    assert med.gamma[0].real > 0                    # lossy line attenuates
    dgz = DefinedGammaZ0(frequency=fr, z0=50, gamma=med.gamma, z0_port=50)
    ntwk = dgz.line(0.1, unit="m")
    assert ntwk.nports == 2
    assert np.all(np.abs(ntwk.s[:, 1, 0]) < 1.0)    # passive
    print("ok: skrf DistributedCircuit / DefinedGammaZ0 smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
