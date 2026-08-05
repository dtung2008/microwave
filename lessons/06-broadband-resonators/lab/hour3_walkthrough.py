# %% Lecture 6, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
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

Z0, ZL = 50.0, 12.5                      # the client's job: 4:1, stepping down
F1, F2, F0 = 2e9, 4e9, 3e9               # the octave; sections are λ/4 at f0

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 One quarter-wave section is narrowband — measure how narrow
def cascade_gamma(z_sections, f, f0=F0, zl=ZL, z0=Z0):
    """Exact ABCD cascade of quarter-wave (at f0) sections -> Gamma(f)."""
    th = np.pi / 2 * np.atleast_1d(f) / f0
    out = np.empty(th.shape, dtype=complex)
    for i, t in enumerate(th):
        abcd = np.eye(2, dtype=complex)
        for z in z_sections:
            abcd = abcd @ np.array([[np.cos(t), 1j * z * np.sin(t)],
                                    [1j * np.sin(t) / z, np.cos(t)]])
        zin = (abcd[0, 0] * zl + abcd[0, 1]) / (abcd[1, 0] * zl + abcd[1, 1])
        out[i] = (zin - z0) / (zin + z0)
    return out

rl = lambda g: -20 * np.log10(np.abs(g))          # noqa: E731

z_single = np.sqrt(Z0 * ZL)                        # 25 ohm — lecture 2's fix
f = np.linspace(1e9, 5e9, 4001)
g1 = cascade_gamma([z_single], f)
inband = (f >= F1) & (f <= F2)
ok = f[rl(g1) >= 20.0]
frac_bw = (ok.max() - ok.min()) / F0
print(f"single λ/4 section ({z_single:.0f} ohm): perfect at f0, but")
print(f"  worst RL over the octave      = {rl(g1[inband]).min():.2f} dB")
print(f"  20-dB fractional bandwidth    = {frac_bw*100:.1f}%")
print(f"  the client wants 20 dB over   = {(F2-F1)/F0*100:.1f}%")
print("one section is ~4x too narrow. More sections, smaller steps.")

# %% 3.3 The Chebyshev designer — ripple theory and the recursion
def cheb_t(n, x):
    x = np.asarray(x, dtype=float)
    ins = np.cos(n * np.arccos(np.clip(x, -1, 1)))
    outs = np.cosh(n * np.arccosh(np.maximum(np.abs(x), 1.0)))
    return np.where(np.abs(x) <= 1, ins, outs) * np.where(x < -1, (-1.)**n, 1.)

theta_m = np.pi / 2 * F1 / F0                     # 60 deg at the band edge
sec_tm = 1 / np.cos(theta_m)                      # = 2 for an octave
a_ln = 0.5 * abs(np.log(ZL / Z0))                 # (1/2)|ln(zl/z0)| = 0.693

