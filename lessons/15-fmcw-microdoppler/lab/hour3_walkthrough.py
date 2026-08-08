# %% Lecture 15, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c
from scipy.signal import find_peaks, stft

# The course 77 GHz waveform (homework module 1 derives these from the spec)
F0 = 77e9
LAM = c / F0                  # 3.8934 mm
B = 300e6                     # chirp bandwidth
TC = 10e-6                    # chirp duration (back-to-back)
FS = 51.2e6                   # complex I/Q ADC rate -> 512 samples per chirp
NS = int(round(FS * TC))
NCH = 512                     # chirps per CPI
ALPHA = B / TC                # slope alpha_c = 3e13 Hz/s
DR = c / (2 * B)              # range bin, 0.4997 m

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)


def dechirp(scatterers, n_chirps, seed=None):
    """The delay/Doppler channel + dechirp mixer (the homework toolkit's
    engine, compressed): full phase 2pi(f0 tau + alpha tau t - alpha tau^2/2),
    tau = 2 r(t)/c at every global sample instant. Unit noise if seeded."""
    t_f = np.arange(NS) / FS
    t_g = np.arange(n_chirps)[:, None] * TC + t_f[None, :]
    cube = np.zeros((n_chirps, NS), dtype=complex)
    if seed is not None:
        rng = np.random.default_rng(seed)
        cube += (rng.standard_normal((n_chirps, NS))
                 + 1j * rng.standard_normal((n_chirps, NS))) * np.sqrt(0.5)
    for amp, r_of_t in scatterers:
        tau = 2.0 * r_of_t(t_g) / c
        cube += amp * np.exp(1j * 2 * np.pi * (
            F0 * tau + ALPHA * tau * t_f[None, :] - 0.5 * ALPHA * tau**2))
    return cube


def point(amp, r0, vr=0.0):
    """A point scatterer at range r0, range rate vr (receding positive)."""
    return (amp, lambda t: r0 + vr * t)


# %% 3.2 One chirp, one target — range became a frequency
cube = dechirp([point(1.0, 60.0)], n_chirps=1)
spec_db = 20 * np.log10(np.abs(np.fft.fft(cube[0])) / NS + 1e-300)
k = int(np.argmax(spec_db))
print(f"beat per meter of range: 2*alpha/c = {2 * ALPHA / c / 1e3:.2f} kHz/m")
print(f"FFT peak at bin {k} -> f_b = {k / TC / 1e6:.3f} MHz "
      f"(formula 2*R*alpha/c = {2 * 60.0 * ALPHA / c / 1e6:.3f} MHz)")
print(f"-> R = {k * DR:.3f} m (planted 60.000; the bin is {DR:.4f} m wide)")
print("a 300 MHz problem arrived at the ADC as a 12 MHz tone — the mixer")
print("compressed it (L12's flourish, now quantified)")

# %% 3.3 The R-v coupling term, measured (the honest first-principles pass)
NPAD = 32 * NS                       # zero-pad x32: 15.6 mm read-out grid
still = dechirp([point(1.0, 60.0)], 1)
moving = dechirp([point(1.0, 60.0, vr=+20.0)], 1)     # receding 20 m/s
f_grid = np.fft.fftfreq(NPAD, 1 / FS)
r_still = f_grid[np.argmax(np.abs(np.fft.fft(still[0], NPAD)))] * c / (2 * ALPHA)
r_moving = f_grid[np.argmax(np.abs(np.fft.fft(moving[0], NPAD)))] * c / (2 * ALPHA)
f_d = 2 * 20.0 / LAM
print(f"same target, now receding at 20 m/s: Doppler f_d = 2v/lam = "
      f"{f_d / 1e3:.2f} kHz rides on the beat")
print(f"apparent range: still {r_still:.4f} m -> moving {r_moving:.4f} m "
      f"(shift {1e3 * (r_moving - r_still):+.1f} mm; "
      f"closed form f_d*c/(2*alpha) = {1e3 * f_d * c / (2 * ALPHA):+.1f} mm)")
print(f"worst case inside the unambiguous window (v = {LAM / (4 * TC):.1f} m/s):"
      f" {1e3 * (2 * (LAM / (4 * TC)) / LAM) * c / (2 * ALPHA):.0f} mm ="
      f" HALF a range bin — chirp-sequence waveforms are self-protecting")

