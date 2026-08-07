# %% Lecture 13, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c as C

# scipy's chebwin warning is about PSD noise bandwidth, not about the
# equal-ripple sidelobe guarantee — irrelevant for pointing antennas.
warnings.filterwarnings("ignore", message="This window is not suitable")
from scipy.signal.windows import chebwin

db20 = lambda x: 20 * np.log10(np.maximum(np.abs(x), 1e-300))  # noqa: E731

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 The array-factor engine — ten lines, written live
# The course array: N = 16 elements on a line, d = lambda/2, 10 GHz.
# Element n sits at x = n*d; a plane wave from angle theta (from broadside)
# reaches it early by d*sin(theta) — phase +k*d*n*sin(theta). Sum the spokes.
F, N = 10e9, 16
LAM = C / F
D = LAM / 2
K = 2 * np.pi / LAM
TH = np.linspace(-90.0, 90.0, 180001)          # 0.001-deg grid

def af(w, d_m, th_deg, ph=None):                # THE ten lines
    w = np.asarray(w, dtype=complex)
    if ph is not None:
        w = w * np.exp(1j * np.asarray(ph))
    n = np.arange(w.size)
    psi = K * d_m * np.sin(np.radians(th_deg))  # radians into np.sin. 3.7
    return np.exp(1j * np.outer(psi, n)) @ w    # waits for the other choice

def stats(a):                                   # measure, don't assume
    a = np.abs(a) / np.abs(a).max()
    i = int(np.argmax(a))
    lo = hi = i
    while lo > 0 and a[lo - 1] <= a[lo]:
        lo -= 1                                 # walk to the first null...
    while hi < a.size - 1 and a[hi + 1] <= a[hi]:
        hi += 1
    j0, j1 = np.searchsorted(a[lo:i], 2**-0.5) + lo, i
    while a[j1] > 2**-0.5 and j1 < hi:
        j1 += 1                                 # ...and the -3 dB edges
    side = np.r_[a[:lo], a[hi + 1:]]
    return dict(peak_deg=TH[i], hpbw_deg=TH[j1] - TH[j0],
                sll_db=float(db20(side.max())) if side.size else -np.inf)

u16 = np.abs(af(np.ones(N), D, TH))
s = stats(u16)
print(f"uniform 16-element, broadside: |AF|max = {u16.max():.1f} (= N)"
      f" at {s['peak_deg']:+.3f} deg")
print(f"  first null: measured near {TH[np.argmin(u16[90000:98000])+90000]:.3f}"
      f" deg | formula asin(lambda/(N d)) = "
      f"{np.degrees(np.arcsin(LAM / (N * D))):.3f} deg")
print(f"  HPBW = {s['hpbw_deg']:.4f} deg | closed form 0.886*lambda/(N d) -> "
      f"{np.degrees(0.886 * LAM / (N * D)):.4f} deg (small-angle)")
print(f"  SLL  = {s['sll_db']:.4f} dB | the sinc story says -13.26;"
      " finite N = 16 lifts it +0.11 dB. Both numbers are 'the' -13 dB.")

# %% 3.3 The DSP homecoming — the array factor IS a DFT, tapers are windows
# Sample AF at psi = 2*pi*k/M and it is EXACTLY the zero-padded FFT of the
# weight vector. Spatial sidelobes and spectral leakage are one mathematics.
M = 4096
psi_grid = 2 * np.pi * np.arange(M) / M
af_psi = np.abs(np.exp(1j * np.outer(psi_grid, np.arange(N))) @ np.ones(N))
fft_w = np.abs(np.fft.fft(np.ones(N), M))
print(f"|AF(psi_k)| vs |FFT(weights, {M})|: max difference = "
      f"{np.abs(af_psi - fft_w).max():.2e}   <- same object")
w30 = chebwin(N, at=30.0)
c = np.abs(af(w30, D, TH))
sc = stats(c)
print(f"chebwin(16, at=30): SLL = {sc['sll_db']:.4f} dB (equal-ripple, as"
      f" guaranteed), HPBW = {sc['hpbw_deg']:.4f} deg")
print(f"  the taper trade, measured: sidelobes -13.15 -> -30 dB costs"
      f" beamwidth x{sc['hpbw_deg'] / s['hpbw_deg']:.4f}")
print("  same trade you met windowing FFTs: leakage down, main lobe wide.")

# %% 3.4 Steering = linear phase — and what the scan costs
# Steer to theta0 by cancelling the geometric phase: ph_n = -k d n sin(theta0)
hp = {}
for t0 in (0.0, 25.0, 45.0):
    ph = -K * D * np.arange(N) * np.sin(np.radians(t0))
    st = stats(af(np.ones(N), D, TH, ph))
    hp[t0] = st["hpbw_deg"]
    print(f"  steer to {t0:4.0f} deg: peak at {st['peak_deg']:+8.3f} deg,"
          f" HPBW = {st['hpbw_deg']:.4f} deg, worst lobe {st['sll_db']:6.2f}"
          " dB")
print(f"  broadening 0 -> 45 deg: x{hp[45.0] / hp[0.0]:.3f} (~1/cos 45 ="
      f" {1 / np.cos(np.radians(45)):.3f}) — the aperture FORESHORTENS:"
      " seen from 45 deg the 24 cm array looks 17 cm wide.")

