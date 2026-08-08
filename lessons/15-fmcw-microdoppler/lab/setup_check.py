"""Pre-class environment verification for lecture 15.

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

# smoke test: a noiseless dechirp must put its beat tone in the exact FFT
# bin the geometry predicts, and scipy.signal.stft must exist (module 3).
try:
    import numpy as np
    from scipy.constants import c
    from scipy.signal import stft

    f0, b, t_c, fs = 77e9, 300e6, 10e-6, 51.2e6
    alpha, n_s, r0 = b / t_c, int(round(fs * t_c)), 60.0
    t = np.arange(n_s) / fs
    tau = 2.0 * r0 / c
    x = np.exp(1j * 2 * np.pi * (f0 * tau + alpha * tau * t
                                 - 0.5 * alpha * tau**2))
    k = int(np.argmax(np.abs(np.fft.fft(x))))
    assert k == int(round(2 * r0 * alpha / c * t_c)) == 120
    f_st, t_st, z = stft(x, fs=fs, nperseg=128, return_onesided=False)
    assert z.shape[0] == 128
    print(f"ok: dechirp smoke test (60 m target -> beat bin {k},"
          " f_b = 12.0 MHz; scipy.signal.stft present)")
except Exception as e:                                       # noqa: BLE001
    print(f"FAIL: smoke test: {type(e).__name__}: {e}")
    ok = False

print("SETUP OK" if ok else "SETUP FAILED — fix the lines above")
