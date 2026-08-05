# %% Lecture 12, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c as C
from scipy.signal import welch

db = lambda x: 10 * np.log10(x)          # noqa: E731  (power ratio -> dB)
undb = lambda x: 10 ** (x / 10)          # noqa: E731

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 Mixing is multiplication — the trig identity, measured
# cos(a)cos(b) = 1/2 cos(a-b) + 1/2 cos(a+b). Two tones in, exactly two
# tones out — at the sum and the difference. Audio-rate stand-ins all hour:
# f_LO = 800 Hz, f_RF = 530 Hz (the physics is scale-free).
FS, N = 8192.0, 8192                     # 1 s of samples -> 1 Hz FFT bins
t = np.arange(N) / FS
F_LO, F_RF = 800.0, 530.0
x_rf = np.cos(2 * np.pi * F_RF * t)
x_lo = np.cos(2 * np.pi * F_LO * t)
y = x_rf * x_lo                          # an ideal multiplier
amp = np.abs(np.fft.rfft(y)) / (N / 2)   # amplitude spectrum
print(f"multiplier output lines: {F_LO - F_RF:.0f} Hz (amp {amp[270]:.4f})"
      f" and {F_LO + F_RF:.0f} Hz (amp {amp[1330]:.4f}) — and nothing else"
      f" (next largest bin: {np.sort(amp)[-3]:.2e})")
print(f"conversion to the difference: 20*log10({amp[270]:.3f}/1) = "
      f"{20 * np.log10(amp[270]):.2f} dB   (the ideal multiplier's -6.02:"
      " half the energy went to the sum you will filter off)")

# %% 3.3 Real mixers are switches — the +/-1 mixer and its Fourier view
# Drive the LO hard and the device stops multiplying and starts switching:
# y = x_rf * sign(cos w_LO t). A square wave is (4/pi)[cos - cos3/3 + ...],
# so products appear at (odd m)*f_LO +/- f_RF, and the wanted line gets
# amplitude 2/pi — the famous -3.92 dB switching conversion loss.
y_sw = x_rf * np.sign(x_lo)
amp_sw = np.abs(np.fft.rfft(y_sw)) / (N / 2)
for f in (270, 1330, 1870, 2930, 3470):
    print(f"  line at {f:5d} Hz: amp {amp_sw[f]:.4f}")
print(f"conversion loss, measured: {20 * np.log10(amp_sw[270]):.2f} dB"
      f"   (theory 20*log10(2/pi) = {20 * np.log10(2 / np.pi):.2f})")
print("odd-m products only — and the 5*LO sum (4530 Hz) has ALIASED to"
      f" {8192 - 4530} Hz: amp {amp_sw[8192 - 4530]:.4f}. Sampling is a"
      " mixer too. Hold that thought for the ADC.")

# %% 3.4 The image, by construction — two frequencies, one IF bin
# f_LO = 1000 Hz, IF = 270 Hz. The signal at f_LO + IF = 1270 Hz and the
# image at f_LO - IF = 730 Hz BOTH land on 270 Hz. Perfect mirror.
f_lo2 = 1000.0
sig = np.cos(2 * np.pi * 1270.0 * t)            # the wanted signal
img = 0.5 * np.cos(2 * np.pi * 730.0 * t)       # an interferer at the image
lo2 = np.cos(2 * np.pi * f_lo2 * t)
a_sig = np.abs(np.fft.rfft(sig * lo2)) / (N / 2)
a_img = np.abs(np.fft.rfft(img * lo2)) / (N / 2)
a_both = np.abs(np.fft.rfft((sig + img) * lo2)) / (N / 2)
print(f"signal alone : IF line at 270 Hz, amp {a_sig[270]:.4f}")
print(f"image alone  : IF line at 270 Hz, amp {a_img[270]:.4f}")
print(f"both together: IF line at 270 Hz, amp {a_both[270]:.4f}"
      "  <- one bin, two owners, inseparable after the mixer")
print("the only defense happened BEFORE the mixer: filtering (preselector)"
      " or planning (put the image where nobody transmits).")

# %% 3.5 The whole m,n grid — a behavioral diode lights up every product
# A diode is exponential, and exp() contains every power of its argument:
# i = exp(a*cos w_LO t + b*cos w_RF t) has a line at EVERY |m f_LO ± n f_RF|.
v = 1.2 * x_lo + 0.9 * x_rf
i = np.exp(v)
spec = np.abs(np.fft.rfft(i - i.mean())) / N
p_dbc = db(np.maximum(spec**2 / (spec**2).max(), 1e-30))
predicted = sorted({(m, n, abs(m * F_LO + s * n * F_RF))
                    for m in range(4) for n in range(4) if m + n > 0
                    for s in ((-1, 1) if m * n else (-1,))})
hits = sum(1 for (_, _, f) in predicted
           if p_dbc[int(f)] > -80 and
           p_dbc[int(f)] == p_dbc[int(f) - 2:int(f) + 3].max())
