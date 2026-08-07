# %% Lecture 9, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
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
from scipy.optimize import brentq

Z0 = 50.0

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 The Richards map — one tangent, a filter's whole life
# Commensurate lines, all lambda/8 at f_c: theta = 45 deg there, and the
# prototype frequency the stubs actually feel is Omega = tan(theta).
FC = 3e9

def richards_omega(f_hz):
    return np.tan(0.25 * np.pi * np.asarray(f_hz, dtype=float) / FC)

print("f (GHz)   theta (deg)   Omega = tan(theta)   the lumped filter feels")
for f, note in [(0.0, "DC"), (1.5, "mid-passband"), (3.0, "band EDGE (=1)"),
                (4.5, "stopband"), (6.0, "Omega -> inf: atten pole"),
                (9.0, "Omega = -1: edge AGAIN"), (12.0, "Omega = 0: 'DC' again")]:
    om = richards_omega(f * 1e9)
    print(f"  {f:5.1f}     {45*f/3:7.1f}      {om:12.4g}       {note}")
print("tan is periodic -> every commensurate filter repeats. Forever.")

# %% 3.3 The stub lowpass, built live (N=3 chebyshev 0.5 dB at 3 GHz)
# g-values (hw8's engine, compact form) -> Richards -> Kuroda both ends.
def g_cheb(n, ripple_db):
    beta = np.log(1.0 / np.tanh(ripple_db * np.log(10.0) / 40.0))
    gam = np.sinh(beta / (2.0 * n))
    a = np.sin((2.0 * np.arange(1, n + 1) - 1.0) * np.pi / (2.0 * n))
    b = gam**2 + np.sin(np.arange(1, n + 1) * np.pi / n) ** 2
    g = [2.0 * a[0] / gam]
    for k in range(1, n):
        g.append(4.0 * a[k - 1] * a[k] / (b[k - 1] * g[k - 1]))
    return np.array(g + [1.0 if n % 2 else 1.0 / np.tanh(beta / 4.0) ** 2])

g1, g2, g3, _ = g_cheb(3, 0.5)
print(f"g = [{g1:.4f}, {g2:.4f}, {g3:.4f}] -> Richards (normalized):")
print(f"  series short stub {g1:.4f} | shunt open stub {1/g2:.4f} | "
      f"series short stub {g3:.4f}   <- series stubs: UNBUILDABLE")
# Kuroda, one identity per end: UE(1) + SS(g) == Sh((1+g)/g) + UE(1+g)
zs1 = (1 + g1) / g1
zu = 1 + g1
print(f"add UE(1) each end, Kuroda: shunt {zs1:.4f} | UE {zu:.4f} | "
      f"shunt {1/g2:.4f} | UE {zu:.4f} | shunt {zs1:.4f}")
els = [("sh", Z0 * zs1), ("ln", Z0 * zu), ("sh", Z0 / g2),
       ("ln", Z0 * zu), ("sh", Z0 * zs1)]
print("x50 ohm:", "  ".join(f"{k}={z:.2f}" for k, z in els),
      f"  all lambda/8 = {c/(8*FC)*1e3:.2f} mm (ideal line)")

def sweep_stubs(elements, f_hz):
    th = 0.25 * np.pi * np.asarray(f_hz, dtype=float) / FC
    m = None
    for kind, z in elements:
        e = np.zeros(th.shape + (2, 2), dtype=complex)
        if kind == "ln":
            e[..., 0, 0] = e[..., 1, 1] = np.cos(th)
            e[..., 0, 1] = 1j * z * np.sin(th)
            e[..., 1, 0] = 1j * np.sin(th) / z
        elif kind == "sh":
            e[..., 0, 0] = e[..., 1, 1] = 1.0
            e[..., 1, 0] = 1j * np.tan(th) / z
        else:                                   # "ss": series short stub
            e[..., 0, 0] = e[..., 1, 1] = 1.0
            e[..., 0, 1] = 1j * z * np.tan(th)
        m = e if m is None else m @ e
    den = m[..., 0, 0] + m[..., 0, 1] / Z0 + m[..., 1, 0] * Z0 + m[..., 1, 1]
    return 2.0 / den                             # S21