# %% 3.4 The chirp sequence — two FFTs and the map has physical axes
TRUTH = [(30.00, 0.0, 30.0), (80.60, -15.30, 25.0), (150.20, +30.00, 20.0)]
gain = (NS / 1.5) * (NCH / 1.5)              # 2-D Hann SNR gain
cube = dechirp([point(np.sqrt(10 ** (s / 10) / gain), r, v)
                for r, v, s in TRUTH], NCH, seed=151)
wr, wd = np.hanning(NS), np.hanning(NCH)
rd = np.fft.fftshift(np.fft.fft(np.fft.fft(cube * wr, axis=1) * wd[:, None],
                                axis=0), axes=0)
power = np.abs(rd) ** 2 / (np.sum(wr**2) * np.sum(wd**2))
v_axis = np.fft.fftshift(np.fft.fftfreq(NCH, TC)) * LAM / 2
print(f"map: {NCH} x {NS} cells, {DR:.4f} m x {v_axis[1] - v_axis[0]:.4f} m/s"
      f" per cell, CPI = {NCH * TC * 1e3:.2f} ms")
p = power.copy()
for r, v, s in TRUTH:
    i, j = np.unravel_index(int(np.argmax(p)), p.shape)
    print(f"  peak {10 * np.log10(power[i, j]):5.1f} dB at "
          f"R = {j * DR:7.2f} m, v = {v_axis[i]:+7.2f} m/s")
    p[max(0, i - 4):i + 5, max(0, j - 4):j + 5] = 0.0
print(f"  planted: {['(%.2f m, %+0.2f m/s)' % (r, v) for r, v, s in TRUTH]}")
e_t = np.sum(np.abs(cube) ** 2)
e_f = np.sum(np.abs(np.fft.fft(np.fft.fft(cube, axis=1), axis=0)) ** 2) / (NS * NCH)
print(f"  Parseval through the (unwindowed) chain: residual "
      f"{abs(e_f - e_t) / e_t:.2e} — the FFT moves energy, never makes it")

# %% 3.5 Resolution is bandwidth — and the window's price
def two_target_cut(sep_m, window):
    cube = dechirp([point(1.0, 100.0), point(1.0, 100.0 + sep_m)], 1)
    w = np.hanning(NS) if window else np.ones(NS)
    return 20 * np.log10(np.abs(np.fft.fft(cube[0] * w, 8 * NS)) + 1e-300)


def n_peaks(cut_db, span=slice(8 * 190, 8 * 220)):
    # count MAINLOBE peaks: within 6 dB of the top (equal targets), so the
    # -13 dB rectangular sidelobes do not masquerade as targets
    pk, _ = find_peaks(cut_db[span], height=cut_db[span].max() - 6.0)
    return len(pk)


for sep in (1.0, 0.6, 0.5, 0.4):
    n_rect = n_peaks(two_target_cut(sep, window=False))
    n_hann = n_peaks(two_target_cut(sep, window=True))
    print(f"two equal targets {sep:.1f} m apart ({sep / DR:.1f} bins): "
          f"rectangular sees {n_rect} peak(s), Hann sees {n_hann}")
print(f"c/2B = {DR:.4f} m is the no-window limit; the Hann window widens the"
      " mainlobe ~x1.6 — dynamic range is bought with resolution")

# %% 3.6 Deliberate bug — forgetting the range window (L13's taper, now lethal)
# strong target 48 dB, weak 18 dB (30 dB down), 16 cells (8 m) away
cube = dechirp([point(np.sqrt(10 ** (48.0 / 10) / (NS / 1.5)), 100.30),
                point(np.sqrt(10 ** (18.0 / 10) / (NS / 1.5)), 108.30)],
               1, seed=152)
