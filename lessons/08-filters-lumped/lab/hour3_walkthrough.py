# %% Lecture 8, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# %% 3.1 Setup verification
import scipy
import skrf

print("python    ", sys.version.split()[0])
print("numpy     ", np.__version__, "  scipy", scipy.__version__)
print("matplotlib", matplotlib.__version__, "  scikit-rf", skrf.__version__)

# %% 3.2 The g-value recursion — and scipy as the independent referee
# The whole engine is a dozen lines. Butterworth is one closed form;
# Chebyshev is the beta/gamma recursion from hour 1.
def g_values(family, n, ripple_db=None):
    if family == "butterworth":
        k = np.arange(1, n + 1)
        return np.concatenate([2 * np.sin((2*k - 1) * np.pi / (2*n)), [1.0]])
    beta = np.log(1 / np.tanh(ripple_db * np.log(10) / 40))   # ln coth(r/17.37)
    gam = np.sinh(beta / (2 * n))
    a = np.sin((2 * np.arange(1, n + 1) - 1) * np.pi / (2 * n))
    b = gam**2 + np.sin(np.arange(1, n + 1) * np.pi / n) ** 2
    g = [2 * a[0] / gam]
    for k in range(1, n):
        g.append(4 * a[k-1] * a[k] / (b[k-1] * g[k-1]))
    return np.array(g + [1.0 if n % 2 else 1 / np.tanh(beta / 4) ** 2])

for fam, rp in [("butterworth", None), ("chebyshev", 0.5)]:
    print(f"{fam}" + (f" {rp} dB ripple" if rp else "") + ":")
    for n in (2, 3, 4, 5):
        print(f"  N={n}: g = {np.round(g_values(fam, n, rp), 4)}")

# hour 1's hand-derived N=1 case: one shunt C = 2*eps. The recursion agrees:
eps = np.sqrt(10 ** (0.5 / 10) - 1)
print(f"N=1 check: recursion g1 = {g_values('chebyshev', 1, 0.5)[0]:.6f}, "
      f"hand-derived 2*eps = {2*eps:.6f}")

# referee: sweep the g-ladder (prototype level: series jWg / shunt jWg, 1-ohm
# ends) against scipy's own cheb1ap poles. Two unrelated code paths.
from scipy.signal import cheb1ap, freqs, zpk2tf

def proto_s21_db(gs, om):
    a = np.broadcast_to(np.eye(2), (len(om), 2, 2)).copy().astype(complex)
    for i, g in enumerate(gs[:-1]):
        m = np.zeros((len(om), 2, 2), complex)
        m[:, 0, 0] = m[:, 1, 1] = 1
        if i % 2 == 0:
            m[:, 0, 1] = 1j * om * g          # series inductor, L = g
        else:
            m[:, 1, 0] = 1j * om * g          # shunt capacitor, C = g
        a = a @ m
    den = a[:, 0, 0] + a[:, 0, 1] + a[:, 1, 0] + a[:, 1, 1]   # 1-ohm ends
    return 20 * np.log10(np.abs(2 / den))

om = np.linspace(0.01, 5, 800)
lad_db = proto_s21_db(g_values("chebyshev", 3, 0.5), om)
bb, aa = zpk2tf(*cheb1ap(3, 0.5))
_, h = freqs(bb, aa, om)
print(f"g-ladder sweep vs scipy cheb1ap response: "
      f"max |delta| = {np.max(np.abs(lad_db - 20*np.log10(np.abs(h)))):.2e} dB")

# what the ripple BUYS: same 0.5 dB passband, same order, rejection at the
# homework's mapped stop frequency Omega = 4.294:
om_s = 4.2941
cheb_rej = 10 * np.log10(1 + eps**2 * np.cosh(3 * np.arccosh(om_s)) ** 2)
om_3db = eps ** (-1 / 3)          # butterworth's 3-dB point, band-edge units
butt_rej = 10 * np.log10(1 + (om_s / om_3db) ** 6)
print(f"N=3, 0.5 dB at the band edge, rejection at Omega = {om_s}:")
print(f"  chebyshev  : {cheb_rej:.2f} dB")
print(f"  butterworth: {butt_rej:.2f} dB   <- ripple bought "
      f"{cheb_rej - butt_rej:.1f} dB of stopband")

