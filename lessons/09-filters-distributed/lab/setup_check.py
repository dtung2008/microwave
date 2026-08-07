"""Pre-class environment verification for lecture 9.

Run:  python setup_check.py     -> must end with "SETUP OK"
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

# smoke test: this lecture's specific moves — an ideal line from
# DefinedGammaZ0 with EXPLICIT gamma (cut in meters), a coupled-section
# Z -> S conversion, and scipy's root finder for the dimension helper.
try:
    import numpy as np
    import skrf
    from scipy.constants import c
    from scipy.optimize import brentq
    from skrf.media import DefinedGammaZ0
    from skrf.network import z2s

    f = np.linspace(1e9, 5e9, 5)
    freq = skrf.Frequency.from_f(f, unit="hz")
    gamma = 1j * 2 * np.pi * f / c
    med = DefinedGammaZ0(frequency=freq, z0=50.0, gamma=gamma)
    lam8 = c / (8.0 * 3e9)
    ln = med.line(lam8, unit="m")
    th = np.angle(ln.s[:, 1, 0])
    # lambda/8 at 3 GHz -> 45 deg of delay there
    assert abs(np.degrees(-th[np.argmin(np.abs(f - 3e9))]) - 45.0) < 1e-6
    # coupled section at exactly 90 deg is an impedance inverter:
    # S21 magnitude for K = (Z0e-Z0o)/2 = 15.68 in a 50-ohm system
    z0e, z0o = 70.60, 39.24
    k_inv = 0.5 * (z0e - z0o)
    z = np.zeros((1, 2, 2), dtype=complex)
    z[:, 0, 0] = z[:, 1, 1] = 0.0                        # cot(90 deg) = 0
    z[:, 0, 1] = z[:, 1, 0] = -0.5j * (z0e - z0o)        # csc(90 deg) = 1
    s = z2s(z, z0=50.0)
    s21_expect = 2 * k_inv * 50.0 / (k_inv**2 + 50.0**2)
    assert abs(abs(s[0, 1, 0]) - s21_expect) < 1e-12
    # brentq (the dimension helper's engine)
    assert abs(brentq(lambda x: x**2 - 2.0, 0, 2) - 2**0.5) < 1e-10
    print("ok: skrf DefinedGammaZ0(gamma explicit) + coupled Z->S + brentq"
          " smoke test")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
