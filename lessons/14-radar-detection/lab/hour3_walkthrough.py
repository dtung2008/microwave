# %% Lecture 14, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

db = lambda x: 10 * np.log10(x)          # noqa: E731  (power ratio -> dB)
undb = lambda x: 10 ** (x / 10)          # noqa: E731

# %% 3.1 Setup verification
import scipy  # noqa: E402
from scipy.stats import ncx2, gamma  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__)

# %% 3.2 The noise after the envelope detector — Rayleigh, measured
# Complex receiver noise, unit total power (I and Q carry half each).
rng = np.random.default_rng(140)
n = 1_000_000
i, q = rng.standard_normal(n), rng.standard_normal(n)
r = np.hypot(i, q) * np.sqrt(0.5)               # envelope, noise power = 1
print(f"mean envelope power <r^2> = {np.mean(r**2):.4f}  (built to be 1)")
print(f"mean envelope       <r>   = {np.mean(r):.4f}  (Rayleigh: sqrt(pi)/2"
      f" = {np.sqrt(np.pi)/2:.4f})")

edges = np.linspace(0, 4.5, 121)
hist, _ = np.histogram(r, bins=edges, density=True)
mid = 0.5 * (edges[:-1] + edges[1:])
pdf = 2 * mid * np.exp(-mid**2)                 # Rayleigh pdf, noise power 1
T6 = np.sqrt(np.log(1e6))                       # threshold, pfa = 1e-6
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(mid, hist, lw=1, label="1e6 measured envelopes")
ax.plot(mid, pdf, "k--", lw=1.2, label="Rayleigh pdf $2r\\,e^{-r^2}$")
ax.axvline(T6, color="r", ls=":", label=f"T for $P_{{fa}}=10^{{-6}}$ = {T6:.3f}")
ax.set_xlabel("envelope r (noise power = 1)")
ax.set_ylabel("probability density")
ax.set_title("what the threshold is up against")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("hw14_rayleigh.png", dpi=130)
print("wrote hw14_rayleigh.png   (the tail past T is the false-alarm rate)")

# %% 3.3 The exact inverse, then the measurement that does not trust it
# P_fa = exp(-T^2 / (2 sigma^2)), per-channel sigma^2 = 1/2  ->  exp(-T^2).
# Invert by hand: T = sqrt(ln(1/P_fa)).
for pfa in (1e-3, 1e-6):
    T = np.sqrt(np.log(1 / pfa))
    meas = np.mean(r > T)
    bar = 3 * np.sqrt(pfa * (1 - pfa) / n)
    print(f"design pfa = {pfa:7.0e}: T = {T:.4f} ({db(T**2):5.2f} dB above the"
          f" noise power) | measured {meas:.2e} "
          f"({int(meas*n)} of 1e6 crossings; 3-sigma +/-{bar:.1e})")
print("at 1e-6 the EXPECTED count in 1e6 trials is 1 — you cannot measure a"
      " pfa with ~1/pfa trials.")
# The 10/pfa rule: 1e7 trials (chunked), expect ~10 crossings.
count = 0
for chunk in range(10):
    rc = np.random.default_rng(1500 + chunk)
    rr = np.hypot(rc.standard_normal(n), rc.standard_normal(n)) * np.sqrt(0.5)
    count += int(np.sum(rr > T6))
print(f"1e7 trials: {count} crossings -> measured pfa = {count/1e7:.1e}"
      f"  (rule of thumb: >= 10/pfa trials to see ~10 events)")

# %% 3.4 P_d needs a signal — Monte Carlo vs Albersheim vs exact (Marcum)
def marcum_pd(snr_db, pfa):
    """Exact single-pulse P_d, nonfluctuating target (the referee)."""
    return ncx2.sf(2 * np.log(1 / pfa), df=2, nc=2 * undb(snr_db))

def albersheim_snr_db(pd, pfa, n_pulses=1):
    a, b = np.log(0.62 / pfa), np.log(pd / (1 - pd))
    return (-5 * np.log10(n_pulses)
            + (6.2 + 4.54 / np.sqrt(n_pulses + 0.44))
            * np.log10(a + 0.12 * a * b + 1.7 * b))

