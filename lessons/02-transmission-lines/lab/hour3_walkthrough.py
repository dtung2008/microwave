# %% Lecture 2, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
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
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 The line engine — the whole lecture in twelve lines
RG58 = dict(r_ohm_m=10.0, l_h_m=250e-9, g_s_m=4.5e-4, c_f_m=100e-12)
Z_ANT = 36.0 - 21.0j          # the antenna this course keeps meeting
F0 = 2.4e9

def propagation(line, f):
    zs = line["r_ohm_m"] + 2j * np.pi * f * line["l_h_m"]     # R' + jwL'
    yp = line["g_s_m"] + 2j * np.pi * f * line["c_f_m"]       # G' + jwC'
    return np.sqrt(zs * yp), np.sqrt(zs / yp)                 # gamma, Z0

def z_in(line, zl, ell, f):
    gam, z0 = propagation(line, f)
    t = np.tanh(gam * ell)                                    # lossy tangent
    return z0 * (zl + z0 * t) / (z0 + zl * t)

gam, z0 = propagation(RG58, F0)
print(f"Z0    = {z0:.4f} ohm        (the ratio the line enforces)")
print(f"gamma = {gam:.4f} /m -> alpha = {gam.real*20/np.log(10):.4f} dB/m,"
      f" vp = {2*np.pi*F0/gam.imag:.3g} m/s = 0.667c")
lam = 2 * np.pi / gam.imag
print(f"lambda = {lam*1e3:.2f} mm; a 10 m feed is {10/lam:.1f} wavelengths")
gl = (Z_ANT - 50) / (Z_ANT + 50)
swr = (1 + abs(gl)) / (1 - abs(gl))
print(f"antenna: |Gamma| = {abs(gl):.4f} at {np.degrees(np.angle(gl)):.1f} deg"
      f" -> SWR = {swr:.3f}, RL = {-20*np.log10(abs(gl)):.2f} dB")
print(f"mismatch loss = {-10*np.log10(1-abs(gl)**2):.3f} dB"
      "  (the antenna keeps 92% of what REACHES it)")

# %% 3.3 The referee — skrf DistributedCircuit solves the same RLGC cell
from skrf.media import DistributedCircuit

f_band = np.linspace(2.0e9, 2.8e9, 401)
fr = skrf.Frequency.from_f(f_band, unit="hz")
med = DistributedCircuit(frequency=fr, R=RG58["r_ohm_m"], L=RG58["l_h_m"],
                         G=RG58["g_s_m"], C=RG58["c_f_m"])
gam_b, z0_b = propagation(RG58, f_band)
print("gamma vs skrf:", np.max(np.abs(gam_b - med.gamma) / np.abs(med.gamma)))
print("z0    vs skrf:", np.max(np.abs(z0_b - med.z0) / np.abs(med.z0)))
# z_in of the 10 m feed, two independent routes (tanh vs Gamma-propagation):
zin_me = z_in(RG58, Z_ANT, 10.0, f_band)
refl_l = (Z_ANT - med.z0) / (Z_ANT + med.z0)
refl_in = refl_l * np.exp(-2 * med.gamma * 10.0)
zin_rf = med.z0 * (1 + refl_in) / (1 - refl_in)
print("z_in(10 m) two ways, max rel err:",
      np.max(np.abs(zin_me - zin_rf) / np.abs(zin_rf)))
# and the homework's headline, previewed in one line:
g_in = (z_in(RG58, Z_ANT, 10.0, F0) - 50) / (z_in(RG58, Z_ANT, 10.0, F0) + 50)
print(f"RL at the antenna: 10.90 dB; at the far end of 10 m:"
      f" {-20*np.log10(abs(g_in)):.2f} dB  <- the feed line that lies (hw2)")

# %% 3.4 Standing waves — the pattern that gave SWR its name
beta = 2 * np.pi * F0 / 2e8                           # lossless skeleton's beta
ell = np.linspace(0, 1.5 * lam, 1200)                 # distance from the load
v_env = np.abs(1 + gl * np.exp(-2j * beta * ell))     # |V(ell)| / |V+|
print(f"pattern max/min = {v_env.max():.4f}/{v_env.min():.4f}"
      f" -> ratio {v_env.max()/v_env.min():.4f}   (SWR said {swr:.4f})")
i_min = np.argmin(v_env[:600])
print(f"first minimum at {ell[i_min]/lam:.4f} lambda from the load"
      f" ({ell[i_min]*1e3:.2f} mm) — Z is purely real there (hw2 Q1)")
fig, ax = plt.subplots(figsize=(9, 3.6))
for phi in np.linspace(0, np.pi, 7):                  # time snapshots
    ax.plot(ell / lam, np.real((1 + gl * np.exp(-2j * beta * ell))
                               * np.exp(1j * (phi + beta * ell))),
            color="#0f62fe", alpha=0.25)
ax.plot(ell / lam, v_env, "k", lw=2, label="envelope |V(z)|")
ax.plot(ell / lam, -v_env, "k", lw=2)
ax.set_xlabel("distance from load (wavelengths)")
ax.set_ylabel("V / |V+|")
ax.set_title("the wave moves; the envelope does not — that is 'standing'")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("standing_wave.png", dpi=130)
print("wrote standing_wave.png")

