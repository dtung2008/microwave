# %% Lecture 11, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
#
# Uses the homework's own toolkit (hw11_starter) for device loading and the
# L-section builder, and hand-types the physics — exactly the division of
# labor the homework asks of you.
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hw11_starter import (F0_HZ, at, build_amp, db20, demo_device,
                          lsection_for, noise_params_at, the_device)

# %% 3.1 Setup verification + the device
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)
nt, label = the_device()
print("device:", label)
f_hz, s = nt.f, nt.s
i0 = at(f_hz, F0_HZ)
print(f"grid point nearest 2.4 GHz: {f_hz[i0]/1e9:.3f} GHz")
print(f"S at f0:\n{np.round(s[i0], 4)}")

# %% 3.2 The gain zoo at f0 — and why |S21|^2 is none of the three gains
s11, s12, s21, s22 = s[:, 0, 0], s[:, 0, 1], s[:, 1, 0], s[:, 1, 1]
delta = s11 * s22 - s12 * s21
k = (1 - abs(s11) ** 2 - abs(s22) ** 2 + abs(delta) ** 2) / (2 * abs(s12 * s21))
mu = (1 - abs(s11) ** 2) / (abs(s22 - delta * np.conj(s11)) + abs(s12 * s21))

msg = abs(s21 / s12)                                  # maximum stable gain
mag = np.where(k > 1, msg * (k - np.sqrt(np.maximum(k**2 - 1, 0))), msg)
print(f"at f0: K = {k[i0]:.4f}  |Delta| = {abs(delta[i0]):.4f}  "
      f"mu = {mu[i0]:.4f}")
print(f"  |S21|^2      = {db20(s21[i0]):6.3f} dB   <- G_T into 50 ohm, "
      "nothing more")
print(f"  MSG          = {10*np.log10(msg[i0]):6.3f} dB   <- |S21/S12|: "
      "the ceiling AFTER you'd stabilize")
print(f"  MAG (G_Tmax) = {10*np.log10(mag[i0]):6.3f} dB   <- the real "
      "ceiling here, since K > 1")
print("matching can BUY the gap between |S21|^2 and MAG — that gap is "
      f"{10*np.log10(mag[i0]) - db20(s21[i0]):.2f} dB of free, passive gain.")

# %% 3.3 The stability audit — the whole file, not the design frequency
below = mu < 1.0
print(f"mu > 1 (unconditionally stable) at {int((~below).sum())}/{len(mu)} "
      "frequency points")
if below.any():
    i = 0
    while i < len(below):
        if below[i]:
            j = i
            while j + 1 < len(below) and below[j + 1]:
                j += 1
            print(f"  mu < 1 band: {f_hz[i]/1e9:.3f}-{f_hz[j]/1e9:.3f} GHz "
                  f"(worst mu = {mu[i:j+1].min():.3f})")
            i = j + 1
        else:
            i += 1
print(f"worst mu anywhere = {mu.min():.4f} at {f_hz[np.argmin(mu)]/1e9:.3f} "
      f"GHz; mu at f0 = {mu[i0]:.4f}")
print("K-Delta says the same thing at every point:",
      bool((((k > 1) & (abs(delta) < 1)) == (mu > 1)).all()))

fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.semilogx(f_hz / 1e9, mu, label=r"$\mu$")
ax.axhline(1, color="k", ls=":")
ax.axvline(F0_HZ / 1e9, color="tab:green", ls="--", label="$f_0$")
ax.fill_between(f_hz / 1e9, 0, 3, where=below, color="tab:red", alpha=0.15)
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel(r"$\mu$")
ax.set_ylim(0, 2.5)
ax.legend()
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
fig.savefig("walkthrough_mu.png", dpi=130)
print("wrote walkthrough_mu.png")