print("SNR ->  P_d (measured | exact) at pfa = 1e-6:")
snrs = np.arange(6.0, 16.01, 1.0)
meas_pd = []
for j, s in enumerate(snrs):
    rj = np.random.default_rng(1510 + j)
    amp = np.sqrt(undb(s))                      # unit noise power
    rr = np.hypot(amp + rj.standard_normal(100_000) * np.sqrt(0.5),
                  rj.standard_normal(100_000) * np.sqrt(0.5))
    meas_pd.append(np.mean(rr > T6))
    if int(s) % 2 == 0:
        print(f"  {s:4.0f} dB: {meas_pd[-1]:.4f} | {marcum_pd(s, 1e-6):.4f}")
alb = albersheim_snr_db(0.9, 1e-6)
exact = brentq(lambda s: marcum_pd(s, 1e-6) - 0.9, 0, 30)
print(f"SNR for (pd=0.9, pfa=1e-6): Albersheim {alb:.2f} dB, exact"
      f" {exact:.2f} dB  <- lecture 1's '13 dB' bar, audited at last")
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(snrs, [marcum_pd(s, 1e-6) for s in snrs], "k-", label="exact (Marcum)")
pd_grid = np.linspace(0.1, 0.9, 33)
ax.plot([albersheim_snr_db(p, 1e-6) for p in pd_grid], pd_grid, "--",
        label="Albersheim")
ax.plot(snrs, meas_pd, "o", ms=4, label="Monte Carlo (1e5/pt)")
ax.axhline(0.9, color="gray", ls=":")
ax.set_xlabel("single-pulse SNR (dB)")
ax.set_ylabel("$P_d$ at $P_{fa}=10^{-6}$")
ax.set_title("the detection curve — steep, but not a step")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("hw14_pd_sweep.png", dpi=130)
print("wrote hw14_pd_sweep.png")

# %% 3.5 Integration — why 10 pulses is not 10x range
# Non-coherent: sum 10 square-law powers. Noise-only sum ~ Gamma(10, 1):
# the threshold is exact by construction (planted truth, no Monte Carlo).
T10 = gamma.isf(1e-6, a=10)                     # 10-pulse power threshold
snr_pp = albersheim_snr_db(0.9, 1e-6, n_pulses=10)
trials = 100_000
rp = np.random.default_rng(1520)
amp = np.sqrt(undb(snr_pp))
z = (np.abs(amp + (rp.standard_normal((trials, 10))
                   + 1j * rp.standard_normal((trials, 10)))
            * np.sqrt(0.5)) ** 2).sum(axis=1)
exact10 = brentq(lambda s: ncx2.sf(2 * T10, df=20, nc=20 * undb(s)) - 0.9,
                 0, 15)                          # exact 10-pulse requirement
print(f"non-coherent, N=10: Albersheim says {snr_pp:.2f} dB per pulse for"
      f" (0.9, 1e-6); exact is {exact10:.2f} dB"
      f" (a {exact10-snr_pp:.2f} dB slip — near its envelope's edge)")
print(f"  exact Gamma threshold T = {T10:.2f}; measured P_d at Albersheim's"
      f" {snr_pp:.2f} dB/pulse = {np.mean(z > T10):.3f}  (0.9 wanted — the"
      " slip, watched)")
print(f"coherent, N=10: SNR gain is exactly 10 dB -> per-pulse need"
      f" {exact - 10:.2f} dB")
print(f"the scoreboard: single pulse needs {exact:.2f} dB;"
      f" 10 coherent {exact-10:.2f}; 10 non-coherent {exact10:.2f}"
      f" (the {exact10-(exact-10):.1f} dB non-coherent tax)")
print(f"range: 10 coherent pulses buy x{10**(10/40):.2f} range;"
      f" non-coherent x{10**((exact-exact10)/40):.2f}. NOT x10 — R^4 again.")

# %% 3.6 CA-CFAR — estimate the noise where the target isn't
# Same scenes and seeds as the homework toolkit (hw14_starter.make_scene).
def make_scene(name, seed):
    rngs = np.random.default_rng(seed)
    nc = 2000
    noise = (rngs.standard_normal(nc) + 1j * rngs.standard_normal(nc)) \
        * np.sqrt(0.5)
    floor = np.ones(nc)
    clutter, targets = None, []
    if name == "clean":
        targets = [(400, 20.0), (1400, 15.0)]
    elif name == "clutter_edge":
        clutter, targets = (1000, 2000, 30.0), [(995, 15.0), (1500, 20.0)]
    elif name == "two_drones":
        targets = [(1000, 22.0), (1006, 15.0)]
    if clutter:
        floor[clutter[0]:clutter[1]] = undb(clutter[2])
    sig = noise * np.sqrt(floor)
    for cell, s in targets:
        sig[cell] += np.sqrt(undb(s) * floor[cell])
    return np.abs(sig) ** 2, targets