f = np.linspace(0.05e9, 15e9, 7476)
s21 = sweep_stubs(els, f)
s21_db = 20 * np.log10(np.abs(s21) + 1e-300)
i3 = np.argmin(np.abs(f - 3e9))
print(f"|S21| at 3 GHz = {s21_db[i3]:.6f} dB  (equal-ripple edge: -0.5 exactly)")
e2 = 10 ** 0.05 - 1
om = np.abs(richards_omega(f))
cn = np.where(om >= 1, np.cosh(3 * np.arccosh(np.maximum(om, 1))),
              np.cos(3 * np.arccos(np.minimum(om, 1))))
theory = -10 * np.log10(1 + e2 * cn**2)
mask = theory > -80
print(f"vs chebyshev-through-the-map closed form: max |delta| = "
      f"{np.max(np.abs(s21_db - theory)[mask]):.2e} dB")
s21_series = sweep_stubs([("ss", Z0 * g1), ("sh", Z0 / g2), ("ss", Z0 * g3)], f)
print(f"Kuroda check vs the unbuildable series form: "
      f"max ||S21| diff| = {np.max(np.abs(np.abs(s21)-np.abs(s21_series))):.1e}"
      "  <- an identity, not an approximation")
fig, ax = plt.subplots(figsize=(8.5, 4.0))
ax.plot(f / 1e9, np.maximum(s21_db, -80), label="stub LPF (5 elements)")
ax.plot(f[::100] / 1e9, np.maximum(theory[::100], -80), "k.", ms=4,
        label="prototype through tan map")
ax.axvline(3, color="gray", ls=":"), ax.axvline(6, color="gray", ls=":")
ax.set_xlabel("f (GHz)"), ax.set_ylabel("|S21| (dB)")
ax.set_title("exact at every frequency — and periodic at every frequency")
ax.legend(), ax.grid(alpha=0.3)
fig.tight_layout(), fig.savefig("hour3_stub.png", dpi=130)
print("wrote hour3_stub.png   (pole at 6 GHz; passband AGAIN at 9-15 GHz)")

# %% 3.4 Stepped-impedance lowpass — the quick-and-wide workhorse, priced
# Butterworth N=3 at 3 GHz, Zh = 120, Zl = 20: beta*l = g*R0/Zh (series L),
# g*Zl/R0 (shunt C). Short-line approximation — watch what it costs.
ZH, ZL = 120.0, 20.0
gb = np.array([1.0, 2.0, 1.0])
bl = np.array([gb[0] * Z0 / ZH, gb[1] * ZL / Z0, gb[2] * Z0 / ZH])
print(f"electrical lengths at f_c: {np.degrees(bl).round(2)} deg "
      "(the 45.8 deg middle strains 'short line')")

def sweep_stepped(theta_c, zline, f_hz):
    sc = np.asarray(f_hz, dtype=float) / 3e9
    m = None
    for t, z in zip(theta_c, zline):
        th = t * sc
        e = np.zeros(th.shape + (2, 2), dtype=complex)
        e[..., 0, 0] = e[..., 1, 1] = np.cos(th)
        e[..., 0, 1] = 1j * z * np.sin(th)
        e[..., 1, 0] = 1j * np.sin(th) / z
        m = e if m is None else m @ e
    den = m[..., 0, 0] + m[..., 0, 1] / Z0 + m[..., 1, 0] * Z0 + m[..., 1, 1]
    return 2.0 / den

fs = np.linspace(0.05e9, 12e9, 2400)
st_db = 20 * np.log10(np.abs(sweep_stepped(bl, [ZH, ZL, ZH], fs)) + 1e-300)
i3s = np.argmin(np.abs(fs - 3e9))
i6s = np.argmin(np.abs(fs - 6e9))
print(f"at 3 GHz: {st_db[i3s]:.2f} dB (true butterworth: -3.01); "
      f"3-dB point lands at {fs[st_db <= -3.0103].min()/1e9:.3f} GHz")
print(f"at 6 GHz: {-st_db[i6s]:.2f} dB vs true butterworth "
      f"{10*np.log10(1+2.0**6):.2f} dB  <- the approximation's stopband tax")

# Now the copper: widths on RO4350B (hw5's board) and skrf MLine physics.
ER, H = 3.48, 0.508e-3