# %% 3.3 Scale and transform — the 60 MHz IF filter appears
# Impedance scale to 50 ohm, then lowpass -> bandpass: every g becomes a
# RESONATOR tuned to f0 = sqrt(f1 f2). Geometric mean. Not (f1+f2)/2.
F1, F2, R0 = 55e6, 65e6, 50.0
F0 = np.sqrt(F1 * F2)
DELTA = (F2 - F1) / F0
print(f"f0 = sqrt(55 * 65) MHz = {F0/1e6:.4f} MHz   (not 60!)   "
      f"Delta = {DELTA:.4f}")

def bandpass_ladder(gs, f1, f2, r0):
    f0, dl = np.sqrt(f1 * f2), (f2 - f1) / np.sqrt(f1 * f2)
    w0 = 2 * np.pi * f0
    out, series = [], True
    for g in gs[:-1]:
        if series:
            out.append(("series", g * r0 / (dl * w0), dl / (g * r0 * w0)))
        else:
            out.append(("shunt", dl * r0 / (g * w0), g / (dl * r0 * w0)))
        series = not series
    return out

def ladder_s(branches, f_hz, r0=R0):
    w = 2 * np.pi * f_hz
    a = np.broadcast_to(np.eye(2), (len(w), 2, 2)).copy().astype(complex)
    for kind, L, C in branches:
        m = np.zeros((len(w), 2, 2), complex)
        m[:, 0, 0] = m[:, 1, 1] = 1
        if kind == "series":
            m[:, 0, 1] = 1j * w * L + 1 / (1j * w * C)
        else:
            m[:, 1, 0] = 1j * w * C + 1 / (1j * w * L)
        a = a @ m
    den = a[:, 0, 0] + a[:, 0, 1]/r0 + a[:, 1, 0]*r0 + a[:, 1, 1]
    return (a[:, 0, 0] + a[:, 0, 1]/r0 - a[:, 1, 0]*r0 - a[:, 1, 1]) / den, \
        2 / den

cheb3 = bandpass_ladder(g_values("chebyshev", 3, 0.5), F1, F2, R0)
for kind, L, C in cheb3:
    print(f"  {kind:6s} L = {L*1e9:9.3f} nH  C = {C*1e12:9.4f} pF  "
          f"-> resonates {1/(2*np.pi*np.sqrt(L*C))/1e6:.4f} MHz")

f = np.linspace(20e6, 120e6, 8001)
s11, s21 = ladder_s(cheb3, f)
s21_db = 20 * np.log10(np.abs(s21))

def spec_table(tag, s21_db_arr):
    inband = (f >= F1) & (f <= F2)
    print(f"  [{tag}]")
    print(f"    worst passband attenuation = "
          f"{-s21_db_arr[inband].min():7.4f} dB   (spec <= 0.5)")
    print(f"    rejection @ 35 MHz         = "
          f"{-np.interp(35e6, f, s21_db_arr):7.2f} dB   (spec >= 40)")
    print(f"    rejection @ 85 MHz         = "
          f"{-np.interp(85e6, f, s21_db_arr):7.2f} dB   (spec >= 40)")

spec_table("chebyshev N=3, f0 = sqrt(f1 f2)", s21_db)
print("note the asymmetry: 52 dB below, 40.5 dB above -- the ladder is")
print("geometrically symmetric; the spec's +-25 MHz is arithmetic.")

# and the referee: the same ladder swept by scikit-rf's own lumped elements
from skrf.media import DefinedGammaZ0

med = DefinedGammaZ0(frequency=skrf.Frequency.from_f(f, unit="hz"), z0=R0)
net = None
for kind, L, C in cheb3:
    two = (med.inductor(L) ** med.capacitor(C) if kind == "series"
           else med.shunt_inductor(L) ** med.shunt_capacitor(C))
    net = two if net is None else net ** two
print(f"skrf referee: max |dS21| vs our ABCD cascade = "
      f"{np.max(np.abs(net.s[:, 1, 0] - s21)):.2e}")

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(f/1e6, s21_db, label="|S21|")
ax.plot(f/1e6, 20*np.log10(np.abs(s11) + 1e-300), alpha=0.6, label="|S11|")
ax.plot([55, 65], [-0.5]*2, "k-", lw=2.5)
ax.plot([33, 37], [-40]*2, "r-", lw=2.5)
ax.plot([83, 87], [-40]*2, "r-", lw=2.5)
ax.set_xlabel("MHz"); ax.set_ylabel("dB"); ax.set_ylim(-80, 5)
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("hour3_bpf.png", dpi=130)
print("wrote hour3_bpf.png")

