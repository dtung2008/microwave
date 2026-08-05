# %% Lecture 3, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
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

Z0 = 50.0
F0 = 2.4e9
ZL = 36.0 - 21.0j          # lecture 2's antenna, back for its match
LAM0 = c / F0

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)
try:
    import pysmithchart  # noqa: F401
    print("pysmithchart", pysmithchart.__version__, " (optional extra, present)")
except ImportError:
    print("pysmithchart not installed (optional — skrf draws our charts)")

# %% 3.2 The map itself — Gamma is where impedances go to become one number
gamma = lambda z: (z - Z0) / (z + Z0)             # noqa: E731  the bilinear map
gL = gamma(ZL)
print(f"z_L = Z_L/Z0 = {ZL/Z0:.4f}   (normalized: the chart's coordinate)")
print(f"Gamma_L = {gL:.4f} = {abs(gL):.4f} @ {np.degrees(np.angle(gL)):.2f} deg")
print(f"SWR = {(1+abs(gL))/(1-abs(gL)):.4f}, RL = {-20*np.log10(abs(gL)):.2f} dB,"
      f" delivered = {100*(1-abs(gL)**2):.1f}%   (lecture 2's numbers, recovered)")
# the map's whole sales pitch: EVERY passive impedance lands inside |Gamma|<=1
rng = np.random.default_rng(3)
z_random = rng.uniform(0, 500, 4000) + 1j * rng.uniform(-500, 500, 4000)
print(f"4000 random passive impedances: max |Gamma| = "
      f"{np.abs(gamma(z_random)).max():.6f}  -> the right half-plane fits in a disk")
y_L = Z0 / ZL
print(f"y_L = 1/z_L = {y_L:.4f}  (same point, admittance glasses on)")

# %% 3.3 Moving along the line = rotating on the chart (lecture 2, replotted)
def zin_line(z_load, d_lam):
    t = np.tan(2 * np.pi * d_lam)
    return Z0 * (z_load + 1j * Z0 * t) / (Z0 + 1j * z_load * t)

for d in (0.125, 0.25, 0.375):
    print(f"d = {d:5.3f} lam: Z_in = {zin_line(ZL, d):.4f} ohm, "
          f"|Gamma| = {abs(gamma(zin_line(ZL, d))):.6f}  (constant!)")
print(f"d = lam/4 is the inverter: Z0^2/Z_L = {Z0**2/ZL:.4f} ohm — same number")
d_vmin = np.angle(gL) / (4 * np.pi) + 0.25        # first real-axis crossing
d_vmax = d_vmin + 0.25
print(f"voltage MIN at d = {d_vmin:.4f} lam: Z_in = {zin_line(ZL, d_vmin):.4f}"
      f"  (= Z0/SWR = {Z0/1.7976:.2f})")
print(f"voltage MAX at d = {d_vmax:.4f} lam: Z_in = {zin_line(ZL, d_vmax):.4f}"
      f"  (= Z0*SWR = {Z0*1.7976:.2f})")

from skrf.plotting import smith
fig, ax = plt.subplots(figsize=(5.6, 5.6))
smith(ax=ax, draw_labels=True)
dd = np.linspace(0, 0.5, 400)
g_rot = gL * np.exp(-1j * 4 * np.pi * dd)
ax.plot(g_rot.real, g_rot.imag, "-", color="#0f62fe", lw=1.8)
ax.plot(gL.real, gL.imag, "ko", ms=7)
ax.annotate("$z_L$, d=0", (gL.real, gL.imag), textcoords="offset points",
            xytext=(8, -12))
for d, tag in ((0.125, "λ/8"), (0.25, "λ/4"), (d_vmin, "v-min"), (d_vmax, "v-max")):
    g = gL * np.exp(-1j * 4 * np.pi * d)
    ax.plot(g.real, g.imag, "o", color="#b3261e", ms=5)
    ax.annotate(tag, (g.real, g.imag), textcoords="offset points", xytext=(6, 6),
                fontsize=9)
ax.set_title("half a wavelength = one full lap (clockwise toward generator)")
fig.tight_layout()
fig.savefig("hour3_chart.png", dpi=130)
print("wrote hour3_chart.png")