def eps_eff_u(u):
    return (ER + 1) / 2 + (ER - 1) / 2 / np.sqrt(1 + 12 / u)

def z0_u(u):
    ee = eps_eff_u(u)
    if u <= 1:
        return 60 / np.sqrt(ee) * np.log(8 / u + u / 4)
    return 120 * np.pi / (np.sqrt(ee) * (u + 1.393 + 0.667 * np.log(u + 1.444)))

def u_for(z):
    return brentq(lambda u: z0_u(u) - z, 1e-3, 40.0, xtol=1e-12)

from skrf.media import MLine

widths = [u_for(z) * H for z in (ZH, ZL, ZH)]
print(f"widths: Zh=120 -> w = {widths[0]*1e3:.4f} mm (mind your fab's minimum"
      f" trace!), Zl=20 -> w = {widths[1]*1e3:.4f} mm")
freq = skrf.Frequency(0.2, 12, 236, "ghz")
net = None
lens = []
for w, z, t in zip(widths, (ZH, ZL, ZH), bl):
    ml = MLine(frequency=freq, w=w, h=H, t=35e-6, ep_r=ER, tand=0.0037,
               rho=1.68e-8, model="hammerstadjensen", disp="kirschningjansen",
               f_epr_tand=3e9)
    i3m = np.argmin(np.abs(freq.f - 3e9))
    beta_fc = np.real(ml.beta[i3m])
    lens.append(t / beta_fc)
    piece = ml.line(t / beta_fc, unit="m")
    piece.renormalize(Z0)
    net = piece if net is None else net ** piece
ml_db = 20 * np.log10(np.abs(net.s[:, 1, 0]) + 1e-300)
print(f"physical lengths: {[f'{ln*1e3:.3f}' for ln in lens]} mm")
print(f"MLine-physics 3-dB point: {freq.f[ml_db <= -3.0103].min()/1e9:.3f} GHz"
      " (finite thickness + dispersion move it again — quote, don't guess)")
fig, ax = plt.subplots(figsize=(8.5, 4.0))
ax.plot(fs / 1e9, np.maximum(st_db, -60), label="ideal-line stepped LPF")
ax.plot(freq.f / 1e9, np.maximum(ml_db, -60), label="same copper in skrf MLine")
ax.plot(fs / 1e9, np.maximum(-10 * np.log10(1 + (fs/3e9)**6), -60), "k--",
        alpha=0.5, label="true butterworth")
ax.axvline(3, color="gray", ls=":")
ax.set_xlabel("f (GHz)"), ax.set_ylabel("|S21| (dB)")
ax.set_title("stepped-impedance: fast to design, honest about neither skirt nor cutoff")
ax.legend(fontsize=9), ax.grid(alpha=0.3)
fig.tight_layout(), fig.savefig("hour3_stepped.png", dpi=130)
print("wrote hour3_stepped.png")

# %% 3.5 The coupled-line bandpass — the synthesis chain, end to end
# N=3, 0.5 dB, 10% at 2.4 GHz on RO4350B: g -> J -> (Z0e, Z0o) -> (w, s, l).
F0 = 2.4e9
DELTA = 0.10
gs = np.concatenate([[1.0], g_cheb(3, 0.5)])          # g0..g4
jz = np.zeros(4)
jz[0] = np.sqrt(0.5 * np.pi * DELTA / (gs[0] * gs[1]))
jz[1] = 0.5 * np.pi * DELTA / np.sqrt(gs[1] * gs[2])
jz[2] = 0.5 * np.pi * DELTA / np.sqrt(gs[2] * gs[3])
jz[3] = np.sqrt(0.5 * np.pi * DELTA / (gs[3] * gs[4]))
z0e = Z0 * (1 + jz + jz**2)
z0o = Z0 * (1 - jz + jz**2)
print("section  J*Z0      Z0e       Z0o      (Pozar Ex 8.8's table, at our f0)")
for i in range(4):
    print(f"   {i+1}    {jz[i]:.4f}  {z0e[i]:8.4f}  {z0o[i]:8.4f}")