def ca_cfar(power, n_train, n_guard, pfa):
    z = np.asarray(power, float)
    nn = z.size
    ps = np.concatenate(([0.0], np.cumsum(z)))
    idx = np.arange(nn)
    llo = np.clip(idx - n_guard - n_train, 0, nn)
    lhi = np.clip(idx - n_guard, 0, nn)
    rlo = np.clip(idx + n_guard + 1, 0, nn)
    rhi = np.clip(idx + n_guard + 1 + n_train, 0, nn)
    tsum = (ps[lhi] - ps[llo]) + (ps[rhi] - ps[rlo])
    cnt = (lhi - llo) + (rhi - rlo)
    alpha = cnt * (pfa ** (-1.0 / cnt) - 1.0)    # closed form from hour 2
    thr = alpha * tsum / cnt
    return z > thr, thr

alpha16 = 16 * (1e-6 ** (-1 / 16) - 1)
print(f"alpha(N=16, pfa=1e-6) = {alpha16:.2f} ({db(alpha16):.2f} dB);"
      f" known-noise multiplier ln(1e6) = {np.log(1e6):.2f}"
      f" -> CFAR loss {db(alpha16/np.log(1e6)):.2f} dB")
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0))
for ax, (name, seed) in zip(axes, [("clean", 1401), ("clutter_edge", 1402),
                                   ("two_drones", 1403)]):
    power, targets = make_scene(name, seed)
    det, thr = ca_cfar(power, 8, 2, 1e-6)
    hits = sorted(c for c, _ in targets if det[c])
    misses = sorted(c for c, _ in targets if not det[c])
    fa = [int(c) for c in np.flatnonzero(det) if c not in {t for t, _ in targets}]
    print(f"scene {name:12s}: hits {hits}  misses {misses}  false alarms {fa}")
    cells = np.arange(power.size)
    ax.plot(cells, db(power), lw=0.4, alpha=0.6)
    ax.plot(cells, db(thr), "r-", lw=1.1)
    ax.plot(np.flatnonzero(det), db(power[det]), "kv", ms=6)
    if name == "two_drones":
        ax.set_xlim(900, 1100)
    ax.set_title(name)
    ax.set_xlabel("range cell")
    ax.set_ylabel("power (dB re thermal)")
    ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("hw14_cfar_scenes.png", dpi=130)
print("wrote hw14_cfar_scenes.png   (the missed 15 dB targets are the"
      " edge-masking and two-drone-masking stories)")
# the masking control arm: same noise (same seed), strong drone deleted
rngs = np.random.default_rng(1403)
solo = (rngs.standard_normal(2000) + 1j * rngs.standard_normal(2000)) \
    * np.sqrt(0.5)
solo[1006] += np.sqrt(undb(15.0))
det_solo, _ = ca_cfar(np.abs(solo) ** 2, 8, 2, 1e-6)
print(f"masking, controlled: the 15 dB drone ALONE in the same noise ->"
      f" detected = {bool(det_solo[1006])}. Its neighbor's power was in the"
      " training cells — the threshold rose, the drone vanished.")

# %% 3.7 Deliberate bug — power statistics where amplitude statistics apply
# The noise power is 1 W total, but each CHANNEL (I, Q) carries only 1/2.
# The Rayleigh exponent wants the per-channel variance: P_fa = exp(-T^2/2s^2)
# with s^2 = 1/2, i.e. exp(-T^2). Someone "simplifies" with the total power
# in the sigma^2 slot: P_fa = exp(-T^2/(2*1)) — one factor of 2, silently.
T_good = np.sqrt(np.log(1e6))                   # exp(-T^2)      = 1e-6
T_bug = np.sqrt(0.5 * np.log(1e6))              # exp(-T^2/ 0.5*2) slipped
meas_good = np.mean(r > T_good)                 # same 1e6 noise draws as 3.2
meas_bug = np.mean(r > T_bug)
print(f"honest threshold  T = {T_good:.4f}: measured pfa = {meas_good:.1e}")
print(f"bugged threshold  T = {T_bug:.4f}: measured pfa = {meas_bug:.1e}"
      f"   <- 10^-6 became ~10^-3: pfa^(1/2), a factor of 2 in an EXPONENT")
print(f"at B = 1 MHz that is ~{meas_bug*1e6:,.0f} false alarms per second"
      " instead of ~1. The screen goes white.")
print("the formula LOOKED right. Monte Carlo caught it — this is why the"
      " homework measures every threshold it sets.")