# %% 3.4 The L-section, designed live (R_L < Z0 -> series element at the load)
RL_, XL_ = ZL.real, ZL.imag
w0 = 2 * np.pi * F0
root = np.sqrt(RL_ * (Z0 - RL_))                  # hour 2's closed form
lsec_sols = []
for sgn, name in ((+1, "sol 1"), (-1, "sol 2")):
    X = sgn * root - XL_                          # series reactance, ohm
    B = sgn * np.sqrt((Z0 - RL_) / RL_) / Z0      # shunt susceptance, S
    lsec_sols.append((X, B))
    ser = f"L = {X/w0*1e9:.4f} nH" if X > 0 else f"C = {-1/(w0*X)*1e12:.4f} pF"
    shn = f"C = {B/w0*1e12:.4f} pF" if B > 0 else f"L = {-1/(w0*B)*1e9:.4f} nH"
    z_mid = (ZL + 1j * X) / Z0
    print(f"{name}: X = {X:8.4f} ohm ({ser}), B = {B*1e3:8.4f} mS ({shn}), "
          f"y after series = {1/z_mid:.4f}")
print("both intermediate points sit EXACTLY on the g=1 circle — that is the"
      " whole design:\n  series element -> walk the constant-r circle to g=1;"
      " shunt element -> slide the g=1 circle home.")

# the referee: build sol 1 in scikit-rf and ask for Gamma at f0
import skrf as rf
from skrf.media import DefinedGammaZ0

def media(f_hz):
    frq = rf.Frequency.from_f(np.atleast_1d(f_hz), unit="hz")
    return DefinedGammaZ0(frequency=frq, z0=Z0, gamma=1j * frq.w / c), frq

def gamma_lsec(l_ser_h, c_sh_f, f_hz):
    med, frq = media(f_hz)
    load = med.load(np.tile(gamma(ZL), (frq.npoints, 1, 1)))
    return (med.shunt_capacitor(c_sh_f) ** med.inductor(l_ser_h) ** load).s[:, 0, 0]

L1_H, C1_F = lsec_sols[0][0] / w0, lsec_sols[0][1] / w0
print(f"skrf cascade, sol 1: |Gamma(f0)| = {abs(gamma_lsec(L1_H, C1_F, F0)[0]):.2e}"
      "   <- matched BY CONSTRUCTION, to machine precision")

# %% 3.5 The single shunt stub, designed live (admittance country)
disc = np.sqrt(RL_ * ((Z0 - RL_) ** 2 + XL_**2) / Z0)
stub_sols = []
for sgn, name in ((+1, "sol 1"), (-1, "sol 2")):
    t = (XL_ + sgn * disc) / (RL_ - Z0)
    d = (np.arctan(t) if t >= 0 else np.pi + np.arctan(t)) / (2 * np.pi)
    b = ((RL_**2 * t - (Z0 - XL_ * t) * (XL_ + Z0 * t))
         / (Z0 * (RL_**2 + (XL_ + Z0 * t) ** 2))) * Z0   # normalized b there
    l_open = np.arctan(-b) / (2 * np.pi)
    if l_open < 0:
        l_open += 0.5
    stub_sols.append((d, l_open))
    print(f"{name}: d = {d:.6f} lam ({d*LAM0*1e3:6.2f} mm), y there = 1{b:+.4f}j,"
          f" open stub l = {l_open:.6f} lam ({l_open*LAM0*1e3:6.2f} mm)")

def gamma_stub(d_lam, l_lam, f_hz):
    med, frq = media(f_hz)
    load = med.load(np.tile(gamma(ZL), (frq.npoints, 1, 1)))
    ntwk = (med.shunt_delay_open(l_lam * LAM0, unit="m")
            ** med.line(d_lam * LAM0, unit="m") ** load)
    return ntwk.s[:, 0, 0]

for (d, l), name in zip(stub_sols, ("sol 1", "sol 2")):
    print(f"skrf cascade, {name}: |Gamma(f0)| = {abs(gamma_stub(d, l, F0)[0]):.2e}")

# %% 3.6 Two products, one antenna — the band sweep (2.0-2.8 GHz)
f = np.linspace(2.0e9, 2.8e9, 801)
designs = {
    "L-section 1 (ser L, sh C)": gamma_lsec(L1_H, C1_F, f),
    "stub 1 (d=0.495, open)": gamma_stub(*stub_sols[0], f),
    "stub 2 (d=0.199, open)": gamma_stub(*stub_sols[1], f),
}
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for name, g in designs.items():
    worst = np.abs(g).max()
    print(f"{name:28s}: worst in-band RL = {-20*np.log10(worst):5.2f} dB")
    ax.plot(f / 1e9, -20 * np.log10(np.abs(g)), label=name)
print("the raw load never leaves 10.90 dB — hold that thought for the homework.")
print("count stored energy: L-section = 2 lumped elements; stub 2 carries"
      " 0.28 lam of line;\nstub 1 carries 0.91 lam. More stored energy ="
      " faster phase slope = narrower match.")