# %% 3.4 Group delay — what the steeper filter costs
# Butterworth N=4 sized to the SAME 0.5-dB edges: its omega=1 is the 3-dB
# point, so widen the design band until the 0.5-dB points land on 55/65.
om_half = eps ** (1 / 4)                      # butterworth's 0.5-dB frequency
bw = (F2 - F1) / om_half                      # 13.0 MHz design bandwidth
f2b = (bw + np.sqrt(bw**2 + 4*F0**2)) / 2     # same f0, wider band
f1b = f2b - bw
butt4 = bandpass_ladder(g_values("butterworth", 4), f1b, f2b, R0)
_, s21b = ladder_s(butt4, f)
spec_table("butterworth N=4, 0.5 dB at 55/65", 20*np.log10(np.abs(s21b)))

def gd_ns(s21_arr):
    return -np.gradient(np.unwrap(np.angle(s21_arr)), 2*np.pi*f) * 1e9

for tag, s in [("chebyshev N=3 ", s21), ("butterworth N=4", s21b)]:
    g = gd_ns(s)
    print(f"  {tag}: group delay {np.interp(F0, f, g):6.1f} ns at f0, "
          f"{np.interp(F1, f, g):6.1f} ns at 55 MHz, "
          f"{np.interp(F2, f, g):6.1f} ns at 65 MHz")
print("flat amplitude was never free: the equal-ripple filter pays at the")
print("band edge in DELAY. A 60 ns delay swing across the band smears the")
print("radar's pulse edges -- c * 60 ns / 2 = 9 m of range smear (L14-15).")

fig, ax = plt.subplots(figsize=(8, 4.2))
band = (f >= 45e6) & (f <= 75e6)
ax.plot(f[band]/1e6, gd_ns(s21)[band], label="chebyshev N=3, 0.5 dB")
ax.plot(f[band]/1e6, gd_ns(s21b)[band], label="butterworth N=4")
ax.axvline(55, color="gray", ls="--", alpha=0.5)
ax.axvline(65, color="gray", ls="--", alpha=0.5)
ax.set_xlabel("MHz"); ax.set_ylabel("group delay (ns)")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("hour3_gd.png", dpi=130)
print("wrote hour3_gd.png")

# %% 3.5 Deliberate bug — the arithmetic-mean center
# Same g-values, same formulas, one "obvious simplification": f0 = 60 MHz
# instead of sqrt(55*65) = 59.79 MHz. A 0.35% slip. Watch the spec table.
def bandpass_ladder_bug(gs, f1, f2, r0):
    f0 = (f1 + f2) / 2                        # <- the bug. looks fine.
    dl, w0 = (f2 - f1) / f0, 2 * np.pi * f0
    out, series = [], True
    for g in gs[:-1]:
        if series:
            out.append(("series", g * r0 / (dl * w0), dl / (g * r0 * w0)))
        else:
            out.append(("shunt", dl * r0 / (g * w0), g / (dl * r0 * w0)))
        series = not series
    return out

bug = bandpass_ladder_bug(g_values("chebyshev", 3, 0.5), F1, F2, R0)
_, s21w = ladder_s(bug, f)
print("both spec tables, side by side:")
spec_table("CORRECT: f0 = sqrt(f1 f2) = 59.79 MHz", s21_db)
spec_table("BUG:     f0 = (f1+f2)/2  = 60.00 MHz", 20*np.log10(np.abs(s21w)))
print("the buggy curve LOOKS the same on screen -- centered near 60, nice")
print("skirts, rejections still pass. But its passband slid up: the whole")
print("ripple band sits at 55.21-65.21 MHz, so at 55 MHz you read ~0.97 dB")
print("-- double the ripple budget. The spec edge, not the eyeball, is the")
print("referee. (The homework checker measures every branch's resonance.)")

# %% 3.6 Teaser — the same recipe at 2.4 GHz (why lecture 9 exists)
lad24 = bandpass_ladder(g_values("chebyshev", 3, 0.5),
                        2.4e9 * 0.95, 2.4e9 * 1.05, 50.0)
print("the same three-branch recipe, 10% bandwidth at 2.4 GHz:")
for kind, L, C in lad24:
    print(f"  {kind:6s} L = {L*1e9:8.3f} nH   C = {C*1e12:8.4f} pF")
print("a 0.083 pF series capacitor is smaller than a solder pad's parasitic;")
print("a 0.30 nH shunt inductor is less than one via. The lumped ladder is")
print("over -- same g-values, copper resonators: that is lecture 9.")
