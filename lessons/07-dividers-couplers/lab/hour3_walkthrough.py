# %% Lecture 7, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
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

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 skrf Circuit anatomy — a Wilkinson from lines and one resistor
# The object model: Media makes elements (Networks), Circuit wires them.
# Three facts verified against the installed 1.13.0 wheel, said aloud:
#   1. every network needs a unique, non-empty .name;
#   2. a connection listing >2 nodes is an ideal junction (our input tee);
#   3. external ports appear in the reduced network in the order their Port
#      objects first appear in the connections list — NOT alphabetically.
from skrf.circuit import Circuit
from skrf.media import DefinedGammaZ0

Z0 = 50.0
F0 = 10.0e9
freq = skrf.Frequency(5, 15, 201, "ghz")            # 50 MHz steps; hits 10 GHz
I0 = int(np.argmin(np.abs(freq.f - F0)))            # index of f0, = 100
media = DefinedGammaZ0(frequency=freq, z0=Z0, gamma=1j * freq.w / c)

def tem_line(z_ohm, deg_at_f0, name):
    d_m = (deg_at_f0 / 360.0) * (c / F0)            # meters, referenced to f0
    return media.line(d_m, unit="m", z0=z_ohm, name=name)

def wilkinson(r_iso_ohm=100.0, z_arm_ohm=Z0 * np.sqrt(2), tag="w"):
    p1 = Circuit.Port(freq, name=f"port1_{tag}", z0=Z0)
    p2 = Circuit.Port(freq, name=f"port2_{tag}", z0=Z0)
    p3 = Circuit.Port(freq, name=f"port3_{tag}", z0=Z0)
    arm_a = tem_line(z_arm_ohm, 90.0, f"arm_a_{tag}")
    arm_b = tem_line(z_arm_ohm, 90.0, f"arm_b_{tag}")
    r_iso = media.resistor(r_iso_ohm, name=f"r_iso_{tag}")
    cnx = [[(p1, 0), (arm_a, 0), (arm_b, 0)],       # tee at the input
           [(p2, 0), (arm_a, 1), (r_iso, 0)],
           [(p3, 0), (arm_b, 1), (r_iso, 1)]]
    n = Circuit(cnx).network
    n.name = f"wilkinson_{tag}"
    return n

wilk = wilkinson()
print("assembled a 3-port; S at f0 (rounded):")
print(np.round(wilk.s[I0], 6))
print("-> S11 = 0, S21 = S31 = -j/sqrt(2), S23 = 0: matched at every port,")
print("   3.01 dB split, isolated outputs. Hour 1 said this triple is illegal")
print("   for a LOSSLESS 3-port. Where the loophole is: cell 3.4.")

# %% 3.3 The hand analysis meets the model — even/odd, typed in four lines
# Closed form at f0 (tan(theta) -> infinity taken on paper, NOT numerically),
# for ARBITRARY arm impedance z2 and resistor r — including broken values.
def wilkinson_s0_hand(z2, r, z0=Z0):
    gam_e = (z2**2 - 2 * z0**2) / (z2**2 + 2 * z0**2)   # even: qw into 2*z0
    gam_o = (r - 2 * z0) / (r + 2 * z0)                 # odd: only r/2 left
    s21 = -2j * z0 * z2 / (z2**2 + 2 * z0**2)           # qw two-port, recombined
    return np.array([[gam_e, s21, s21],
                     [s21, (gam_e + gam_o) / 2, (gam_e - gam_o) / 2],
                     [s21, (gam_e - gam_o) / 2, (gam_e + gam_o) / 2]])

for z2, r in [(Z0 * np.sqrt(2), 100.0), (60.0, 100.0), (Z0 * np.sqrt(2), 200.0)]:
    d = np.abs(wilkinson_s0_hand(z2, r) - wilkinson(r, z2, f"t{int(z2)}_{int(r)}").s[I0]).max()
    print(f"z_arm = {z2:6.2f} ohm, R = {r:5.1f} ohm: hand vs Circuit, "
          f"max|dS| = {d:.1e}")
print("-> the algebra and the assembled model agree to float precision,")
print("   even for broken designs. Two independent implementations, one answer.")

# %% 3.4 The Wilkinson swept — and the impossibility theorem as one number
s = wilk.s
db = lambda x: 20 * np.log10(np.maximum(np.abs(x), 1e-16))  # noqa: E731
f_ghz = freq.f / 1e9
match_db, split_db, iso_db = db(s[:, 0, 0]), db(s[:, 1, 0]), db(s[:, 2, 1])

