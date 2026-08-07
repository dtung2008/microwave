# %% Lecture 10, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells). Fully deterministic — no RNG.
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c, k

T0 = 290.0
db = lambda x: 10 * np.log10(x)          # noqa: E731  (power ratio -> dB)
undb = lambda x: 10 ** (np.asarray(x, dtype=float) / 10)  # noqa: E731

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401  (skrf unused today — pin check only)

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 The noise vocabulary — kT0B, NF <-> Te, and the 290 K fine print
print(f"kT0 per Hz = {db(k*T0/1e-3):.2f} dBm/Hz    (lecture 1's -174)")
print(f"noise floor, B = 1 MHz: {db(k*T0*1e6/1e-3):.2f} dBm")
print("\nNF <-> Te  (F = 1 + Te/290;  Te = 290*(F-1)):")
for nf in [0.5, 1.0, 1.5, 3.0, 8.0]:
    print(f"  NF = {nf:3.1f} dB  ->  F = {undb(nf):6.4f}  ->  "
          f"Te = {T0*(undb(nf)-1):7.1f} K")
print("fine print: NF 3 dB means Te = 288.6 K — the receiver adds (almost)")
print("exactly as much noise as a 290 K source hands it. The 290 K is a")
print("CONVENTION (IEEE, 1963-ish); a satellite dish staring at 50 K of sky")
print("does not care what we defined — that is why satellite people use Te.")
# Y-factor: how NF is actually measured (hot/cold source, two power readings)
enr_db = 15.0                              # excess noise ratio of the source
t_hot = T0 * (undb(enr_db) + 1.0)          # noise diode ON
te = T0 * (undb(1.5) - 1.0)                # device under test: our 1.5 dB LNA
y = (t_hot + te) / (T0 + te)               # ratio of the two power readings
f_meas = undb(enr_db) / (y - 1.0)
print(f"\nY-factor in one line: ENR 15 dB source -> T_hot = {t_hot:.0f} K;")
print(f"  Y = {y:.4f} ({db(y):.2f} dB)  ->  F = ENR/(Y-1) = {f_meas:.4f}"
      f"  ->  NF = {db(f_meas):.4f} dB (we planted 1.5)")

# %% 3.3 The cascade engine — Friis 1944 in twelve lines, three front-ends
ELEMENTS = {
    "cable": dict(gain_db=-2.0, nf_db=2.0, iip3_dbm=np.inf),
    "lna":   dict(gain_db=20.0, nf_db=1.5, iip3_dbm=-5.0),
    "bpf":   dict(gain_db=-1.5, nf_db=1.5, iip3_dbm=np.inf),
    "mixer": dict(gain_db=-7.0, nf_db=8.0, iip3_dbm=15.0),
    "ifamp": dict(gain_db=30.0, nf_db=4.0, iip3_dbm=10.0),
}

def cascade(names):
    """gain (dB), NF (dB), IIP3 (dBm) of a chain — LINEAR inside, dB at the door."""
    g_run, f_sys, inv_ip3 = 1.0, 1.0, 0.0
    for n in names:
        e = ELEMENTS[n]
        f_sys += (undb(e["nf_db"]) - 1.0) / g_run     # Friis 1944
        inv_ip3 += g_run / undb(e["iip3_dbm"])        # hour 2's cascade
        g_run *= undb(e["gain_db"])
    ip3 = db(1.0 / inv_ip3) if inv_ip3 > 0 else np.inf
    return db(g_run), db(f_sys), ip3

CANDIDATES = {
    "mast LNA   (lna>cable>bpf>mixer>ifamp)": ("lna", "cable", "bpf", "mixer", "ifamp"),
    "shack LNA  (cable>lna>bpf>mixer>ifamp)": ("cable", "lna", "bpf", "mixer", "ifamp"),
    "filter 1st (cable>bpf>lna>mixer>ifamp)": ("cable", "bpf", "lna", "mixer", "ifamp"),
}
for label, names in CANDIDATES.items():
    g, nf, ip3 = cascade(names)
    print(f"{label}: G = {g:.1f} dB, NF = {nf:.4f} dB, IIP3 = {ip3:+.4f} dBm")
print("moving the cable behind the LNA: NF 4.0377 -> 2.3387 = 1.70 dB saved")
print("  (not the full 2.00 — behind 20 dB of gain the cable still costs 0.30)")
print("the war story's chain (filter first): 5.3792 dB — 3.04 dB thrown away\n")