def coupled_abcd(ze, zo, te, to):
    se, ce, so, co = np.sin(te), np.cos(te), np.sin(to), np.cos(to)
    den = ze * so - zo * se
    m = np.zeros(np.shape(te) + (2, 2), dtype=complex)
    m[..., 0, 0] = m[..., 1, 1] = (ze * ce * so + zo * co * se) / den
    m[..., 1, 0] = 2j * se * so / den
    m[..., 0, 1] = 0.5j * ((ze**2 + zo**2) * se * so
                           - 2 * ze * zo * (1 + ce * co)) / den
    return m

def sweep_coupled(f_hz, ratio_eo=(1.0, 1.0)):
    th = 0.5 * np.pi * np.asarray(f_hz, dtype=float) / F0
    m = None
    for ze, zo in zip(z0e, z0o):
        e = coupled_abcd(ze, zo, th * ratio_eo[0], th * ratio_eo[1])
        m = e if m is None else m @ e
    den = m[..., 0, 0] + m[..., 0, 1] / Z0 + m[..., 1, 0] * Z0 + m[..., 1, 1]
    return 2.0 / den

fb = np.linspace(0.1e9, 10e9, 4951)
sb = sweep_coupled(fb)
sb_db = 20 * np.log10(np.abs(sb) + 1e-300)
i0 = np.argmin(np.abs(fb - F0))
band = (fb >= 2.28e9) & (fb <= 2.52e9)
ok = -sb_db <= 0.5
lo = fb[np.where(~ok & (fb < F0))[0].max() + 1]
hi = fb[np.where(~ok & (fb > F0))[0].min() - 1]
print(f"IL at f0 = {-sb_db[i0]:.4f} dB; worst atten in the design band = "
      f"{(-sb_db[band]).max():.4f} dB")
print(f"measured 0.5-dB band: {lo/1e9:.3f}-{hi/1e9:.3f} GHz = "
      f"{(hi-lo)/F0*100:.2f}% (designed 10% — the narrowband mapping's fee)")
# dimensions on the course board
for i in range(4):
    tse, tso = u_for(z0e[i] / 2), u_for(z0o[i] / 2)

    def w_of_s(s_h, target=tse):
        return brentq(lambda w_h: (2/np.pi)*np.arccosh(
            (2*np.cosh(np.pi*w_h + np.pi*s_h/2) - np.cosh(np.pi*s_h/2) + 1)
            / (np.cosh(np.pi*s_h/2) + 1)) - target, 1e-4, 40.0)

    def resid(s_h):
        w_h = w_of_s(s_h)
        g_ = np.cosh(np.pi*s_h/2)
        d_ = np.cosh(np.pi*w_h + np.pi*s_h/2)
        return ((2/np.pi)*np.arccosh((2*d_ - g_ - 1)/(g_ - 1))
                + (4/(np.pi*(1 + ER/2)))*np.arccosh(1 + 2*w_h/s_h)) - tso

    s_h = brentq(resid, 1e-3, 20.0)
    w_h = w_of_s(s_h)
    ln = c / (4 * F0 * np.sqrt(eps_eff_u(w_h)))
    print(f"  section {i+1}: w = {w_h*H*1e3:.4f} mm  s = {s_h*H*1e3:.4f} mm  "
          f"l = {ln*1e3:.3f} mm   (Akhtarzad quasi-static — a starting point,"
          " not a tapeout)")

# %% 3.6 The openEMS case study — ideal model meets 'reality'
# openEMS is instructor-run only. This cell post-processes WHATEVER Touchstone
# sits at CASE_FILE; absent the export it builds a LOUDLY-LABELED placeholder:
# the ideal model re-swept with even/odd eps_eff split +-3% (odd mode lives
# more in air -> runs faster) and +2% dispersion — documented physics, NOT a
# field solution.
import os

CASE_FILE = "openems_coupled_bpf.s2p"
if os.path.exists(CASE_FILE):
    case = skrf.Network(CASE_FILE)
    src = f"instructor openEMS export ({CASE_FILE})"