def band_edges(y_db, level_db):
    """Contiguous band around f0 where y_db <= level_db (GHz edges)."""
    ok = y_db <= level_db
    lo = hi = I0
    while lo > 0 and ok[lo - 1]:
        lo -= 1
    while hi < len(ok) - 1 and ok[hi + 1]:
        hi += 1
    return f_ghz[lo], f_ghz[hi]

for label, y in [("input match |S11| <= -20 dB ", match_db),
                 ("isolation   |S23| <= -20 dB ", iso_db)]:
    lo, hi = band_edges(y, -20.0)
    print(f"{label}: {lo:.2f}-{hi:.2f} GHz "
          f"({100 * (hi - lo) / 10.0:.0f}% fractional bandwidth)")
print(f"split at band edges: |S21|(5 GHz) = {split_db[0]:.2f} dB, "
      f"at f0 = {split_db[I0]:.4f} dB")

gram = s[I0].conj().T @ s[I0] - np.eye(3)
print(f"unitarity residual ||S^H S - I|| at f0 = {np.linalg.norm(gram):.6f}")
print("-> 1.0, not 0: the matched, reciprocal, isolated 3-port is NOT")
print("   lossless — the theorem holds; the resistor is the escape hatch.")
print("   (Driven at port 1, balanced and matched: nothing dissipates.")
print("    The deficit lives in rows 2 and 3 — odd-mode/reflected power.)")

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(f_ghz, split_db, label="|S21| split")
ax.plot(f_ghz, match_db, label="|S11| match")
ax.plot(f_ghz, iso_db, label="|S23| isolation")
ax.axhline(-20, color="gray", lw=0.7, alpha=0.6)
ax.axvline(10, color="gray", ls=":", alpha=0.6)
ax.set_xlabel("frequency (GHz)"); ax.set_ylabel("dB"); ax.set_ylim(-60, 0)
ax.set_title("the Wilkinson, swept"); ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig("wilkinson_sweep.png", dpi=130)
print("wrote wilkinson_sweep.png")

# %% 3.5 The branch-line hybrid — 90 degrees, verified; C/D/I, tabulated
def branchline():
    p = [Circuit.Port(freq, name=f"port{k}_bl", z0=Z0) for k in (1, 2, 3, 4)]
    ser12 = tem_line(Z0 / np.sqrt(2), 90.0, "ser12")   # 35.36 ohm series arms
    ser43 = tem_line(Z0 / np.sqrt(2), 90.0, "ser43")
    shn14 = tem_line(Z0, 90.0, "shn14")                # 50 ohm shunt arms
    shn23 = tem_line(Z0, 90.0, "shn23")
    cnx = [[(p[0], 0), (ser12, 0), (shn14, 0)],
           [(p[1], 0), (ser12, 1), (shn23, 0)],
           [(p[2], 0), (ser43, 1), (shn23, 1)],
           [(p[3], 0), (ser43, 0), (shn14, 1)]]
    n = Circuit(cnx).network
    n.name = "branchline"
    return n

bl = branchline()
s0 = bl.s[I0]
print(f"|S21| = {db(s0[1, 0]):.4f} dB, |S31| = {db(s0[2, 0]):.4f} dB, "
      f"phase(S21) - phase(S31) = "
      f"{np.degrees(np.angle(s0[1, 0]) - np.angle(s0[2, 0])):.1f} deg")
print("-> equal 3.01 dB split, exactly 90 degrees apart: the quadrature hybrid.")

print("\nC/D/I read like a datasheet (port 1 in, 3 coupled, 4 isolated):")
print("  f (GHz)   C = -|S31|   D = |S31|-|S41|   I = -|S41|   [dB]")
for fg in (8.0, 9.0, 9.5, 10.0, 10.5, 11.0, 12.0):
    i = int(np.argmin(np.abs(f_ghz - fg)))
    C = -db(bl.s[i, 2, 0]); I = -db(bl.s[i, 3, 0]); D = I - C
    print(f"  {fg:7.1f}   {C:9.2f}   {D:14.2f}   {I:9.2f}")
