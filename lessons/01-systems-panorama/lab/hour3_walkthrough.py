# %% Lecture 1, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c, k

T0 = 290.0

# %% 3.1 Setup verification
import scipy, pandas, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__)
print("pandas ", pandas.__version__, " scikit-rf", skrf.__version__)

# %% 3.2 dB warm-up — the five numbers every RF engineer carries
db = lambda x: 10 * np.log10(x)          # noqa: E731  (power ratio -> dB)
undb = lambda x: 10 ** (x / 10)          # noqa: E731

print(f"db(2)      = {db(2):.4f}   (doubling  = +3 dB)")
print(f"db(10)     = {db(10):.4f}  (order of magnitude = +10 dB)")
print(f"db(0.5)    = {db(0.5):.4f}  (halving = -3 dB)")
print(f"kT0 per Hz = {db(k*T0/1e-3):.2f} dBm/Hz   (the -174 every"
      " datasheet quotes)")
print(f"noise floor, B = 1 MHz: {db(k*T0*1e6/1e-3):.2f} dBm")
print(f"noise floor, B = 20 MHz: {db(k*T0*20e6/1e-3):.2f} dBm")
# and the trap, stated now, demonstrated in 3.7:
print("NEVER add two dBm numbers. dBm + dB = dBm. dBm + dBm = nonsense.")

# %% 3.3 The lambda argument — when does a wire stop being a wire?
trace_m = 0.03                            # a 3 cm PCB trace
print(f"a {trace_m*100:.0f} cm trace, in wavelengths:")
for f in [50.0, 1e6, 100e6, 2.4e9, 10e9, 77e9]:
    lam = c / f
    unit = ("Hz", f) if f < 1e3 else ("MHz", f/1e6) if f < 1e9 else ("GHz", f/1e9)
    print(f"  f = {unit[1]:8.1f} {unit[0]:3s}: lambda = {lam:12.4g} m, "
          f"trace = {trace_m/lam:12.4g} lambda")
print("rule of thumb: distributed effects matter past ~lambda/10 ->"
      " at 2.4 GHz your 3 cm trace is already a component.")

# %% 3.4 Friis two ways — dB chain vs watts chain (they must agree exactly)
WIFI = dict(f_hz=2.4e9, p_t_dbm=20.0, g_t_dbi=6.0, g_r_dbi=2.0,
            b_hz=20e6, nf_db=7.0)

def fspl_db(f_hz, r_m):
    return db((4 * np.pi * r_m * f_hz / c) ** 2)

def friis_db_chain(link, r_m):
    p_r = link["p_t_dbm"] + link["g_t_dbi"] + link["g_r_dbi"] \
        - fspl_db(link["f_hz"], r_m)
    noise = db(k * T0 * link["b_hz"] / 1e-3) + link["nf_db"]
    return p_r, p_r - noise

def friis_watts_chain(link, r_m):
    lam = c / link["f_hz"]
    p_t_w = 1e-3 * undb(link["p_t_dbm"])
    density = p_t_w * undb(link["g_t_dbi"]) / (4 * np.pi * r_m ** 2)
    a_eff = undb(link["g_r_dbi"]) * lam ** 2 / (4 * np.pi)
    p_r_w = density * a_eff
    n_w = k * T0 * link["b_hz"] * undb(link["nf_db"])
    return db(p_r_w / 1e-3), db(p_r_w / n_w)

for r in (50, 1000):
    a_dbm, a_snr = friis_db_chain(WIFI, r)
    b_dbm, b_snr = friis_watts_chain(WIFI, r)
    print(f"r = {r:5d} m: dB-chain P_r = {a_dbm:8.2f} dBm, SNR = {a_snr:6.2f} dB"
          f"   | watts-chain agrees to {abs(a_dbm-b_dbm):.1e} dB")
print("two independent implementations, one answer — this is the homework's"
      " referee principle.")

# %% 3.5 The radar equation — three customers and the R^4 tyranny
RADAR = dict(f_hz=10e9, p_t_w=10e3, g_dbi=33.0, b_hz=1e6,
             nf_db=3.0, loss_db=6.0, snr_req_db=13.0)