def cheb_design(n):
    """Section impedances by the small-reflection recursion (Pozar 5.7)."""
    gm = a_ln / float(cheb_t(n, sec_tm))
    th = np.linspace(0, np.pi, 8 * (n + 4), endpoint=False)
    y = cheb_t(n, sec_tm * np.cos(th))            # expand in cos((n-2k)th)
    basis = np.stack([np.cos((n - 2*k) * th) for k in range(n//2 + 1)], axis=1)
    coef, *_ = np.linalg.lstsq(basis, y, rcond=None)
    g = np.zeros(n + 1)
    for k in range(n // 2 + 1):
        g[k] = gm * coef[k] * (1.0 if n - 2*k == 0 else 0.5)
    for k in range(n + 1):
        g[k] = g[min(k, n - k)]                   # symmetry
    z, sign = [Z0], np.sign(np.log(ZL / Z0))      # steps go DOWN here
    for k in range(n):
        z.append(z[-1] * np.exp(sign * 2 * g[k]))
    return gm, np.array(z[1:])

print(f"theta_m = {np.degrees(theta_m):.0f} deg, sec(theta_m) = {sec_tm:.0f},"
      f"  A = (1/2)|ln(1/4)| = {a_ln:.4f}")
print("N   T_N(2)   ripple Gm   theory RL    sections (ohm)")
for n in (1, 2, 3, 4):
    gm, z = cheb_design(n)
    print(f"{n}  {float(cheb_t(n, sec_tm)):7.0f}   {gm:.5f}   "
          f"{-20*np.log10(gm):6.2f} dB    {np.round(z, 2)}")
print("each extra section multiplies T_N(2) by ~e^1.317 -> buys ~11.4 dB")

# %% 3.4 Sweep the designs — the theory meets an exact cascade (the surprise)
print("N   theory RL   exact swept worst in-band RL     gap")
for n in (1, 2, 3, 4):
    gm, z = cheb_design(n)
    worst = rl(cascade_gamma(z, f[inband])).min()
    print(f"{n}   {-20*np.log10(gm):6.2f} dB     {worst:6.2f} dB"
          f"                {-20*np.log10(gm) - worst:+.2f} dB")
print("theory said N=2 clears 20 dB (20.09). The EXACT cascade of that very")
print("design measures 18.98 dB — the spec is MISSED. Small reflections is")
print("an approximation, and a 4:1 ratio is not a small reflection.")
print("The honest minimum is N=3 (29.44 dB, with margin). ALWAYS sweep.")

# referee: scikit-rf builds the same cascade from Network objects
import skrf as rf
from skrf.media import DefinedGammaZ0

def skrf_gamma(z_sections, f_hz):
    freq = rf.Frequency.from_f(f_hz, unit="hz")
    gam = 1j * 2 * np.pi * freq.f / c
    total = None
    for z in z_sections:
        line = DefinedGammaZ0(frequency=freq, z0=z, gamma=gam).line(
            c / F0 / 4, unit="m")
        line.renormalize(Z0)
        total = line if total is None else total ** line
    load = DefinedGammaZ0(frequency=freq, z0=Z0, gamma=gam).load(
        (ZL - Z0) / (ZL + Z0))
    return (total ** load).s[:, 0, 0]

_, z3 = cheb_design(3)
d = np.abs(np.abs(skrf_gamma(z3, f[inband])) -
           np.abs(cascade_gamma(z3, f[inband]))).max()
print(f"skrf cascade referee (N=3): max |Gamma| delta = {d:.1e}"
      "  — two implementations, one answer")

# %% 3.5 The Bode-Fano budget calculator — is a spec physical?
def bode_fano_best_rl_db(r_ohm, c_farad, f1, f2):
    if c_farad == 0:
        return np.inf
    ln_inv = np.pi / (r_ohm * c_farad * 2 * np.pi * (f2 - f1))
    return 20 * np.log10(np.e) * ln_inv          # = 8.686 * ln(1/Gm)

print("the client's load is 12.5 ohm in parallel with pad capacitance C:")
for c_pf in (0.0, 2.2, 10.0):
    best = bode_fano_best_rl_db(ZL, c_pf * 1e-12, F1, F2)
    tag = ("no ceiling" if np.isinf(best) else
           f"best possible RL = {best:6.2f} dB -> 20 dB spec "
           + ("feasible" if best >= 20 else "IMPOSSIBLE, renegotiate"))
    print(f"  C = {c_pf:4.1f} pF: {tag}")
c_max = np.pi / (ZL * 2 * np.pi * (F2 - F1) * np.log(10 ** (20 / 20)))
print(f"largest C that keeps the spec physical: {c_max*1e12:.3f} pF")
print("no theorem was harmed in module 2: the transformer job is C = 0.")

# %% 3.6 A resonator on the bench — 3-dB Q vs the skrf Qfactor fit
from skrf.qfactor import Qfactor       # NOT rf.Qfactor (deprecated alias)

f0r, q_u, d_coup = 3e9, 500.0, 0.5     # d = |S21(f0)|: the coupling's diameter
q_l_true = q_u * (1 - d_coup)          # loading: Q_L = Q_u(1 - |S21(f0)|)
fr = np.linspace(f0r - 6 * f0r / q_l_true, f0r + 6 * f0r / q_l_true, 801)
x = fr / f0r - f0r / fr
s21 = d_coup / (1 + 1j * q_l_true * x)

mag = np.abs(s21)
i0 = mag.argmax()
half = mag[i0] / np.sqrt(2)
f_lo = np.interp(half, mag[:i0 + 1], fr[:i0 + 1])
f_hi = np.interp(-half, -mag[i0:], fr[i0:])
q_l_3db = fr[i0] / (f_hi - f_lo)
print(f"planted: Q_u = {q_u:.0f}, |S21(f0)| = {d_coup}, so Q_L = {q_l_true:.0f}")
print(f"3-dB method: f0 = {fr[i0]/1e9:.4f} GHz, Q_L = {q_l_3db:.1f}")

ntwk = rf.Network(frequency=rf.Frequency.from_f(fr, unit="hz"),
                  s=s21.reshape(-1, 1, 1), z0=50)
qf = Qfactor(ntwk, res_type="transmission")
res = qf.fit()
print(f"skrf Qfactor (MAT58 NLQFIT6): Q_L = {qf.Q_L:.1f}, "
      f"Q_0 = {qf.Q_unloaded(res, A=1.0):.1f}")

# %% 3.7 Deliberate bug — reporting Q_L as Q_u (the coupling everyone forgets)
print(f"BUG: 'the cavity Q is {q_l_3db:.0f}'  <- this is Q_L, the LOADED Q")
print("     the 3-dB width of |S21| measures the resonator PLUS your probes")
q_u_corr = q_l_3db / (1 - mag[i0])
print(f"FIX: Q_u = Q_L / (1 - |S21(f0)|) = {q_l_3db:.1f} / (1 - {mag[i0]:.2f})"
      f" = {q_u_corr:.1f}")
print(f"     off by exactly the coupling: x{q_u_corr/q_l_3db:.2f} here —")
print("     and x25 for the homework's C_cavity. |S21(f0)| in the formula is")
print("     LINEAR. Feed it dB and you will invent a negative Q.")

# figure for the record
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
for n in (1, 2, 3):
    _, z = cheb_design(n)
    ax[0].plot(f / 1e9, rl(cascade_gamma(z, f)), label=f"N={n}")
ax[0].axhline(20, color="k", ls=":"), ax[0].axvspan(2, 4, alpha=0.08)
ax[0].set(xlabel="f (GHz)", ylabel="RL (dB)", ylim=(0, 50),
          title="one section is narrowband; N=3 buys the octave")
ax[0].legend(), ax[0].grid(alpha=0.3)
ax[1].plot((fr - f0r) / 1e6, 20 * np.log10(np.abs(s21)))
ax[1].axhline(20 * np.log10(half), color="k", ls=":")
ax[1].set(xlabel="detuning (MHz)", ylabel="|S21| (dB)",
          title=f"3-dB width -> Q_L={q_l_3db:.0f}; coupling -> Q_u={q_u_corr:.0f}")
ax[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig("hour3_lecture6.png", dpi=130)
print("wrote hour3_lecture6.png")
