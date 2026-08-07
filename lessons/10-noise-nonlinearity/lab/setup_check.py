"""Pre-class environment verification for lecture 10.

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

# smoke test 1: Friis's cascade limit — an attenuator in front of a chain
# must raise its noise figure by exactly the attenuation, in dB
try:
    import numpy as np

    undb = lambda x: 10.0 ** (x / 10.0)                      # noqa: E731
    db = lambda x: 10.0 * np.log10(x)                        # noqa: E731

    def nf_casc_db(stages):                                  # (gain_db, nf_db)
        g, f = 1.0, 1.0
        for g_db, nf_db in stages:
            f += (undb(nf_db) - 1.0) / g
            g *= undb(g_db)
        return db(f)

    rest = [(20.0, 1.5), (-7.0, 8.0)]
    delta = nf_casc_db([(-2.0, 2.0)] + rest) - nf_casc_db(rest)
    assert abs(delta - 2.0) < 1e-12
    print("ok: Friis smoke test (2 dB pad in front adds exactly 2.0000 dB NF)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: Friis smoke test: {type(e).__name__}: {e}")
    ok = False

# smoke test 2: a cubic driven by two exact-bin tones must put its IM3 at
# 2f1-f2 and 2f2-f1 — the spurs lecture 10 lives on
try:
    n = 4096
    t = np.arange(n) / n
    x = np.cos(2 * np.pi * 500 * t) + np.cos(2 * np.pi * 510 * t)
    a = np.abs(np.fft.rfft(x - 0.05 * x**3)) * 2.0 / n
    assert a[490] > 1e-4 and a[520] > 1e-4          # IM3 pair present
    assert a[505] < 1e-12                            # nothing between the tones
    print("ok: two-tone smoke test (IM3 lands at 2f1-f2 and 2f2-f1)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: two-tone smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
