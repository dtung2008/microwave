"""Pre-class environment verification for lecture 6.

Run:  python setup_check.py     -> must end with "SETUP OK"

Same course environment as lecture 1, plus a smoke test of the two referees
this lecture leans on: skrf media cascading and skrf.qfactor.Qfactor.
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

# smoke test 1: an ideal-line cascade in skrf media (this week's referee #1)
try:
    import numpy as np
    import skrf
    from skrf.media import DefinedGammaZ0

    freq = skrf.Frequency(2, 4, 5, "ghz")
    med = DefinedGammaZ0(frequency=freq, z0=25.0,
                         gamma=1j * 2 * np.pi * freq.f / 299792458.0)
    line = med.line(299792458.0 / 3e9 / 4, unit="m")
    line.renormalize(50.0)
    assert line.nports == 2
    print("ok: skrf media line + renormalize smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: media smoke test: {type(e).__name__}: {e}")
    ok = False

# smoke test 2: the Qfactor fitter (this week's referee #2)
try:
    import numpy as np
    import skrf
    from skrf.qfactor import Qfactor

    f = np.linspace(2.94e9, 3.06e9, 201)
    x = f / 3e9 - 3e9 / f
    s21 = 0.5 / (1 + 1j * 250.0 * x)
    ntwk = skrf.Network(frequency=skrf.Frequency.from_f(f, unit="hz"),
                        s=s21.reshape(-1, 1, 1), z0=50)
    qf = Qfactor(ntwk, res_type="transmission")
    res = qf.fit()
    q0 = qf.Q_unloaded(res, A=1.0)
    assert abs(qf.Q_L - 250.0) / 250.0 < 0.01
    assert abs(q0 - 500.0) / 500.0 < 0.01
    print(f"ok: skrf Qfactor smoke test (Q_L fit {qf.Q_L:.1f} on a planted"
          " 250.0)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: Qfactor smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