# %% 3.5 The bounce diagram — a digital engineer's 'ringing' is our Gamma
# 10 m of lossless 50-ohm line, 25-ohm source, 150-ohm load, 1 V step.
z0_l, zs, zl = 50.0, 25.0, 150.0
g_s = (zs - z0_l) / (zs + z0_l)                       # -1/3 at the source
g_l = (zl - z0_l) / (zl + z0_l)                       # +1/2 at the load
t1 = 10.0 / 2e8                                       # one-way: 50 ns
v_launch = z0_l / (z0_l + zs)                         # divider at t=0
v_dc = zl / (zl + zs)
print(f"one-way delay {t1*1e9:.0f} ns; launch {v_launch:.4f} V;"
      f" Gamma_s = {g_s:+.3f}, Gamma_L = {g_l:+.3f}; final DC {v_dc:.4f} V")
t_end, v_now, v_load, times, volts = 1000e-9, v_launch, 0.0, [0.0], [0.0]
k = 0
while (2 * k + 1) * t1 < t_end:
    v_load += v_now * (1 + g_l)                       # arrival k at the load
    times += [(2 * k + 1) * t1 * 1e9, (2 * k + 1) * t1 * 1e9]
    volts += [volts[-1], v_load]
    if k < 4:
        print(f"  bounce {k}: t = {(2*k+1)*t1*1e9:4.0f} ns,"
              f" V_load -> {v_load:.4f} V")
    v_now *= g_l * g_s                                # round trip
    k += 1
print(f"  ... -> {v_load:.4f} V; overshoot {(v_launch*(1+g_l)-v_dc)/v_dc:+.1%}"
      " on the first edge. On a scope this is called ringing;"
      " its true name is |Gamma|.")
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.plot(times + [t_end * 1e9], volts + [volts[-1]], color="#0f62fe")
ax.axhline(v_dc, color="k", ls=":", label=f"DC value {v_dc:.3f} V")
ax.set_xlabel("time (ns)")
ax.set_ylabel("load voltage (V)")
ax.set_title("bounce diagram: 10 m line, 25-ohm source, 150-ohm load")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("bounce.png", dpi=130)
print("wrote bounce.png")

# %% 3.6 Deliberate bug — the 3-lambda/4 'transformer' (tan has a period)
# tan(beta*ell) repeats every half wavelength, so if lambda/4 inverts, so
# does 3*lambda/4. Design both, lossless first:
vp = 2e8
theta = np.angle(gl)
spacer = (theta + np.pi) / (2 * (2 * np.pi * F0 / vp))    # to the real plane
r_plane = 50 * (1 - abs(gl)) / (1 + abs(gl))
z_t = np.sqrt(50 * r_plane)
print(f"spacer {spacer*1e3:.3f} mm -> plane {r_plane:.3f} ohm,"
      f" Z_T = {z_t:.3f} ohm")

def fix(line_t, ell_t, f):
    sp = dict(r_ohm_m=0.0, l_h_m=50/vp, g_s_m=0.0, c_f_m=1/(50*vp))
    z1 = z_in(sp, Z_ANT, spacer, f)
    z2 = z_in(line_t, z1, ell_t, f)
    return (z2 - 50) / (z2 + 50)

ideal_t = dict(r_ohm_m=0.0, l_h_m=z_t/vp, g_s_m=0.0, c_f_m=1/(z_t*vp))
lam0 = vp / F0
print(f"LOSSLESS |Gamma(f0)|:  lambda/4 = {abs(fix(ideal_t, lam0/4, F0)):.1e},"
      f"  3lambda/4 = {abs(fix(ideal_t, 3*lam0/4, F0)):.1e}   both 'perfect'")
# now give the transformer the cable's alpha (R' = 2 alpha Z_T):
lossy_t = dict(ideal_t, r_ohm_m=2 * gam.real * z_t)
for name, ell_t in [("lambda/4 ", lam0 / 4), ("3lambda/4", 3 * lam0 / 4)]:
    g0 = abs(fix(lossy_t, ell_t, F0))
    print(f"WITH LOSS {name}: |Gamma(f0)| = {g0:.5f}"
          f" -> RL {-20*np.log10(g0):.2f} dB")
# and the real tax — bandwidth. 20-dB-RL band, contiguous around f0:
f_wide = np.linspace(0.1e9, 4.8e9, 47001)
for name, ell_t in [("lambda/4 ", lam0 / 4), ("3lambda/4", 3 * lam0 / 4)]:
    inside = np.abs(fix(ideal_t, ell_t, f_wide)) <= 10 ** (-20 / 20)
    i0 = np.argmin(np.abs(f_wide - F0))
    lo = hi = i0
    while lo > 0 and inside[lo - 1]:
        lo -= 1
    while hi < len(f_wide) - 1 and inside[hi + 1]:
        hi += 1
    print(f"{name}: 20-dB-RL band = {(f_wide[hi]-f_wide[lo])/1e6:6.1f} MHz"
          f"  ({f_wide[lo]/1e9:.3f}-{f_wide[hi]/1e9:.3f} GHz)")
print("same at f0, HALF the bandwidth, 3x the copper, 3x the loss."
      " The tangent's period is not a free lunch.")
