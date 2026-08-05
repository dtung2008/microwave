# %% Lecture 4, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

Z0 = 50.0                                  # course reference impedance, ohm
F = np.linspace(0.05e9, 3.0e9, 201)        # a VNA-style sweep
W = 2 * np.pi * F
db20 = lambda x: 20 * np.log10(np.abs(x))  # noqa: E731  (voltage-wave -> dB)

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__)
print("scikit-rf", skrf.__version__)

# %% 3.2 The worked two-ports of hours 1-2, as printed numbers
# ABCD builders (every matrix is a (nf,2,2) stack; @ multiplies per frequency)
def abcd_series(z):
    a = np.zeros((len(F), 2, 2), complex)
    a[:, 0, 0] = a[:, 1, 1] = 1.0
    a[:, 0, 1] = z
    return a

def abcd_shunt(y):
    a = np.zeros((len(F), 2, 2), complex)
    a[:, 0, 0] = a[:, 1, 1] = 1.0
    a[:, 1, 0] = y
    return a

def abcd_line(z_line, f0, quarter_waves):
    bl = (np.pi / 2) * quarter_waves * (F / f0)
    a = np.zeros((len(F), 2, 2), complex)
    a[:, 0, 0] = a[:, 1, 1] = np.cos(bl)
    a[:, 0, 1] = 1j * z_line * np.sin(bl)
    a[:, 1, 0] = 1j * np.sin(bl) / z_line
    return a

def abcd_to_s(a, z0=Z0):                    # the homework's module-1 formula
    A, B, C, D = a[:, 0, 0], a[:, 0, 1], a[:, 1, 0], a[:, 1, 1]
    den = A + B / z0 + C * z0 + D
    s = np.empty_like(a)
    s[:, 0, 0] = (A + B / z0 - C * z0 - D) / den
    s[:, 0, 1] = 2 * (A * D - B * C) / den
    s[:, 1, 0] = 2 / den
    s[:, 1, 1] = (-A + B / z0 - C * z0 + D) / den
    return s

i0 = np.argmin(np.abs(F - 1.0e9))           # index of f0 = 1 GHz

pad = np.zeros((len(F), 2, 2), complex)     # matched x1/2 attenuator, by hand
pad[:, 0, 1] = pad[:, 1, 0] = 0.5
print(f"x1/2 pad        : |S11| = 0.000, |S21| = 0.500 = {db20(0.5):.2f} dB, "
      f"|S11|^2+|S21|^2 = {0.25:.4f}  (3/4 of the power DISSIPATED)")

line75 = abcd_to_s(abcd_line(75.0, 1.0e9, 1.0))   # 75-ohm quarter-wave at f0
p_line = abs(line75[i0, 0, 0])**2 + abs(line75[i0, 1, 0])**2
print(f"75-ohm λ/4 line : |S11| = {abs(line75[i0,0,0]):.4f}, "
      f"|S21| = {abs(line75[i0,1,0]):.4f} = {db20(line75[i0,1,0]):.3f} dB, "
      f"|S11|^2+|S21|^2 = {p_line:.4f}  (lossless: the missing power REFLECTED)")

tr = np.zeros((len(F), 2, 2), complex)      # ideal 1:2 transformer: A=1/n, D=n
tr_a = np.zeros((len(F), 2, 2), complex)
tr_a[:, 0, 0] = 0.5
tr_a[:, 1, 1] = 2.0
tr = abcd_to_s(tr_a)
print(f"ideal 1:2 xfmr  : S11 = {tr[i0,0,0].real:+.3f}, "
      f"S21 = {tr[i0,1,0].real:+.3f}, "
      f"|S11|^2+|S21|^2 = {abs(tr[i0,0,0])**2 + abs(tr[i0,1,0])**2:.4f}")
print("two lossless devices with |S21| < 1: mismatch is not dissipation.")
print("NEITHER can have |S21| > 1 — the homework's Q1 asks you to say why.")

# %% 3.3 A real measured file, read with this week's eyes
rs = skrf.data.ring_slot                    # lecture 1 showed you this file
print(rs)
sv = np.linalg.svd(rs.s, compute_uv=False)[:, 0]       # sigma_max per freq
gram = np.conj(np.swapaxes(rs.s, -1, -2)) @ rs.s - np.eye(2)
print(f"reciprocity |S12-S21| max : {np.abs(rs.s - np.swapaxes(rs.s,-1,-2)).max():.2e}"
      "   (a simulation: symmetric to machine zero)")
print(f"sigma_max over the band   : {sv.min():.5f} .. {sv.max():.5f}"
      "   (< 1 everywhere: passive, with ~0.05% margin)")
print(f"unitarity ||S^H S - I||   : {np.linalg.norm(gram, axis=(-2,-1)).max():.4f}"
      "   (NOT lossless: the slot radiates/dissipates)")

# %% 3.4 Conversions, hand-rolled vs the skrf referee (module 1's contract)
from skrf.network import a2s, s2a, s2z, z2s  # noqa: E402

def s_to_abcd(s, z0=Z0):
    s11, s12, s21, s22 = s[:, 0, 0], s[:, 0, 1], s[:, 1, 0], s[:, 1, 1]
    a = np.empty_like(s)
    a[:, 0, 0] = ((1 + s11) * (1 - s22) + s12 * s21) / (2 * s21)
    a[:, 0, 1] = z0 * ((1 + s11) * (1 + s22) - s12 * s21) / (2 * s21)
    a[:, 1, 0] = ((1 - s11) * (1 - s22) - s12 * s21) / (2 * s21) / z0
    a[:, 1, 1] = ((1 - s11) * (1 + s22) + s12 * s21) / (2 * s21)
    return a