print("-> I = C + D at every row — isolation is NOT directivity; they differ")
print("   by the coupling. At f0 the ideal model's D and I hit the float floor;")
print("   real microstrip couplers ship with D ~ 15-20 dB. Off f0, watch both die.")

bal_db = np.abs(db(bl.s[:, 1, 0]) - db(bl.s[:, 2, 0]))
ok = bal_db <= 0.5
lo = hi = I0
while lo > 0 and ok[lo - 1]:
    lo -= 1
while hi < len(ok) - 1 and ok[hi + 1]:
    hi += 1
print(f"amplitude balance within 0.5 dB: {f_ghz[lo]:.2f}-{f_ghz[hi]:.2f} GHz "
      f"({100 * (f_ghz[hi] - f_ghz[lo]) / 10.0:.0f}% fractional bandwidth)"
      " — hybrids are narrowband creatures.")

# %% 3.6 The monopulse teaser — Sigma, Delta, and the 180-degree null
# Antenna elements on ports 2 and 3, equal amplitude, relative phase psi
# (the angle-of-arrival proxy). Read port 1 as Sigma, port 4 as Delta.
psi_deg = np.arange(0.0, 360.0, 0.25)
a2 = np.full(psi_deg.shape, 1 / np.sqrt(2), dtype=complex)
a3 = np.exp(1j * np.radians(psi_deg)) / np.sqrt(2)
b_sig = s0[0, 1] * a2 + s0[0, 2] * a3
b_del = s0[3, 1] * a2 + s0[3, 2] * a3
p_sig, p_del = db(b_sig), db(b_del)
i0psi = int(np.argmin(np.abs(psi_deg - 0.0)))
print(f"boresight (psi = 0): Sigma = {p_sig[i0psi]:.4f} dB, "
      f"Delta = {p_del[i0psi]:.4f} dB")
print("-> BOTH at -3 dB. A 90-degree hybrid does not null at boresight —")
print("   expect and welcome that reaction; the homework's Q2 is this moment.")
k = int(np.argmin(p_del))
print(f"Delta null: psi = {psi_deg[k]:.2f} deg, "
      f"depth = {p_del[k] - p_sig[k]:.1f} dB below Sigma")
pa, pb = s0[3, 1] * a2[k], s0[3, 2] * a3[k]
print(f"at the null the two paths into Delta: |{np.abs(pa):.4f}| and "
      f"|{np.abs(pb):.4f}|, "
      f"{np.degrees(np.angle(pa) - np.angle(pb)) % 360:.6f} deg apart")
print("-> equal amplitudes, exactly 180 degrees: that is what a null is made of.")
print("   A rat-race (180-degree hybrid) moves this null to psi = 0 — boresight;")
print("   that is why monopulse comparators are built from 180-degree hybrids.")

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(psi_deg, p_sig, label=r"$\Sigma$ (port 1)")
ax.plot(psi_deg, p_del, label=r"$\Delta$ (port 4)")
ax.axvline(90, color="gray", ls=":", alpha=0.6)
ax.set_xlabel(r"relative phase $\psi$ (deg)")
ax.set_ylabel("output power (dB re incident)")
ax.set_ylim(-80, 3); ax.set_title("monopulse curves, branch-line at f$_0$")
ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig("monopulse_psi.png", dpi=130)
print("wrote monopulse_psi.png")

# %% 3.7 Deliberate bug — the doubled isolation resistor
# A tech "upgrades" the 100 ohm resistor to 200 ohm (bigger is better, no?).
# Even mode never touches the resistor; odd mode sees ONLY the resistor.
sick = wilkinson(r_iso_ohm=200.0, tag="sick")
rows = [("input match  |S11|", 0, 0), ("output match |S22|", 1, 1),
        ("split        |S21|", 1, 0), ("isolation    |S23|", 2, 1)]
print("report card at f0        R = 100 (right)   R = 200 (doubled)")
for label, i, j in rows:
    print(f"  {label}   {db(wilk.s[I0, i, j]):10.2f} dB   "
          f"{db(sick.s[I0, i, j]):10.2f} dB")
print("-> the input match SURVIVES exactly (S11 is pure even mode — no R in")
print("   it at all). Output match and isolation collapse to -15.56 dB =")
print("   20*log10(1/6): Gamma_odd = (200-100)/(200+100) = 1/3, halved twice.")
print("   A one-port bench check at the input would ship this part. The")
print("   report card catches it because it measures the ODD-mode entries.")