kw = int(round(108.30 / DR))
alpha_cfar = 16 * (1e-7 ** (-1 / 16.0) - 1)          # hw14's multiplier
for name, w in (("no window", np.ones(NS)), ("Hann     ", np.hanning(NS))):
    prof = np.abs(np.fft.fft(cube[0] * w)) ** 2 / np.sum(w**2)
    prof_db = 10 * np.log10(prof + 1e-300)
    train = np.r_[prof[kw - 10:kw - 2], prof[kw + 3:kw + 11]]
    thr_db = 10 * np.log10(alpha_cfar * train.mean())
    verdict = "DETECTED" if prof_db[kw] > thr_db else "buried"
    print(f"  {name}: weak cell {prof_db[kw]:6.2f} dB | sidelobe floor "
          f"{10 * np.log10(np.median(train)):6.2f} dB | CFAR threshold "
          f"{thr_db:6.2f} dB -> {verdict}")
print("the strong target's rectangular-window sidelobes still sit ~14 dB")
print("above thermal sixteen cells out (34 dB below its own peak) — a CFAR")
print("threshold rides on them and a target 30 dB down vanishes. The")
print("homework's airliner does exactly this to the drone across 155 m.")

# %% 3.7 Micro-Doppler — the drone waves back
N_B, F_ROT, L_TIP = 2, 100.0, 0.11            # rotor: 2 blades, 6000 rpm
V_TIP = 2 * np.pi * F_ROT * L_TIP
M = 8000                                       # 80 ms dwell at PRF = 100 kHz
n = np.arange(M)
t = n * TC
rng = np.random.default_rng(153)
sig = 1.0 * np.ones(M) + 0j                    # the body, hovering: DC
for k in range(N_B):
    r_blade = L_TIP * np.cos(2 * np.pi * F_ROT * t + 2 * np.pi * k / N_B)
    sig += 0.5 * np.exp(1j * 4 * np.pi * r_blade / LAM)
sig += (rng.standard_normal(M) + 1j * rng.standard_normal(M)) * np.sqrt(0.5) * 0.05
print(f"blade tips: v_tip = 2*pi*f_rot*L = {V_TIP:.1f} m/s -> "
      f"+/-{2 * V_TIP / LAM / 1e3:.1f} kHz of micro-Doppler "
      f"(PRF {1 / TC / 1e3:.0f} kHz keeps it unaliased)")
spec = np.fft.fftshift(np.fft.fft(sig * np.hanning(M)))
freq = np.fft.fftshift(np.fft.fftfreq(M, TC))
p_db = 20 * np.log10(np.abs(spec) + 1e-300)
floor = np.median(p_db)
pk, _ = find_peaks(p_db, height=floor + 10.0, distance=8)
f_lines = freq[pk][freq[pk] > 50.0]
d = np.diff(f_lines)
s0 = np.median(d[d < 1.5 * d.min()])
spacing = float(np.median(d / np.round(d / s0)))
print(f"HERM comb: {len(f_lines)} lines on the positive side, spacing = "
      f"{spacing:.3f} Hz  (N_b * f_rot = {N_B * F_ROT:.0f} Hz — planted)")
print(f"spacing alone gives the product; the blade-flash rate in the"
      f" spectrogram (one flash per {1e3 / (N_B * F_ROT):.0f} ms) is the same"
      " number seen in time")
f_st, t_st, z_st = stft(sig, fs=1 / TC, nperseg=256, noverlap=224,
                        return_onesided=False)
order = np.argsort(f_st)
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
s_db = 20 * np.log10(np.abs(z_st[order]) + 1e-300)
med = float(np.median(s_db))
ax[0].pcolormesh(t_st * 1e3, f_st[order] / 1e3, s_db, vmin=med + 2,
                 vmax=med + 25, shading="auto", cmap="viridis")
ax[0].set_xlabel("time (ms)")
ax[0].set_ylabel("micro-Doppler (kHz)")
ax[0].set_title("the drone waves back: blade flashes")
ax[1].plot(freq / 1e3, p_db, lw=0.7)
ax[1].set_xlim(-0.1, 2.1)
ax[1].set_xlabel("slow-time frequency (kHz)")
ax[1].set_ylabel("power (dB)")
ax[1].set_title("the HERM comb: lines every N_b*f_rot")
fig.tight_layout()
fig.savefig("hour3_microdoppler.png", dpi=130)
print("wrote hour3_microdoppler.png  (a bird has the DC line and none of the"
      " comb — same blip, different spectrogram)")