print(f"m,n <= 3 grid: {len(predicted)} predicted products; measured peaks"
      f" in the exact bin: {hits}/{len(predicted)}")
print(f"  e.g. (2,2) at {2*F_LO - 2*F_RF:.0f} Hz: {p_dbc[540]:.1f} dBc |"
      f" (3,3) at {3*F_LO - 3*F_RF:.0f} Hz: {p_dbc[810]:.1f} dBc")
print("the grid does not stop at 3 — e.g. 4*f_LO at 3200 Hz sits at"
      f" {p_dbc[3200]:.1f} dBc. Every product is a place an interferer"
      " can enter. That is why frequency PLANNING exists.")
fig, ax = plt.subplots(figsize=(9, 3.6))
f_axis = np.fft.rfftfreq(N, 1 / FS)
ax.plot(f_axis, p_dbc, lw=0.7)
for (_, _, f) in predicted:
    ax.axvline(f, color="#b3261e", alpha=0.25, lw=0.8)
ax.set_xlim(0, 4096); ax.set_ylim(-100, 5)
ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("dBc")
ax.set_title("behavioral diode mixer: every |m·f_LO ± n·f_RF| exists")
fig.tight_layout(); fig.savefig("mixer_grid.png", dpi=130)
print("wrote mixer_grid.png")

# %% 3.6 The frequency-plan calculator — scaled up to the course radar
# RF 10.0-10.4 GHz, IF filter 10 MHz wide, ADC 100 MS/s (undersampling: the
# IF band must fit ONE Nyquist zone). The emitter survey near the site:
RF_LO, RF_HI, IF_BW, ADC_FS = 10.0e9, 10.4e9, 10e6, 100e6
EMITTERS = [("marine radars", 9.300e9, 9.500e9),
            ("airfield radar", 9.595e9, 9.605e9),
            ("police/amateur", 10.500e9, 10.550e9),
            ("backhaul link", 11.200e9, 11.700e9)]

def image_band(if_hz, side):             # image = f_RF ± 2*IF, band-swept
    s = +2 if side == "high" else -2
    return RF_LO + s * if_hz, RF_HI + s * if_hz