# %% 3.4 Stability circles — where the danger lives on the chart
iw = int(np.argmin(mu))                                # worst-mu frequency
den_l = abs(s22) ** 2 - abs(delta) ** 2
c_l = np.conj(s22 - delta * np.conj(s11)) / den_l
r_l = abs(s12 * s21 / den_l)
th = np.linspace(0, 2 * np.pi, 361)
fig, ax = plt.subplots(figsize=(5.2, 5.2))
ax.plot(np.cos(th), np.sin(th), "k")
for i, col in [(iw, "tab:red"), (i0, "tab:blue")]:
    ax.plot(c_l[i].real + r_l[i] * np.cos(th),
            c_l[i].imag + r_l[i] * np.sin(th), color=col,
            label=f"load stab. circle {f_hz[i]/1e9:.2f} GHz")
ax.set_aspect("equal")
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("walkthrough_circles.png", dpi=130)
print("wrote walkthrough_circles.png")
print(f"at {f_hz[iw]/1e9:.3f} GHz: |C_L| = {abs(c_l[iw]):.3f}, R_L = "
      f"{r_l[iw]:.3f} -> nearest unstable load sits {abs(abs(c_l[iw])-r_l[iw]):.3f}"
      " from the chart center — that DISTANCE is mu (Edwards-Sinsky).")
print(f"at f0 the circle clears the chart by mu - 1 = {mu[i0]-1:.3f}: "
      "every passive load is safe AT f0.")

# %% 3.5 Gain design at f0 — simultaneous match, target, cascade referee
s1 = s[i0]
S11, S12, S21, S22 = s1[0, 0], s1[0, 1], s1[1, 0], s1[1, 1]
D = S11 * S22 - S12 * S21
b1 = 1 + abs(S11) ** 2 - abs(S22) ** 2 - abs(D) ** 2
b2 = 1 + abs(S22) ** 2 - abs(S11) ** 2 - abs(D) ** 2
c1 = S11 - D * np.conj(S22)
c2 = S22 - D * np.conj(S11)
gms = (b1 - np.sqrt(b1 ** 2 - 4 * abs(c1) ** 2)) / (2 * c1)
gml = (b2 - np.sqrt(b2 ** 2 - 4 * abs(c2) ** 2)) / (2 * c2)
print(f"Gamma_MS = {abs(gms):.4f} at {np.degrees(np.angle(gms)):.1f} deg;  "
      f"Gamma_ML = {abs(gml):.4f} at {np.degrees(np.angle(gml)):.1f} deg")


def gt_db(s1, gs, gl):
    gin = s1[0, 0] + s1[0, 1] * s1[1, 0] * gl / (1 - s1[1, 1] * gl)
    gt = (1 - abs(gs) ** 2) * abs(s1[1, 0]) ** 2 * (1 - abs(gl) ** 2) \
        / (abs(1 - gin * gs) ** 2 * abs(1 - s1[1, 1] * gl) ** 2)
    return 10 * np.log10(gt)


print(f"G_T at the simultaneous match = {gt_db(s1, gms, gml):.4f} dB "
      f"(MAG said {10*np.log10(mag[i0]):.4f})")
amp = build_amp(nt, gms, gml)                         # L-sections ** device
print(f"cascade referee at f0: |S21|^2 of the built amp = "
      f"{db20(amp.s[i0, 1, 0]):.4f} dB")
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot(f_hz / 1e9, db20(amp.s[:, 1, 0]), label="built amp $|S_{21}|^2$")
ax.plot(f_hz / 1e9, db20(s[:, 1, 0]), alpha=0.5, label="bare device")
ax.axvline(F0_HZ / 1e9, color="tab:green", ls="--")
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel("dB")
ax.set_xlim(0, min(f_hz[-1] / 1e9, 8))
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("walkthrough_amp.png", dpi=130)
print("wrote walkthrough_amp.png  (the match is a resonance — L3's lesson)")

# %% 3.6 The noise trade at f0 — Gamma_opt is not Gamma_MS
fmin, gopt, rn = noise_params_at(F0_HZ)