else:
    re_, ro_ = np.sqrt(1.02 * 1.03), np.sqrt(1.02 * 0.97)
    sc = sweep_coupled(fb, ratio_eo=(re_, ro_))
    s4 = np.zeros((len(fb), 2, 2), dtype=complex)  # |S21| story only here;
    s4[:, 0, 1] = s4[:, 1, 0] = sc                 # hw9's loader ships full S
    case = skrf.Network(frequency=skrf.Frequency.from_f(fb, unit="hz"),
                        s=s4, z0=Z0)
    src = "PLACEHOLDER (ideal + documented eps_eff perturbation — NOT field-solved)"
print(f"case study source: {src}")
cs_db = 20 * np.log10(np.abs(case.s[:, 1, 0]) + 1e-300)
fc_ = case.frequency.f

def c3db(f_, s_db_, lo_, hi_):
    w = (f_ >= lo_) & (f_ <= hi_)
    okk = f_[w][s_db_[w] >= s_db_[w].max() - 3.0]
    return 0.5 * (okk.min() + okk.max())

print(f"passband center (-3 dB midpoint): ideal {c3db(fb, sb_db, 2e9, 3e9)/1e9:.4f}"
      f" GHz -> case {c3db(fc_, cs_db, 2e9, 3e9)/1e9:.4f} GHz")
i0c = np.argmin(np.abs(fc_ - F0))
print(f"|S21| at 2.4 GHz: ideal {sb_db[i0]:.3f} dB -> case {cs_db[i0c]:.3f} dB")
w2i = (fb > 4.2e9) & (fb < 5.4e9)
w2c = (fc_ > 4.2e9) & (fc_ < 5.4e9)
print(f"worst |S21| near 2f0: ideal {sb_db[w2i].max():.1f} dB -> case "
      f"{cs_db[w2c].max():.1f} dB  <- the ideal zero was a promise the modes"
      " could not keep")
fig, ax = plt.subplots(figsize=(8.5, 4.0))
ax.plot(fb / 1e9, np.maximum(sb_db, -80), label="ideal")
ax.plot(fc_ / 1e9, np.maximum(cs_db, -80), alpha=0.7, label=f"case: {src[:24]}")
ax.set_xlabel("f (GHz)"), ax.set_ylabel("|S21| (dB)")
ax.set_title("the ideal-vs-EM gap (same post-processing, any Touchstone)")
ax.legend(fontsize=9), ax.grid(alpha=0.3)
fig.tight_layout(), fig.savefig("hour3_case.png", dpi=130)
print("wrote hour3_case.png")

# %% 3.7 Deliberate bug — victory declared at 2f0
# The system spec: >= 40 dB rejection everywhere above 3.2 GHz. Sweep the
# finished 2.4 GHz filter to 4.8 GHz (= 2f0), like a reasonable person who
# read the datasheet template and not the physics.
f_bug = fb[fb <= 4.8e9]
bug_db = sb_db[fb <= 4.8e9]
above = f_bug >= 3.2e9
print(f"BUG sweep 0.1-4.8 GHz: worst rejection above 3.2 GHz = "
      f"{-bug_db[above].max():.1f} dB, and it only deepens with f")
print("  'meets 40 dB everywhere above 3.2 GHz — ship it.'")
full = fb >= 3.2e9
print(f"full sweep to 10 GHz: worst rejection above 3.2 GHz = "
      f"{-sb_db[full].max():.1f} dB at {fb[full][np.argmax(sb_db[full])]/1e9:.2f}"
      " GHz  <- a SECOND PASSBAND, wide open, 2.4 GHz beyond the bug's sweep")
print("theta(7.2 GHz) = 270 deg = 90 + 180: the coupled sections cannot tell"
      " the difference. Commensurate filters are periodic — sweep past 3f0,"
      " always.")
fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.0), sharey=True)
axs[0].plot(f_bug / 1e9, np.maximum(bug_db, -80))
axs[0].set_title("the sweep that 'passed' (stops at 2f0)")
axs[1].plot(fb / 1e9, np.maximum(sb_db, -80), color="C3")
axs[1].axvline(7.2, color="gray", ls="--")
axs[1].set_title("the same filter, swept honestly")
for a in axs:
    a.set_xlabel("f (GHz)"), a.grid(alpha=0.3)
axs[0].set_ylabel("|S21| (dB)")
fig.tight_layout(), fig.savefig("hour3_bug.png", dpi=130)
print("wrote hour3_bug.png")