# whose fault is the NF? whose fault is the IP3? (mast chain blame table)
g_run = 1.0
print("blame table, mast chain (F contributions / IIP3 loading):")
for n in ("lna", "cable", "bpf", "mixer", "ifamp"):
    e = ELEMENTS[n]
    f_c = (undb(e["nf_db"]) - 1.0) / g_run if g_run != 1.0 else undb(e["nf_db"])
    inv = g_run / undb(e["iip3_dbm"])
    print(f"  {n:6s}: F term {f_c:6.4f}   1/IIP3 term {inv:7.5f} /mW")
    g_run *= undb(e["gain_db"])
print("-> the LNA dominates BOTH: it saves the noise and spends the linearity.")

# %% 3.4 Two tones meet a cubic — the 3:1 slope, measured
# The LNA as a memoryless cubic: y = x + a3*x^3 with a3 set so IIP3 = -5 dBm.
# Convention: voltage across 50 ohms; P_dbm = 10log10(A^2/0.1) for amplitude A.
iip3_dbm = -5.0
a_ip3_sq = 0.1 * undb(iip3_dbm)            # V^2 at the intercept
a3 = -4.0 / (3.0 * a_ip3_sq)
fs, n = 40.96e6, 4096                      # 10 kHz bins — tones land exactly
f1, f2 = 5.00e6, 5.10e6                    # bins 500, 510
t = np.arange(n) / fs
print(f"a3 = {a3:.2f} /V^2  (from IIP3 = -5 dBm)")
print("drive both tones up in 5 dB steps and watch the spurs take 15:")
levels = [-45.0, -40.0, -35.0, -30.0]
p_f, p_i = [], []
for p_in in levels:
    a = np.sqrt(0.1 * undb(p_in))
    x = a * np.cos(2*np.pi*f1*t) + a * np.cos(2*np.pi*f2*t)
    y = x + a3 * x**3
    s = np.abs(np.fft.rfft(y)) * 2.0 / n
    p_f.append(float(db(s[500]**2 / 0.1)))       # fundamental, f1
    p_i.append(float(db(s[490]**2 / 0.1)))       # IM3 at 2f1-f2 = 4.9 MHz
    print(f"  P_in {p_in:6.1f} dBm: fundamental {p_f[-1]:8.3f} dBm, "
          f"IM3 {p_i[-1]:9.3f} dBm, gap {p_f[-1]-p_i[-1]:7.3f} dB")
slope_f = np.polyfit(levels, p_f, 1)[0]
slope_i = np.polyfit(levels, p_i, 1)[0]
iip3_meas = levels[0] + (p_f[0] - p_i[0]) / 2.0
print(f"measured slopes: fundamental {slope_f:.4f}, IM3 {slope_i:.4f} (the 3:1)")
print(f"extrapolated intercept: {iip3_meas:.4f} dBm — the -5 we planted.")
print("IP3 is a FICTION (nothing survives to the crossing) that predicts")
print(f"REAL spurs: at -30 dBm in, the spur is 2x(-5-(-30)) = 50 dB down.")
print(f"P_1dB sanity: IIP3 - 9.6 = {iip3_dbm-9.6:.1f} dBm input 1-dB point.")

fig, ax = plt.subplots(figsize=(9.5, 4.2))
a = np.sqrt(0.1 * undb(-30.0))
x = a * np.cos(2*np.pi*f1*t) + a * np.cos(2*np.pi*f2*t)
s = np.abs(np.fft.rfft(x + a3 * x**3)) * 2.0 / n
freqs = np.fft.rfftfreq(n, 1/fs) / 1e6
floor = -160.0
ax.plot(freqs, np.maximum(db(s**2 / 0.1 + 1e-30), floor), lw=0.8)
for fx, txt, dx, dy in [(4.9, "2f1-f2", -14, 6), (5.2, "2f2-f1", 14, 6),
                        (5.0, "f1", -6, 6), (5.1, "f2", 6, 6),
                        (15.0, "3f1", -12, 6), (15.3, "3f2", 12, 6),
                        (15.1, "2f1+f2", -16, 16), (15.2, "f1+2f2", 16, 16)]:
    ax.annotate(txt, (fx, float(db(s[int(round(fx*1e6/1e4))]**2/0.1))),
                textcoords="offset points", xytext=(dx, dy), ha="center",
                fontsize=7)