def nf_db(gs):
    ex = 4 * rn * abs(gs - gopt) ** 2 / ((1 - abs(gs) ** 2) * abs(1 + gopt) ** 2)
    return 10 * np.log10(fmin + ex)


print(f"noise model at f0 (instructor-modeled — the .s2p has no noise data):")
print(f"  NF_min = {10*np.log10(fmin):.3f} dB at Gamma_opt = {abs(gopt):.3f} "
      f"at {np.degrees(np.angle(gopt)):.1f} deg;  R_n/Z0 = {rn:.3f}")
print(f"  NF at the gain match Gamma_MS : {nf_db(gms):.3f} dB")
print(f"  NF at 50 ohm (Gamma_S = 0)    : {nf_db(0):.3f} dB")
gout_o = S22 + S12 * S21 * gopt / (1 - S11 * gopt)
gt_opt = gt_db(s1, gopt, np.conj(gout_o))
print(f"  G_T if we sit at Gamma_opt (output re-matched): {gt_opt:.3f} dB "
      f"-> the noise match costs {10*np.log10(mag[i0]) - gt_opt:.3f} dB of "
      "gain. That trade is the whole LNA discipline — and homework module 3.")

# %% 3.7 DELIBERATE BUG — "it's stable at 2.4 GHz, ship it"
# The design frequency is fine: mu(f0) > 1, every passive termination safe.
# The bug: nobody swept mu. This device is conditionally stable in-band
# elsewhere — and "some passive load oscillates" is a promise, not a maybe.
print(f"mu at f0 = {mu[i0]:.3f} > 1  ->  'stable', says the f0-only engineer")
print(f"mu sweep says: worst mu = {mu[iw]:.3f} at {f_hz[iw]/1e9:.3f} GHz")
# construct an explicitly PASSIVE load just inside the unstable region there:
chat = c_l[iw] / abs(c_l[iw])
rad = mu[iw] + 0.15 * (1 - mu[iw])                    # just past the rim
for gtest in (chat * rad, -chat * rad):               # unstable side depends
    gin = s[iw, 0, 0] + s[iw, 0, 1] * s[iw, 1, 0] * gtest \
        / (1 - s[iw, 1, 1] * gtest)
    if abs(gin) > 1:
        print(f"  a passive load |Gamma_L| = {abs(gtest):.3f} at "
              f"{f_hz[iw]/1e9:.3f} GHz makes |Gamma_in| = {abs(gin):.4f} > 1")
        print("  -> the input port shows NEGATIVE RESISTANCE: one reactive"
              " bias tee away from an oscillator, at a frequency your")
        print("     2.4 GHz test bench never looks at. Sweep mu over the"
              " WHOLE file, every design, every time.")
# and the finished amp itself, off frequency:
gl_f = lsection_for(gml, f_hz).flipped().s[:, 0, 0]   # what the output net
gin_f = s11 + s12 * s21 * gl_f / (1 - s22 * gl_f)     # presents vs f
i_bad = int(np.argmax(abs(gin_f)))
ms_f = lsection_for(gms, f_hz).s[:, 1, 1]
gout_f = s22 + s12 * s21 * ms_f / (1 - s11 * ms_f)
j_bad = int(np.argmax(abs(gout_f)))
print(f"  our own finished amp: max |Gamma_in(f)|  = {abs(gin_f[i_bad]):.3f} "
      f"at {f_hz[i_bad]/1e9:.3f} GHz; max |Gamma_out(f)| = "
      f"{abs(gout_f[j_bad]):.3f} at {f_hz[j_bad]/1e9:.3f} GHz")
if max(abs(gin_f[i_bad]), abs(gout_f[j_bad])) > 1:
    print("  -> >1: our 2.4 GHz LNA is a reflection AMPLIFIER out of band."
          " The homework's module 1 exists so you catch this before layout.")
else:
    print("  -> these matchers happen to stay on the passive side — but mu<1"
          " guarantees SOME passive load does not. The audit is not optional.")
