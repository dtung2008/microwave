# %% Lecture 16, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells). Run from this lab/ directory —
# the capstone assembles pieces from the course's own homework toolkits,
# here re-exported by hw16_starter.
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hw16_starter import (
    ARRAY, THETA_DEG, TRACK_SCENES, ALERT,
    db, undb, hpbw_deg, wavelength_m, steering_vector, make_snapshots,
    top_peaks_deg, make_frames, alpha_beta_track, cpa_truth,
)

ARR = ARRAY
N = ARR["n"]

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401
import pyargus      # the one new package this lecture uses

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)
print("pyargus imported from", pyargus.__path__[0])
print(f"the array: N = {N}, 77 GHz, d = lambda/2 = {ARR['d_m']*1e3:.4f} mm, "
      f"HPBW = {hpbw_deg(ARR):.2f} deg")

# %% 3.2 The snapshot model, and beamscan written live (it is ~6 lines)
# x = A s + n: hw15 gave us the range-Doppler CELL; today we keep the
# per-element phases across the array — the wavefront. One source at
# -12 deg, 10 dB per element, 64 snapshots.
def sample_cov(x):
    return x @ x.conj().T / x.shape[1]

def beamscan(x, theta_deg):
    r_hat = sample_cov(x)
    a = steering_vector(ARR, np.atleast_1d(theta_deg))     # hw13's phases
    return np.real(np.einsum("ip,ij,jp->p", a.conj(), r_hat, a)) / N**2

x1 = make_snapshots(ARR, [dict(theta_deg=-12.0, p_db=10.0)], 64, seed=1601)
print("snapshots X:", x1.shape, " (16 elements x 64 snapshots)")
p1 = beamscan(x1, THETA_DEG)
pk = top_peaks_deg(THETA_DEG, p1, 1)[0]
print(f"beamscan peak: {pk:+.2f} deg (planted -12.00), reads "
      f"{db(p1.max()):+.2f} dB (planted 10 dB per element)")
print("this is lecture 13's array factor used BACKWARDS: instead of")
print("sending a beam somewhere, we ask which arrival phase-front the")
print("snapshots contain. resolution = the beamwidth, by construction.")

# %% 3.3 MVDR vs beamscan — two close drones, then a jammer (the null on screen)
def mvdr(x, theta_deg, load_db=None):
    r_hat = sample_cov(x)
    if load_db is not None:
        r_hat = r_hat + undb(load_db) * np.eye(N)
    a = steering_vector(ARR, np.atleast_1d(theta_deg))
    b = np.linalg.solve(r_hat, a)                  # R^-1 a, no explicit inverse
    return N / np.real(np.einsum("ip,ip->p", a.conj(), b))

sep = 1.5 * hpbw_deg(ARR)
x2 = make_snapshots(ARR, [dict(theta_deg=-sep/2, p_db=10.0),
                          dict(theta_deg=+sep/2, p_db=10.0)], 64, seed=1620)
pb2, pm2 = beamscan(x2, THETA_DEG), mvdr(x2, THETA_DEG)
print(f"two drones {sep:.2f} deg apart (1.5 beamwidths), 10 dB each:")
print("  beamscan peaks "
      f"{['%+.2f' % t for t in sorted(top_peaks_deg(THETA_DEG, pb2, 2))]} deg")
print("  MVDR     peaks "
      f"{['%+.2f' % t for t in sorted(top_peaks_deg(THETA_DEG, pm2, 2))]} deg")

xj = make_snapshots(ARR, [dict(theta_deg=-10.0, p_db=10.0),
                          dict(theta_deg=+25.0, p_db=50.0)], 64, seed=1601)
pbj, pmj = beamscan(xj, THETA_DEG), mvdr(xj, THETA_DEG)
i_dr = int(np.argmin(np.abs(THETA_DEG - (-10.0))))
print("add the jammer: drone -10 deg / 10 dB, jammer +25 deg / 50 dB:")
print(f"  beamscan at the drone's angle: {db(pbj[i_dr]):+.2f} dB — that is "
      "the JAMMER'S sidelobe floor (~27 dB), the 10 dB drone is under it")
print(f"  MVDR     at the drone's angle: {db(pmj[i_dr]):+.2f} dB — the "
      "adapted null removed the jammer everywhere except at +25 itself")

fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
ax[0].plot(THETA_DEG, db(pb2/pb2.max()), label="beamscan")
ax[0].plot(THETA_DEG, db(pm2/pm2.max()), label="MVDR")
for t in (-sep/2, +sep/2):
    ax[0].axvline(t, color="k", ls=":", alpha=0.5)
ax[0].set_xlim(-25, 25); ax[0].set_ylim(-35, 2)
ax[0].set_title("two drones, 1.5 beamwidths")
ax[1].plot(THETA_DEG, db(pbj), label="beamscan")
ax[1].plot(THETA_DEG, db(pmj), label="MVDR")
ax[1].axvline(-10, color="k", ls=":", alpha=0.5)
ax[1].axvline(25, color="r", ls=":", alpha=0.5)
ax[1].set_xlim(-60, 60)
ax[1].set_title("drone 10 dB at -10, jammer 50 dB at +25")
for a in ax:
    a.set_xlabel("theta (deg)"); a.set_ylabel("dB")
    a.legend(fontsize=8); a.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig("hour3_spectra.png", dpi=130)
print("wrote hour3_spectra.png")

# %% 3.4 Monopulse — lecture 7's comparator, now in software
# Sum beam = uniform weights; difference beam = right half minus left half.
# With this split the discriminant is the IMAGINARY part of Delta/Sigma;
# its slope near boresight turns a ratio into degrees.
sgn = np.concatenate([-np.ones(N//2), np.ones(N//2)])
a0 = steering_vector(ARR, 0.0)
w_sum, w_del = a0, a0 * sgn
dth = 0.2
r = [np.real((w_del.conj() @ steering_vector(ARR, t)) /
             (w_sum.conj() @ steering_vector(ARR, t)) / 1j)
     for t in (-dth, +dth)]
slope_per_deg = (r[1] - r[0]) / (2 * dth)
print(f"monopulse slope: {slope_per_deg:.4f} per deg (calibrated, no noise)")
for th_true in (0.9, 1.7, -2.3):
    x = make_snapshots(ARR, [dict(theta_deg=th_true, p_db=20.0)], 64,
                       seed=1640)
    ratio = np.mean(np.real((w_del.conj() @ x) / (w_sum.conj() @ x) / 1j))
    est = ratio / slope_per_deg
    print(f"  true {th_true:+5.2f} deg -> monopulse {est:+6.3f} deg "
          f"(error {abs(est-th_true):.3f}; HPBW = {hpbw_deg(ARR):.2f})")
print("two beams, one division: angle to a small fraction of the beamwidth —")
print("as long as you stay in the ratio's linear region (watch -2.3).")

# %% 3.5 The capstone pipeline — detect, locate, avoid (one scene, live)
# hw15's pipeline hands us (R, v) per frame (toolkit make_frames); we add
# theta with beamscan, track with the alpha-beta filter, and decide.
frames = make_frames("fast_intruder")
t_s = np.array([f["t_s"] for f in frames])
for tid in TRACK_SCENES["fast_intruder"]["targets"]:
    pos = []
    for f in frames:
        det = next(d for d in f["detections"] if d["track_id"] == tid)
        th = np.radians(top_peaks_deg(THETA_DEG,
                                      beamscan(det["x_snap"], THETA_DEG), 1)[0])
        pos.append((det["r_m"] * np.sin(th), det["r_m"] * np.cos(th)))
    trk = alpha_beta_track(t_s, np.asarray(pos))
    p, v = trk["pos_m"][-1], trk["vel_m_s"][-1]
    t_go = -float(p @ v) / float(v @ v)
    d_cpa = float(np.linalg.norm(p + v * t_go))
    alert = 0.0 < t_go <= ALERT["t_horizon_s"] and d_cpa < ALERT["d_alert_m"]
    tt, dd = cpa_truth("fast_intruder", tid)
    print(f"{tid:14s}: CPA in {t_go:+6.2f} s at {d_cpa:6.2f} m "
          f"-> {'ALERT' if alert else 'no alert':8s} "
          f"| closed-form truth ({tt - t_s[-1]:+6.2f} s, {dd:6.2f} m)")
print("waveform -> channel -> snapshots -> (R, v) -> theta -> track ->")
print("decision: every arrow is a lecture. That is the course.")

# %% 3.6 pyargus cross-check — an independent referee on identical snapshots
from pyargus import directionEstimation as de

align_wl = np.arange(N) * ARR["d_m"] / wavelength_m(ARR["f_hz"])  # [0, 0.5, ...]
sv = de.gen_ula_scanning_vectors(align_wl, 90.0 - THETA_DEG)  # axis-referenced
r_hat = de.corr_matrix_estimate(x1.T, imp="fast")
pk_py = top_peaks_deg(THETA_DEG, np.abs(de.DOA_Bartlett(r_hat, sv)), 1)[0]
pk_us = top_peaks_deg(THETA_DEG, beamscan(x1, THETA_DEG), 1)[0]
print(f"one drone at -12: our beamscan {pk_us:+.2f} deg, pyargus Bartlett "
      f"{pk_py:+.2f} deg -> delta {abs(pk_us-pk_py):.3f} deg")
pk_pyc = top_peaks_deg(THETA_DEG, np.abs(de.DOA_Capon(r_hat, sv)), 1)[0]
pk_usm = top_peaks_deg(THETA_DEG, mvdr(x1, THETA_DEG), 1)[0]
print(f"                  our MVDR    {pk_usm:+.2f} deg, pyargus Capon    "
      f"{pk_pyc:+.2f} deg -> delta {abs(pk_usm-pk_pyc):.3f} deg")
print("(pyargus measures from the array AXIS with cos(theta); feed it")
print(" 90 - theta and the two conventions are the same vector.)")

# %% 3.7 Deliberate bug — MVDR that nulls its own target (K too small)
# The covariance is ESTIMATED. From K = 8 snapshots of a 16-element array,
# R_hat is rank-deficient; MVDR happily "adapts" to noise structure that
# is not there — and the strongest thing in the data, the target itself,
# is what it decides to null.
th_t, i_t = 8.0, int(np.argmin(np.abs(THETA_DEG - 8.0)))
x_many = make_snapshots(ARR, [dict(theta_deg=th_t, p_db=15.0)], 256, seed=1633)
x_few = make_snapshots(ARR, [dict(theta_deg=th_t, p_db=15.0)], 8, seed=1633)
p_many = mvdr(x_many, THETA_DEG)
p_bug = mvdr(x_few, THETA_DEG)                 # the bug: K = 8 < N = 16
p_fix = mvdr(x_few, THETA_DEG, load_db=10.0)   # the fix: diagonal loading
p_scan = beamscan(x_few, THETA_DEG)
print(f"target planted at +8.00 deg, 15 dB; honest MVDR reads "
      f"db(1+N*p) = {db(1 + N*undb(15.0)):.2f} dB")
print(f"  K = 256, unloaded : P(truth) = {db(p_many[i_t]):+8.2f} dB, "
      f"peak {top_peaks_deg(THETA_DEG, p_many, 1)[0]:+.2f} deg")
print(f"  K =   8, unloaded : P(truth) = {db(p_bug[i_t]):+8.2f} dB   "
      "<- the adaptive beamformer NULLED ITS OWN TARGET")
print(f"  K =   8, load 10 dB: P(truth) = {db(p_fix[i_t]):+8.2f} dB, "
      f"peak {top_peaks_deg(THETA_DEG, p_fix, 1)[0]:+.2f} deg   <- restored")
print(f"  K =   8, beamscan : P(truth) = {db(p_scan[i_t]):+8.2f} dB   "
      "(non-adaptive, does not care)")
print(f"  (the K = 8 'power' spectrum even goes NEGATIVE at "
      f"{np.mean(p_bug < 0)*100:.0f}% of angles — a rank-8 R_hat is not a "
      "covariance, and MVDR trusts it anyway)")
fig, ax = plt.subplots(figsize=(8.0, 4.2))
ax.plot(THETA_DEG, db(np.abs(p_bug) + 1e-300), lw=1.0,
        label="MVDR, |K = 8| (the bug)")
ax.plot(THETA_DEG, db(p_fix), lw=1.0, label="MVDR, K = 8 + 10 dB loading")
ax.plot(THETA_DEG, db(p_many), lw=1.0, ls="--", label="MVDR, K = 256")
ax.axvline(th_t, color="k", ls=":", alpha=0.6)
ax.set_xlim(-40, 50); ax.set_ylim(-130, 40)
ax.set_xlabel("theta (deg)"); ax.set_ylabel("MVDR spectrum (dB)")
ax.set_title("too few snapshots: the null lands on the target")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig("hour3_bug.png", dpi=130)
print("wrote hour3_bug.png")
print("adaptivity is a loan against the covariance estimate; K pays it")
print("back. diagonal loading is the honest engineer's collateral.")