def s_to_z(s, z0=Z0):
    eye = np.eye(2)
    return z0 * (np.linalg.inv(eye - s) @ (eye + s))

print("on ring_slot (201 frequencies), worst |delta| vs scikit-rf:")
print(f"  s_to_abcd vs s2a : {np.abs(s_to_abcd(rs.s) - s2a(rs.s, z0=50)).max():.2e}")
print(f"  s_to_z    vs s2z : {np.abs(s_to_z(rs.s) - s2z(rs.s, z0=50)).max():.2e}")
print(f"  round trip a2s(s_to_abcd(S)) - S : "
      f"{np.abs(a2s(s_to_abcd(rs.s), z0=50) - rs.s).max():.2e}")
print("same algebra, two authors, agreement at machine precision — the referee"
      " principle again.")

# %% 3.5 Cascading done right: multiply ABCD, or let skrf ** do it
sec1 = abcd_line(75.0, 1.0e9, 1.0)                      # three mismatched
sec2 = abcd_series(1j * W * 4e-9 + 2.0)                 # sections, chained
sec3 = abcd_shunt(1j * W * 1.5e-12)
mine = abcd_to_s(sec1 @ sec2 @ sec3)                    # ABCD product -> S

freq = skrf.Frequency.from_f(F, unit="hz")
nw = [skrf.Network(frequency=freq, s=abcd_to_s(a), z0=Z0)
      for a in (sec1, sec2, sec3)]
ref = nw[0] ** nw[1] ** nw[2]                           # the ** operator
print(f"3-section chain, |mine - skrf **| max = {np.abs(mine - ref.s).max():.2e}")
print(f"chain |S21| at 1 GHz = {db20(mine[i0,1,0]):.3f} dB")

# %% 3.6 The invariant suite, built live (the homework's module 2)
def is_reciprocal(s, tol=2e-3):
    return bool(np.abs(s - np.swapaxes(s, -1, -2)).max() <= tol)

def unitarity_residual(s):
    gram = np.conj(np.swapaxes(s, -1, -2)) @ s - np.eye(s.shape[-1])
    return float(np.linalg.norm(gram, axis=(-2, -1)).max())

def passivity_residual(s):
    sv_max = np.linalg.svd(s, compute_uv=False)[:, 0]
    return float(max(0.0, (sv_max**2 - 1.0).max()))

iso = np.zeros((len(F), 2, 2), complex)     # ideal isolator: S21=1, S12=0
iso[:, 1, 0] = 1.0
line50 = abcd_to_s(abcd_line(50.0, 1.0e9, 1.0))
print(f"{'network':16s} {'reciprocal':>10s} {'unitarity':>10s} {'passivity':>10s}")
for name, s in [("50-ohm line", line50), ("x1/2 pad", pad),
                ("isolator", iso), ("ring_slot", rs.s)]:
    print(f"{name:16s} {str(is_reciprocal(s)):>10s} "
          f"{unitarity_residual(s):>10.2e} {passivity_residual(s):>10.2e}")
print("three one-number physics tests. The homework aims them at three files"
      " that arrived with claims attached.")

# %% 3.7 Deliberate bug — cascading S by matrix multiplication
# S maps INCIDENT waves to OUTGOING waves at both ports. Stage 1's outgoing
# wave at port 2 is stage 2's incident wave at port 1 — S @ S does not do
# that bookkeeping. ABCD (and the T-matrix) do. Watch it wreck two circuits:
naive_pad = pad[i0] @ pad[i0]
print(f"two x1/2 pads, naive S@S : S21 = {abs(naive_pad[1,0]):.3f}"
      "   <- two attenuators in a row 'transmit nothing'?!")
print(f"correct (ABCD)           : S21 = 0.250 = {db20(0.25):.2f} dB")

lsec = abcd_series(1j * W * 5.3e-9) @ abcd_shunt(1j * W * 2.12e-12)
s_l = abcd_to_s(lsec)                                   # L-section, reciprocal
naive = s_l @ line75                                    # WRONG cascade
right = abcd_to_s(lsec @ abcd_line(75.0, 1.0e9, 1.0))   # right cascade
print(f"L-section + 75-ohm λ/4 line at 1 GHz:")
print(f"  naive S@S  |S21| = {db20(naive[i0,1,0]):7.2f} dB   <- plausible-looking!")
print(f"  ABCD       |S21| = {db20(right[i0,1,0]):7.2f} dB")
print(f"  is_reciprocal(naive) = {is_reciprocal(naive)}   "
      f"(|S12 - S21| max = {np.abs(naive - np.swapaxes(naive,-1,-2)).max():.3f})")
print(f"  is_reciprocal(right) = {is_reciprocal(right)}")
print("two reciprocal passive parts cannot cascade into a non-reciprocal"
      " network — the INVARIANT convicts the algebra even when the number"
      " looks plausible. That is why the homework builds the suite.")

# footnote for the curious: the naive product of two lossless S-matrices is
# still unitary (products of unitary matrices are), so the unitarity check
# alone would MISS this bug. You need the whole suite.

fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot(F / 1e9, db20(right[:, 1, 0]), label="correct cascade (ABCD)")
ax.plot(F / 1e9, db20(naive[:, 1, 0]), "--", label="naive S @ S (wrong)")
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel("|S21| (dB)")
ax.set_title("the same 'cascade', two algebras")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("cascade_bug.png", dpi=130)
print("wrote cascade_bug.png")