ax.set_ylim(-130, -20)
ax.set_xlim(0, 20)
ax.set_xlabel("frequency (MHz)")
ax.set_ylabel("power (dBm)")
ax.set_title("two tones through x + a3*x^3: IMD moves in next door,"
             " harmonics move far away")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("two_tone.png", dpi=130)
print("wrote two_tone.png  (the close-in spurs are the unfilterable ones)")

# %% 3.5 SFDR — both ceilings on one axis
nf_mast, ip3_mast = 2.3387, -7.3767        # cell 3.3's mast chain
for b in [1e3, 1e6, 1e8]:
    mds = db(k*T0*b/1e-3) + nf_mast
    sfdr = (2.0/3.0) * (ip3_mast - mds)
    print(f"B = {b:9.0e} Hz: MDS = {mds:8.2f} dBm, "
          f"SFDR = {sfdr:6.2f} dB")
print("floor moves 10 dB per decade of B; SFDR only 6.67 — the 2/3 at work.")
print("top of the range: the input where IM3 spurs surface from the floor,")
p_top = (2*ip3_mast + db(k*T0*1e6/1e-3) + nf_mast) / 3.0
print(f"  P_in,max = (2*IIP3 + MDS)/3 = {p_top:.2f} dBm at B = 1 MHz.")

# %% 3.6 Deliberate bug — Friis fed decibels (plausible, wrong, caught)
def cascade_nf_BUGGED(names):
    """Friis's formula with dB numbers used as if linear. DO NOT DO THIS."""
    f_sys, g_run = None, None
    for n in names:
        e = ELEMENTS[n]
        if f_sys is None:
            f_sys, g_run = e["nf_db"], e["gain_db"]
        else:
            f_sys += (e["nf_db"] - 1.0) / g_run
            g_run *= e["gain_db"]
    return f_sys

mast = ("lna", "cable", "bpf", "mixer", "ifamp")
shack = ("cable", "lna", "bpf", "mixer", "ifamp")
print(f"mast chain : bugged NF = {cascade_nf_BUGGED(mast):.4f} dB, "
      f"true = {cascade(mast)[1]:.4f} dB   <- both look plausible!")
print(f"shack chain: bugged NF = {cascade_nf_BUGGED(shack):.4f} dB, "
      f"true = {cascade(shack)[1]:.4f} dB")
print("weak check — 'system NF >= first stage NF':")
print(f"  mast:  bugged 1.6470 >= 1.5  PASSES (the check is too weak to see it)")
print(f"  shack: bugged 1.8470 >= 2.0? no — caught. A lossy first stage helps.")
print("sharp check — a front attenuator must add EXACTLY its loss in dB:")
rest = ("lna", "bpf", "mixer", "ifamp")
d_true = cascade(shack)[1] - cascade(("lna", "bpf", "mixer", "ifamp"))[1]
# careful: shack = cable + (lna bpf mixer ifamp) — same rest chain
d_bug = cascade_nf_BUGGED(shack) - cascade_nf_BUGGED(rest)
print(f"  true engine : NF(cable+rest) - NF(rest) = {d_true:.4f} dB "
      f"(cable loss = 2.0000)")
print(f"  bugged      : {d_bug:.4f} dB — nowhere near 2. The invariant, not")
print("  the plausibility of the answer, is what catches unit crimes.")

# %% 3.7 The stakes — lecture 1's radar engine feels the chain order
RADAR = dict(f_hz=10e9, p_t_w=10e3, g_dbi=33.0, b_hz=1e6,
             nf_db=3.0, loss_db=6.0, snr_req_db=13.0)

def radar_max_range_m(radar, sigma):
    lam = c / radar["f_hz"]
    num = radar["p_t_w"] * undb(2*radar["g_dbi"]) * lam**2 * sigma
    den = ((4*np.pi)**3 * k*T0*radar["b_hz"] * undb(radar["nf_db"])
           * undb(radar["loss_db"]) * undb(radar["snr_req_db"]))
    return (num/den) ** 0.25

for nf, tag in [(3.0, "lecture 1's assumed NF"),
                (2.0378, "best of the 20 orderings"),
                (14.9267, "worst of the 20 orderings")]:
    r = radar_max_range_m(dict(RADAR, nf_db=nf), 0.01)
    print(f"drone range with NF = {nf:7.4f} dB ({tag:24s}): {r/1e3:6.3f} km")
print("same parts, same power, same dish — ordering alone is a factor of 2.10")
print("in detection range. That is the homework: find the order, price it.")