ax.axhline(10, color="k", ls=":", lw=1)
ax.axhline(-20 * np.log10(abs(gL)), color="gray", ls="-.", lw=1,
           label="unmatched load")
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel("return loss (dB)")
ax.set_ylim(0, 45)
ax.invert_yaxis()
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
ax.set_title("the price of the match is paid in bandwidth")
fig.tight_layout()
fig.savefig("hour3_band.png", dpi=130)
print("wrote hour3_band.png")

# %% 3.7 Deliberate bug — matching the impedance instead of the admittance
# A shunt stub adds SUSCEPTANCE, so the rotation must stop on the g=1 circle
# (admittance chart). The bug: stop where the IMPEDANCE looks like 1 + jx —
# the r=1 circle — and size the stub to "cancel x". Every step looks
# reasonable. The point is diametrically wrong.
d_bug = 0.245274                    # here z_in/Z0 = 1 + j0.5949 (r=1 circle!)
z_bug = zin_line(ZL, d_bug) / Z0
x_bug = z_bug.imag
l_bug = np.arctan(-x_bug) / (2 * np.pi)   # "cancel x" with an open stub
if l_bug < 0:
    l_bug += 0.5
g_bug = gamma_stub(d_bug, l_bug, F0)[0]
print(f"BUG: rotate to d = {d_bug} lam where z_in = {z_bug:.4f}  <- r = 1! looks"
      " like the rail!")
print(f"     stub l = {l_bug:.6f} lam sized to 'cancel' x = {x_bug:+.4f}")
print(f"     result: |Gamma(f0)| = {abs(g_bug):.4f}, SWR = "
      f"{(1+abs(g_bug))/(1-abs(g_bug)):.3f}, RL = {-20*np.log10(abs(g_bug)):.2f} dB")
print(f"     the UNMATCHED antenna had |Gamma| = {abs(gL):.4f}, SWR = 1.798 —"
      " the 'match' made it WORSE.")
y_at_bug = 1 / z_bug
print(f"     admittance at the bug plane: y = {y_at_bug:.4f} — nowhere near"
      " g = 1.")
print(f"     correct stop (sol 1) is d = {stub_sols[0][0]:.4f} lam ="
      f" d_bug + lam/4: the two planes are DIAMETRICALLY opposite on the chart.")

fig, ax = plt.subplots(figsize=(5.6, 5.6))
smith(ax=ax, draw_labels=True)
th = np.linspace(0, 2 * np.pi, 361)
ax.plot(abs(gL) * np.cos(th), abs(gL) * np.sin(th), "k--", lw=0.8, alpha=0.5)
ax.plot(-0.5 + 0.5 * np.cos(th), 0.5 * np.sin(th), "-", color="#2e7d32", lw=1.2,
        alpha=0.7, label="g = 1 (the real rail)")
ax.plot(0.5 + 0.5 * np.cos(th), 0.5 * np.sin(th), "-", color="#b3261e", lw=1.2,
        alpha=0.7, label="r = 1 (the imposter)")
g_ok = gL * np.exp(-1j * 4 * np.pi * stub_sols[0][0])
g_bad = gL * np.exp(-1j * 4 * np.pi * d_bug)
ax.plot(gL.real, gL.imag, "ko", ms=7)
ax.annotate("$z_L$", (gL.real, gL.imag), textcoords="offset points",
            xytext=(8, -12))
ax.plot(g_ok.real, g_ok.imag, "o", color="#2e7d32", ms=8)
ax.annotate("correct stop (y = 1+jb)\n(0.495λ ≈ a full lap)", (g_ok.real, g_ok.imag),
            textcoords="offset points", xytext=(-30, -34), fontsize=9)
ax.plot(g_bad.real, g_bad.imag, "X", color="#b3261e", ms=10)
ax.annotate("bug stop (z = 1+jx)", (g_bad.real, g_bad.imag),
            textcoords="offset points", xytext=(16, -2), fontsize=9)
ax.plot([g_ok.real, g_bad.real], [g_ok.imag, g_bad.imag], ":", color="gray",
        lw=1)
g_fin = gamma((1 / (y_at_bug + 1j * np.tan(2 * np.pi * l_bug))) * Z0)
ax.plot(g_fin.real, g_fin.imag, "s", color="#b3261e", ms=8)
ax.annotate(f"where the 'match'\nactually ends (|Γ|={abs(g_bug):.2f})",
            (g_fin.real, g_fin.imag), textcoords="offset points",
            xytext=(-118, 14), fontsize=9)
ax.set_title("the impedance imposter: two circles, mirror twins")
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig("hour3_bug.png", dpi=130)
print("wrote hour3_bug.png")
print("moral: a shunt element speaks admittance. Ask 'what does the next"
      " element add?'\nbefore choosing which chart you are standing on.")