# %% 3.5 The d > lambda/2 crime — the grating lobe walks in where predicted
# Open the spacing to 0.65 lambda and scan. A second full-height beam enters
# visible space once sin(theta0) > lambda/d - 1.
D2 = 0.65 * LAM
onset = np.degrees(np.arcsin(LAM / D2 - 1.0))
print(f"d = 0.65 lambda: predicted grating onset at scan angle "
      f"asin(lambda/d - 1) = {onset:.2f} deg")

def worst_far_lobe(t0, d_m):
    ph = -K * d_m * np.arange(N) * np.sin(np.radians(t0))
    a = np.abs(af(np.ones(N), d_m, TH, ph))
    far = np.abs(TH - t0) > 15.0
    j = np.where(far)[0][np.argmax(a[far])]
    return float(db20(a[j] / a.max())), float(TH[j])

fig, axes = plt.subplots(2, 3, figsize=(13.5, 6.6), sharey=True)
for ax, t0 in zip(axes.flat, (0.0, 15.0, 30.0, 33.0, 40.0, 45.0)):
    ph = -K * D2 * np.arange(N) * np.sin(np.radians(t0))
    a = np.abs(af(np.ones(N), D2, TH, ph))
    lvl, ang = worst_far_lobe(t0, D2)
    ax.plot(TH, db20(a / a.max()), lw=0.9)
    ax.set_ylim(-40, 2)
    ax.set_title(f"scan {t0:.0f}°: far lobe {lvl:.1f} dB", fontsize=10)
    ax.grid(alpha=0.3)
    print(f"  scan {t0:4.0f} deg: worst far-out lobe {lvl:6.2f} dB"
          f" at {ang:+8.3f} deg")
fig.suptitle("d = 0.65λ, scanning 0° → 45°: the grating lobe walks in")
fig.tight_layout()
fig.savefig("hour3_grating.png", dpi=130)
print("wrote hour3_grating.png")
lvl45, ang45 = worst_far_lobe(45.0, D2)
gform = np.degrees(np.arcsin(np.sin(np.radians(45.0)) - LAM / D2))
print(f"  at scan 45: grating lobe at {ang45:.3f} deg, {lvl45:.2f} dB"
      f" | formula asin(sin 45 - lambda/d) = {gform:.3f} deg")
print(f"  full height — the array cannot tell {ang45:.0f} deg from +45."
      f" The no-crime spacing: d < lambda/(1+sin 45) = "
      f"{LAM / (1 + np.sin(np.radians(45))) / LAM:.4f} lambda.")

# %% 3.6 Aperture sizing — what separates two drones 100 m apart at 5 km?
sep_deg = np.degrees(2 * np.arctan(50.0 / 5000.0))
print(f"two drones 100 m apart at 5 km subtend {sep_deg:.3f} deg")
d_dish = LAM / np.radians(sep_deg)
print(f"beamwidth ~ lambda/D -> need D ~ {d_dish:.2f} m of aperture at"
      " 10 GHz")
r16 = 100.0 / np.radians(s['hpbw_deg'])
print(f"our 16-element ULA (24 cm, HPBW {s['hpbw_deg']:.2f} deg) separates"
      f" them only inside {r16:.0f} m")
print(f"tie-back to lecture 1: this row is D = 10*log10(16) ="
      f" {10 * np.log10(16):.2f} dBi. The course dish is 33 dBi.")
print(f"  a 16x16 planar sheet: D ~ pi*N*M -> "
      f"{10 * np.log10(np.pi * 256):.2f} dBi; 33 dBi wants ~"
      f"{10 ** 3.3 / np.pi:.0f} lambda/2 elements (~26 x 25). One line, two"
      " lectures: L16 steers this sheet.")

# %% 3.7 Deliberate bug — degrees fed into np.sin
# Beautiful, plausible, wrong: the pattern below was computed with theta in
# DEGREES handed straight to np.sin. It looks like a fine multi-beam array.
af_bug = np.abs(np.exp(1j * np.outer(K * D * np.sin(TH), np.arange(N)))
                @ np.ones(N))                    # sin(degrees)!
pk = np.where((af_bug[1:-1] > af_bug[:-2]) & (af_bug[1:-1] >= af_bug[2:])
              & (af_bug[1:-1] > 0.9 * N))[0] + 1
spacing = float(np.mean(np.diff(TH[pk])))
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
ax[0].plot(TH, db20(u16 / u16.max()), lw=0.9)
ax[0].set_title("radians (the truth): one beam, -13 dB sidelobes")
ax[1].plot(TH, db20(af_bug / af_bug.max()), lw=0.9, color="#b3261e")
ax[1].set_title("degrees into np.sin: a beautiful, plausible lie")
for a_ in ax:
    a_.set_ylim(-40, 2)
    a_.set_xlabel("theta (deg)")
    a_.grid(alpha=0.3)
ax[0].set_ylabel("dB")
fig.tight_layout()
fig.savefig("hour3_bug.png", dpi=130)
print("wrote hour3_bug.png")
print(f"the bugged 'array' shows {pk.size} full-height beams, spaced"
      f" {spacing:.4f} deg apart.")
print(f"  {spacing:.4f} = pi. A period of exactly pi on a DEGREES axis is"
      " the fingerprint: np.sin ate degrees. sin(theta_deg) repeats every"
      " pi units, and every repeat is a fake broadside.")
print("  nothing crashed, the plot is gorgeous, and a 16-element radar just"
      " grew 57 beams. Label your angles: *_deg vs *_rad.")