TARGETS = {"airliner": 40.0, "fighter": 1.0, "drone": 0.01}

def radar_snr_db(radar, sigma, r_m):
    lam = c / radar["f_hz"]
    return (db(radar["p_t_w"]) + 2 * radar["g_dbi"] + db(lam**2) + db(sigma)
            - db((4*np.pi)**3) - db(r_m**4)
            - db(k*T0*radar["b_hz"]) - radar["nf_db"] - radar["loss_db"])

def radar_max_range_m(radar, sigma):
    lam = c / radar["f_hz"]
    num = radar["p_t_w"] * undb(2*radar["g_dbi"]) * lam**2 * sigma
    den = ((4*np.pi)**3 * k*T0*radar["b_hz"] * undb(radar["nf_db"])
           * undb(radar["loss_db"]) * undb(radar["snr_req_db"]))
    return (num/den) ** 0.25

for name, sig in TARGETS.items():
    print(f"{name:8s} sigma = {sig:6.2f} m2 -> "
          f"R_max = {radar_max_range_m(RADAR, sig)/1e3:6.2f} km")
s10 = radar_snr_db(RADAR, 1.0, 10e3)
s20 = radar_snr_db(RADAR, 1.0, 20e3)
print(f"double the range, 10 -> 20 km: SNR falls {s10-s20:.2f} dB"
      " (a one-way link falls 6.02 dB)")
r747 = radar_max_range_m(RADAR, 40.0)
need = (400e3 / r747) ** 4
print(f"seeing the airliner at 400 km instead of {r747/1e3:.1f} km needs"
      f" {need:,.0f}x the power-aperture product. That is why ARSR antennas"
      " are the size of a house.")

# %% 3.6 First contact with scikit-rf — and one honest lesson
from skrf.data import ring_slot
from skrf.media import Freespace
import skrf as rf

print(ring_slot)                       # a real 2-port S-parameter dataset
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
plt.sca(ax[0])
ring_slot.plot_s_db(m=1, n=0)          # |S21| in dB
ring_slot.plot_s_db(m=0, n=0)          # |S11| in dB
plt.sca(ax[1])
ring_slot.plot_s_smith(m=0, n=0)       # lecture 3 will teach this chart
fig.tight_layout()
fig.savefig("ring_slot.png", dpi=130)
print("wrote ring_slot.png  (S-parameters: lecture 4; the chart: lecture 3)")

fs = Freespace(frequency=rf.Frequency(1, 100, 5, "ghz"))
one_km = fs.line(1000, "m")
print("skrf Freespace, 1 km, |S21| =",
      np.round(20*np.log10(np.abs(one_km.s[:, 1, 0])), 6), "dB")
print("-> LOSSLESS. 'Freespace' is a plane-wave MEDIUM; the 1/R^2 spreading"
      " 'loss' is antenna bookkeeping (Friis), not a property of space.")

# %% 3.7 Deliberate bug — the 30 dB lie (dBW fed to a dBm budget)
# The budget wants transmit power in dBm. Someone computes db(10e3) = 40 —
# which is 40 dBW, a perfectly real number — and types it into the dBm slot.
# The chain happily adds it: every term is "just decibels." The result is a
# radar 30 dB better than the one you own.
p_t_dbw = db(RADAR["p_t_w"])
print(f"BUG: p_t = db(10e3) = {p_t_dbw:.1f}  <- this is dBW; the budget"
      " slot wanted dBm (= 70.0)")
bugged = dict(RADAR, p_t_w=RADAR["p_t_w"] * undb(30))   # what the slip claims
r_true = radar_max_range_m(RADAR, 0.01)
r_bug = radar_max_range_m(bugged, 0.01)
print(f"honest drone range:        {r_true/1e3:6.2f} km")
print(f"with the 30 dB unit slip:  {r_bug/1e3:6.2f} km"
      f"   (x{r_bug/r_true:.2f} = 10^(30/40): 30 dB spread over R^4)")
print("the budget LOOKED plausible. dB errors always do. Label every number.")