def audit(if_hz, side):
    lo, hi = image_band(if_hz, side)
    own = not (lo < RF_HI and RF_LO < hi)
    zone = int((if_hz - IF_BW/2) // (ADC_FS/2)) == int((if_hz + IF_BW/2)
                                                       // (ADC_FS/2))
    coll = [(nm, e1, e2) for nm, e1, e2 in EMITTERS
            if lo < e2 and e1 < hi]
    return own, zone, coll

# An innocent-looking plan: low-side LO, catalog 321.4 MHz IF filter.
IF = 321.4e6
lo_band = (RF_LO - IF, RF_HI - IF)
own, zone, coll = audit(IF, "low")
print(f"PLAN: low-side LO {lo_band[0]/1e9:.4f}-{lo_band[1]/1e9:.4f} GHz,"
      f" IF = {IF/1e6:.1f} MHz")
print(f"  IF in ADC Nyquist zone {int(IF // (ADC_FS/2))}"
      f" [{int(IF//(ADC_FS/2))*50}-{int(IF//(ADC_FS/2))*50+50} MHz]:"
      f" fits = {zone}")
print(f"  image band {image_band(IF,'low')[0]/1e9:.4f}-"
      f"{image_band(IF,'low')[1]/1e9:.4f} GHz, outside our own band: {own}")
print("  every self-consistency check passes. Ship it? …")

# %% 3.7 Deliberate bug — the plan that works until you consult the table
# Nothing above was WRONG. But nobody asked who TRANSMITS in the image band.
own, zone, coll = audit(IF, "low")
print("consulting the emitter table for the low-side image band:")
for nm, e1, e2 in coll:
    print(f"  COLLISION: {nm} ({e1/1e9:.3f}-{e2/1e9:.3f} GHz) sits in the"
          " image band — full conversion gain, zero rejection available")
f_tune = 9.6e9 + 2 * IF
print(f"tuned to {f_tune/1e9:.4f} GHz, the 9.600 GHz airfield radar IS the"
      " image. The receiver hears it as loudly as the drone.")
own_h, zone_h, coll_h = audit(IF, "high")
print(f"flip the LO high-side: image band "
      f"{image_band(IF,'high')[0]/1e9:.4f}-"
      f"{image_band(IF,'high')[1]/1e9:.4f} GHz, collisions: "
      f"{len(coll_h)} — same IF filter, same ADC, clean plan.")
print("the homework's audit does this to order 3 with severities; the fix"
      " cost one wire. Finding it after installation costs a site visit.")

# %% 3.8 Phase noise — the skirt that buries the slow drone
# Synthesize an LO with the course profile (dBc/Hz), verify the synthesis,
# then watch a 60 dB clutter line's skirt swallow a 1 m/s drone.
PROFILE = [(1.0, -40.0), (10.0, -40.0), (100.0, -70.0),
           (1e3, -90.0), (1e4, -110.0), (1e5, -120.0)]

def l_dbc(f):
    return np.interp(np.log10(np.maximum(f, 1e-6)),
                     np.log10([p[0] for p in PROFILE]),
                     [p[1] for p in PROFILE])

FS2, T2 = 4096.0, 16.0
N2 = int(FS2 * T2)
rng = np.random.default_rng(1212)
f_r = np.fft.rfftfreq(N2, 1 / FS2)
s_phi = np.zeros_like(f_r)
s_phi[1:] = 2 * undb(l_dbc(f_r[1:]))     # one-sided S_phi = 2*L(f)
z = rng.standard_normal(len(f_r)) + 1j * rng.standard_normal(len(f_r))
a = z * np.sqrt(s_phi * FS2 * N2) / 2
a[0], a[-1] = 0.0, a[-1].real
phi = np.fft.irfft(a, N2)
print(f"integrated phase jitter (1 Hz-2 kHz): {np.degrees(np.std(phi)):.2f}"
      " deg RMS — tiny. The problem is never the total; it is WHERE it sits.")
f_w, s_meas = welch(phi, fs=FS2, nperseg=4096, noverlap=2048)
for f0 in (100.0, 1000.0):
    k = int(np.argmin(np.abs(f_w - f0)))
    print(f"  synthesized LO, measured L({f0:.0f} Hz) = "
          f"{db(s_meas[k]/2):.1f} dBc/Hz   (profile: {l_dbc(f0):.0f})")
t2 = np.arange(N2) / FS2
CLUTTER_DB, F0_HZ = 60.0, 10.2e9
hz_per_mps = 2 * F0_HZ / C
x = np.sqrt(undb(CLUTTER_DB)) * np.exp(1j * phi)      # the ground, +60 dB
for v in (1.0, 3.0):                     # two drones: a drift and a jog
    x = x + np.exp(1j * (2*np.pi * round(v*hz_per_mps) * t2 + phi))
f_d, pxx = welch(x, fs=FS2, nperseg=4096, noverlap=2048, detrend=False,
                 return_onesided=False)
for v in (1.0, 3.0):
    k = int(round(v * hz_per_mps))
    kk = int(np.argmin(np.abs(f_d - k)))
    skirt = np.median(np.r_[pxx[kk-12:kk-3], pxx[kk+4:kk+13]])
    snr = db(max(pxx[kk] - skirt, skirt*1e-6) / skirt)
    verdict = "visible" if snr >= 13 else "BURIED under the skirt"
    print(f"  drone at {v:.0f} m/s (f_d = {k} Hz): line-over-skirt = "
          f"{snr:5.1f} dB -> {verdict}")
print("same drone RCS, same range, same power — only the OSCILLATOR decides"
      " which one exists. The homework measures the exact crossover speed.")

# %% 3.9 The FMCW dechirp receiver — the mixer is the ranging engine
# FMCW (frequency-modulated continuous wave): transmit a chirp, mix the echo
# with the chirp itself. The delay tau becomes a constant BEAT frequency
# f_b = alpha * tau. Audio-rate demo; lecture 15 owns the full derivation.
B_HZ, T_S = 2000.0, 1.0                  # chirp: 2 kHz span in 1 s
alpha = B_HZ / T_S                       # chirp slope, Hz/s
tau = 0.050                              # echo delay, 50 ms
tt = np.arange(int(FS * T_S)) / FS
chirp = np.cos(2 * np.pi * (100.0 * tt + 0.5 * alpha * tt**2))
n_tau = int(tau * FS)
beat = chirp[n_tau:] * chirp[:-n_tau]    # dechirp = multiply by the echo
spec_b = np.abs(np.fft.rfft(beat * np.hanning(len(beat))))
f_b = np.fft.rfftfreq(len(beat), 1 / FS)
k = np.argmax(spec_b[f_b < 1000])        # low-pass: keep the difference term
print(f"dechirp beat: measured {f_b[k]:.1f} Hz | planted alpha*tau = "
      f"{alpha * tau:.1f} Hz")
alpha_x = 400e6 / 1e-3                   # the course radar: 400 MHz in 1 ms
print(f"scale to X-band: alpha = 4e11 Hz/s -> {2*alpha_x/C:.1f} Hz of beat"
      " per meter of range")
print(f"  drone at 3 km -> f_b = {2*3000*alpha_x/C/1e6:.2f} MHz; the"
      f" 100 MS/s ADC reaches {50e6*C/(2*alpha_x)/1e3:.2f} km of range.")
print("a 400 MHz-wide problem arrived at the ADC as single-digit MHz: the"
      " mixer did the compression. That is lecture 15's whole receiver.")
