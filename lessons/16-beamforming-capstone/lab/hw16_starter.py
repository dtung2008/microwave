"""Homework 16 starter — Detect, locate, avoid (the capstone).

You implement the three modules marked TODO below. Everything else is the
toolkit: the 77 GHz corridor array, the snapshot simulator, the per-frame
(R, v) detections in homework 15's conventions, the alpha-beta filter, the
pyargus referee hookup, and the checker.

Run from this directory:

    python hw16_starter.py --check    # measured facts per module (the instrument)
    python hw16_starter.py --plot     # the four pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` is a decibel quantity; `*_m`, `*_s`,
`*_m_s`, `*_hz` are SI; `*_deg` / `*_rad` label every angle (lecture 13's
felony — np.sin eats radians). Angles theta are measured FROM BROADSIDE
(the corridor axis), positive toward +x. Velocity sign convention (hw15,
restated): v is the RANGE RATE — positive = receding, negative = closing.
Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
import zlib

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s

# ----------------------------------------------------------------------------
# The systems (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
def wavelength_m(f_hz):
    """Free-space wavelength lambda = c / f.  (Mirrors hw1's toolkit.)"""
    return C_M_S / np.asarray(f_hz, dtype=float)


# The corridor guard: homework 15's 77 GHz sensor grows the receive array it
# always deserved — a 16-element ULA (uniform linear array), d = lambda/2,
# element n at x = n*d (hw13's geometry, verbatim). Same N as homework 13's
# X-band aperture; at 77 GHz the whole array is 29 mm across.
ARRAY = dict(
    f_hz=77e9,                          # W-band, lambda = 3.8934 mm
    n=16,                               # element count
    d_m=wavelength_m(77e9) / 2.0,       # element spacing, m (= lambda/2)
)

# Uniform-ULA half-power beamwidth at broadside (hw13's closed form; the
# resolution ruler for the whole homework): 6.34 deg for this array.
X_HALF_POWER = 1.39155738     # solves sin(x)/x = 1/sqrt(2)  (hw13's constant)


def hpbw_deg(arr=ARRAY):
    """Broadside half-power beamwidth, closed form (mirrors hw13's referee)."""
    du = X_HALF_POWER * wavelength_m(arr["f_hz"]) / (np.pi * arr["n"] * arr["d_m"])
    return float(2.0 * np.degrees(np.arcsin(du)))


# The course DOA grid: 0.02 deg steps, +/-90 deg. Fine enough that grid
# quantization (0.01 deg worst case) is invisible against the 0.5 deg
# success criterion.
THETA_DEG = np.arange(-90.0, 90.0 + 1e-9, 0.02)

# The DOA scenes (module 1). Powers are per-element SNR in dB (noise power
# = 1 per element). Separation 1.5 beamwidths = 9.52 deg, placed symmetric
# about broadside. The jammer is a wideband noise source 40 dB above the
# drone — it lands in EVERY range-Doppler cell (that is what makes it a
# jammer and not a target).
_SEP_DEG = 1.5 * hpbw_deg()
DOA_SCENES = dict(
    one_drone=[dict(theta_deg=-12.0, p_db=10.0)],
    two_drones=[dict(theta_deg=-_SEP_DEG / 2, p_db=10.0),
                dict(theta_deg=+_SEP_DEG / 2, p_db=10.0)],
    jammer=[dict(theta_deg=-10.0, p_db=10.0),      # the drone
            dict(theta_deg=+25.0, p_db=50.0)],     # the jammer (+40 dB)
)
N_SNAP = 64            # snapshots per DOA estimate (module 1's default)

# The avoidance contract (module 3): alert when the closest point of
# approach comes inside D_ALERT within the next T_HORIZON.
ALERT = dict(d_alert_m=30.0, t_horizon_s=20.0)

# The three guarded-corridor scenes (module 2+3). The sensor sits at the
# origin looking down the corridor (+y = boresight, theta toward +x).
# Trajectories are straight lines at constant velocity — so the CPA
# (closest point of approach) referee is CLOSED FORM, exact by construction.
# Each target: start position (x, y) m, velocity (vx, vy) m/s, per-element
# snapshot SNR dB. 16 frames, 0.25 s apart (a 3.75 s look); every CPA lies
# BEYOND the last frame, so the decision is always a prediction.
N_FRAMES, DT_S = 16, 0.25
JAMMER_DEG, JAMMER_DB = 25.0, 50.0          # scene-3 jammer (fixed bearing)
TRACK_SCENES = dict(
    crossing_drones=dict(
        jammer=False,
        targets=dict(
            drone_a=dict(p0_m=(-45.0, 40.0), v_m_s=(9.0, -3.0), snr_db=10.0),
            drone_b=dict(p0_m=(50.0, 80.0), v_m_s=(-6.0, -2.0), snr_db=10.0),
        )),
    fast_intruder=dict(
        jammer=False,
        targets=dict(
            fixed_wing=dict(p0_m=(30.0, 190.0), v_m_s=(-9.0, -38.0),
                            snr_db=13.0),
            leaving_drone=dict(p0_m=(-20.0, 90.0), v_m_s=(2.0, 5.0),
                               snr_db=10.0),
        )),
    jammed_crossing=dict(
        jammer=True,
        targets=dict(
            drone_j=dict(p0_m=(-45.0, 55.0), v_m_s=(11.0, -8.0), snr_db=10.0),
        )),
)

# Measurement noise on the provided (R, v) detections (the hw15 pipeline's
# job, done for you): sub-bin range interpolation leaves ~0.15 m, Doppler
# ~0.10 m/s. The ANGLE is not provided — that is your module 1's job.
R_NOISE_M, V_NOISE_M_S = 0.15, 0.10


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> decibels (re-provided each lecture; course rule)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """Decibels -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def steering_vector(arr, theta_deg):
    """Steering vector(s) a(theta) of the ULA — hw13's array-factor phase
    as a COLUMN vector: element n at x = n*d contributes
    exp(+j*k*d*n*sin(theta)). Returns shape (n,) for a scalar angle,
    (n, len(theta)) for a vector of angles. The whole snapshot model rests
    on this convention; the pyargus referee is mapped onto the same one.
    """
    k = 2.0 * np.pi / wavelength_m(arr["f_hz"])
    n_idx = np.arange(arr["n"])
    th = np.radians(np.asarray(theta_deg, dtype=float))
    a = np.exp(1j * k * arr["d_m"] * np.outer(n_idx, np.sin(th)))
    return a[:, 0] if np.isscalar(theta_deg) else a


def make_snapshots(arr, sources, n_snap=N_SNAP, seed=1601):
    """The snapshot model x = A s + n, honestly: K snapshots of an N-element
    array. `sources` is a list of dicts (theta_deg, p_db): each source is a
    complex Gaussian signal of per-element power undb(p_db) (a fluctuating
    echo — Swerling-style, lecture 14), receiver noise is unit power per
    element. Returns X, shape (n, n_snap). Physically: one snapshot = one
    chirp's worth of the target's range-Doppler cell, taken across the
    array (hw15 gave you the cell; this week you get its wavefront).
    """
    rng = np.random.default_rng(seed)
    n = arr["n"]
    x = (rng.standard_normal((n, n_snap))
         + 1j * rng.standard_normal((n, n_snap))) * np.sqrt(0.5)
    for src in sources:
        a = steering_vector(arr, src["theta_deg"])
        s = (rng.standard_normal(n_snap) + 1j * rng.standard_normal(n_snap)) \
            * np.sqrt(undb(src["p_db"]) / 2.0)
        x += np.outer(a, s)
    return x


def top_peaks_deg(theta_deg, p_lin, n_peaks=1, min_sep_deg=2.0):
    """Peak picking (plumbing, not physics): the n_peaks largest local
    maxima of a sampled spectrum, at least min_sep_deg apart, strongest
    first. Returns a list of angles (deg)."""
    th = np.asarray(theta_deg, dtype=float)
    p = np.asarray(p_lin, dtype=float)
    is_pk = np.r_[False, (p[1:-1] > p[:-2]) & (p[1:-1] >= p[2:]), False]
    idx = np.flatnonzero(is_pk)
    idx = idx[np.argsort(p[idx])[::-1]]
    out = []
    for i in idx:
        if all(abs(th[i] - a) >= min_sep_deg for a in out):
            out.append(float(th[i]))
        if len(out) == n_peaks:
            break
    return out


def make_frames(scene_name, seed=1616):
    """The hw15 pipeline's output for one corridor scene, frame by frame.

    Returns a list of N_FRAMES frames. Each frame is a dict:
      t_s        : frame time
      detections : list of dicts, one per detected target —
          track_id : which track this detection belongs to (association is
                     GIVEN; real trackers spend half their code earning it)
          r_m      : measured range (truth + 0.15 m noise)
          v_m_s    : measured range rate, receding positive (hw15's sign)
          x_snap   : (n, 32) array snapshots of this target's range-Doppler
                     cell — YOUR module 1 turns these into theta
      jammer_ref : (n, 32) target-free snapshots (noise + jammer only) when
                   the scene is jammed, else None. A real receiver gets
                   these for free — the jammer is in EVERY cell; an empty
                   one is a clean look at it.
    """
    scene = TRACK_SCENES[scene_name]
    rng = np.random.default_rng(seed + zlib.crc32(scene_name.encode()) % 1000)
    frames = []
    for fi in range(N_FRAMES):
        t = fi * DT_S
        dets = []
        for tid, tgt in scene["targets"].items():
            p = np.asarray(tgt["p0_m"]) + np.asarray(tgt["v_m_s"]) * t
            r = float(np.hypot(*p))
            v_r = float(np.dot(p, tgt["v_m_s"]) / r)      # receding positive
            theta = float(np.degrees(np.arctan2(p[0], p[1])))
            srcs = [dict(theta_deg=theta, p_db=tgt["snr_db"])]
            if scene["jammer"]:
                srcs.append(dict(theta_deg=JAMMER_DEG, p_db=JAMMER_DB))
            x = make_snapshots(ARRAY, srcs, n_snap=32,
                               seed=int(rng.integers(2**31)))
            dets.append(dict(
                track_id=tid,
                r_m=r + R_NOISE_M * rng.standard_normal(),
                v_m_s=v_r + V_NOISE_M_S * rng.standard_normal(),
                x_snap=x))
        ref = None
        if scene["jammer"]:
            ref = make_snapshots(
                ARRAY, [dict(theta_deg=JAMMER_DEG, p_db=JAMMER_DB)],
                n_snap=32, seed=int(rng.integers(2**31)))
        frames.append(dict(t_s=t, detections=dets, jammer_ref=ref))
    return frames


def jammer_bearing_deg(frames):
    """Estimated jammer bearing from the target-free reference snapshots
    (plumbing): beamscan the first frame's jammer_ref, return the peak.
    Returns None for unjammed scenes."""
    ref = frames[0]["jammer_ref"]
    if ref is None:
        return None
    r_hat = ref @ ref.conj().T / ref.shape[1]
    a = steering_vector(ARRAY, THETA_DEG)
    p = np.real(np.einsum("ip,ij,jp->p", a.conj(), r_hat, a)) / ARRAY["n"] ** 2
    return top_peaks_deg(THETA_DEG, p, 1)[0]


def alpha_beta_track(t_s, pos_xy_m, alpha=0.5, beta=0.2):
    """The alpha-beta filter (the tracking minimum, hour 2's equations),
    run per axis on a sequence of measured positions. Initialization: state
    at the first point, velocity from the first pair. Returns dict:
      pos_m : (T, 2) filtered positions
      vel_m_s : (T, 2) filtered velocities
    The gains are the course defaults — Q4 asks you to reason about them,
    not tune them.
    """
    t = np.asarray(t_s, dtype=float)
    z = np.asarray(pos_xy_m, dtype=float)
    x = z[0].copy()
    v = (z[1] - z[0]) / (t[1] - t[0])
    pos, vel = [x.copy()], [v.copy()]
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        x_pred = x + v * dt
        res = z[i] - x_pred
        x = x_pred + alpha * res
        v = v + (beta / dt) * res
        pos.append(x.copy())
        vel.append(v.copy())
    return dict(pos_m=np.array(pos), vel_m_s=np.array(vel))


def cpa_truth(scene_name, track_id):
    """The closed-form CPA referee: for a straight-line trajectory
    p(t) = p0 + v*t, t_cpa = -(p0.v)/|v|^2 and d_cpa = |p(t_cpa)| — exact
    by construction. Times are measured from the scene's first frame."""
    tgt = TRACK_SCENES[scene_name]["targets"][track_id]
    p0 = np.asarray(tgt["p0_m"], dtype=float)
    v = np.asarray(tgt["v_m_s"], dtype=float)
    t_cpa = float(-np.dot(p0, v) / np.dot(v, v))
    d_cpa = float(np.linalg.norm(p0 + v * t_cpa))
    return t_cpa, d_cpa


# The instructor's truth table (module 3's referee): the alert verdict per
# target, from the closed-form CPA against the ALERT contract. Yes, you can
# read it — the referee measures whether your PIPELINE reproduces it from
# noisy measurements, which is the entire point.
TRUTH_TABLE = {
    (sc, tid): (0.0 < cpa_truth(sc, tid)[0] <= ALERT["t_horizon_s"]
                and cpa_truth(sc, tid)[1] < ALERT["d_alert_m"])
    for sc in TRACK_SCENES for tid in TRACK_SCENES[sc]["targets"]
}


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def sample_covariance(x_snap):
    """Module 1 (warm-up) — the sample spatial covariance R_hat = X X^H / K
    from snapshots X of shape (n, K). One line; everything adaptive stands
    on it, and hour 3's deliberate bug is what happens when K is too small.
    """
    raise NotImplementedError


def beamscan_spectrum(x_snap, arr, theta_deg):
    """Module 1 (the fast one) — conventional (delay-and-sum / Bartlett)
    DOA spectrum: steer a uniform beam to every angle in theta_deg and
    report the received power,

        P(theta) = a(theta)^H R_hat a(theta) / N^2.

    The 1/N^2 normalization makes a lone source's peak read its per-element
    SNR (linear, re noise) — the checker's dB numbers assume it. Vectorize
    over angles (a loop over 9001 angles works but drags). Resolution =
    the beamwidth, by construction — it is lecture 13's pattern, used
    backwards.
    """
    raise NotImplementedError


def mvdr_spectrum(x_snap, arr, theta_deg, load_db=None):
    """Module 1 (the adaptive one) — MVDR/Capon spectrum:

        P(theta) = N / ( a(theta)^H R_hat^{-1} a(theta) ).

    This normalization makes a noise-only direction read 0 dB (a^H I a =
    N) and a lone source of per-element SNR p read 1 + N*p — the array
    gain N rides in front, unlike beamscan's convention; the checker
    prints db(1 + N*p) next to your peak so you can see it. What matters
    for DOA is WHERE the peaks sit, and the sharpness MVDR buys.

    load_db: diagonal loading, dB re the per-element noise power (None =
    no loading). Loading adds undb(load_db) * I to R_hat before inverting —
    hour 3's fix for the too-few-snapshots bug; module 2's jammed scene
    also passes it. Use a linear solve (np.linalg.solve), not an explicit
    matrix inverse in a loop over angles.
    """
    raise NotImplementedError


def resolution_study(arr, sep_bw, snr_grid_db, n_snap=N_SNAP, seed=1620):
    """Module 1 (the study) — the resolution question, measured.

    Two equal-power drones sep_bw beamwidths apart (symmetric about
    broadside), per-element SNR swept over snr_grid_db. For each SNR, one
    snapshot draw (seed + index — deterministic), both spectra, and the
    classic two-point resolution test: RESOLVED means the spectrum at each
    true angle exceeds the spectrum at the midpoint (there is a dip
    between the two sources). Return a dict:

      sep_deg      : the separation used, deg
      snr_db       : the grid (as given)
      beamscan     : list of bools, resolved per SNR
      mvdr         : list of bools, resolved per SNR
      dip_beamscan_db, dip_mvdr_db : the measured dip depths per SNR,
                     min(P(theta_1), P(theta_2)) / P(midpoint) in dB
                     (negative = no dip, i.e. the midpoint is HIGHER)
      flip_beamscan_db, flip_mvdr_db : the lowest SNR from which the
                     method stays resolved through the top of the grid
                     (None if it never settles)

    ANSWERS.md Q1 is answered from this. The checker runs it at 1.5 and
    0.7 beamwidths.
    """
    raise NotImplementedError


def chain_frames(frames, arr, method="beamscan", load_db=None,
                 mask_deg=None):
    """Module 2 (the chain) — plug DOA into the provided detections.

    For every frame and every detection, estimate theta from the
    detection's x_snap with YOUR beamscan (method="beamscan") or YOUR MVDR
    (method="mvdr", passing load_db through), on the course grid THETA_DEG.
    Take the STRONGEST spectrum peak (toolkit's top_peaks_deg) — except:
    when mask_deg is given, first get the jammer bearing from the
    toolkit's jammer_bearing_deg(frames) and skip any peak within
    mask_deg of it (the jammer is a peak too; an angle you refuse to
    report is the price of admission — Q2).

    Return the frames as (R, v, theta) target lists: a list (per frame) of
    lists of dicts dict(track_id, r_m, v_m_s, theta_deg) — r_m and v_m_s
    copied from the detection, theta_deg yours.
    """
    raise NotImplementedError


def cpa_ttc(pos_xy_m, vel_xy_m_s):
    """Module 3 (the geometry) — closest point of approach, closed form.

    Given a track state — position p (m) and velocity v (m/s), both 2-D,
    relative to the sensor at the origin — return (t_cpa_s, d_cpa_m):
    the time until the closest approach (negative = it already happened /
    the target is opening) and the miss distance at that moment. Derive it
    by minimizing |p + v t|^2 — hour 2 did it on the board in four lines.
    Handle |v| = 0 (hovering: d_cpa = |p|, t_cpa = 0).
    """
    raise NotImplementedError


def alert_decision(t_cpa_s, d_cpa_m, alert=ALERT):
    """Module 3 (the verdict) — the alert rule, exactly as stated in the
    contract: alert iff the CPA is ahead (t_cpa > 0, measured from the
    decision moment), within the horizon (t_cpa <= t_horizon_s), and
    inside the protected radius (d_cpa < d_alert_m). Return a bool.
    Defend the rule — against both miss and false-alarm costs — in
    ANSWERS.md Q4."""
    raise NotImplementedError


def avoid_study(scene_names=tuple(TRACK_SCENES), arr=ARRAY):
    """Module 3 (the capstone) — detect, locate, avoid, per scene.

    For each scene: make_frames -> YOUR chain_frames (use beamscan for the
    clean scenes; for the jammed scene use MVDR with load_db=10 and
    mask_deg=3) -> per track_id, convert (r, theta) to x = r sin(theta),
    y = r cos(theta), run the toolkit's alpha_beta_track, take the LAST
    filtered state (the decision moment), and get YOUR cpa_ttc and
    alert_decision.

    Time bookkeeping (so your table matches the closed-form referee):
    cpa_ttc at the last frame returns time-to-go from that frame; the
    alert rule uses the time-to-go; but REPORT t_cpa_s from the scene's
    first frame, i.e. t_cpa_s = t_last + time-to-go.

    Return dict[(scene_name, track_id)] = dict(t_cpa_s, d_cpa_m, alert,
    n_frames). The checker holds it against the closed-form truth and the
    instructor's truth table.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# The referees: pyargus (an independent DOA implementation, installed with
# the course env) fed the IDENTICAL snapshots on the IDENTICAL grid, and
# the closed-form CPA of the planted straight-line trajectories. Your
# modules and these referees are independent; if they disagree, someone is
# wrong about the physics — find out who.
# ----------------------------------------------------------------------------
def _pyargus_spectra(x_snap, arr, theta_deg):
    """pyargus Bartlett + Capon on our snapshots, mapped onto our angle
    convention: pyargus measures incidence from the array AXIS with
    steering exp(+j*2pi*(d/lambda)*n*cos(theta_inc)); ours is broadside-
    referenced with sin(theta). theta_inc = 90 - theta makes them the same
    vector. Returns (p_bartlett, p_capon), linear, arbitrary scale (the
    referee compares PEAK ANGLES, not levels)."""
    from pyargus import directionEstimation as de

    align_wl = np.arange(arr["n"]) * arr["d_m"] / wavelength_m(arr["f_hz"])
    sv = de.gen_ula_scanning_vectors(align_wl,
                                     90.0 - np.asarray(theta_deg, float))
    r_hat = de.corr_matrix_estimate(x_snap.T, imp="fast")
    p_bart = np.abs(de.DOA_Bartlett(r_hat, sv))
    p_capon = np.abs(de.DOA_Capon(r_hat, sv))
    return p_bart, p_capon


def _doa_referee_lines(m):
    """Peak-angle deltas, your spectra vs pyargus, identical snapshots."""
    lines = []
    try:
        import pyargus  # noqa: F401
    except ImportError:
        return ["  pyargus not installed - referee skipped "
                "(pip install pyargus)"]
    for name, srcs in DOA_SCENES.items():
        x = make_snapshots(ARRAY, srcs, N_SNAP, seed=1601)
        n_src = len(srcs)
        p_b = m["beamscan_spectrum"](x, ARRAY, THETA_DEG)
        p_m = m["mvdr_spectrum"](x, ARRAY, THETA_DEG)
        ref_b, ref_c = _pyargus_spectra(x, ARRAY, THETA_DEG)
        mine_b = sorted(top_peaks_deg(THETA_DEG, p_b, n_src))
        mine_m = sorted(top_peaks_deg(THETA_DEG, p_m, n_src))
        py_b = sorted(top_peaks_deg(THETA_DEG, ref_b, n_src))
        py_c = sorted(top_peaks_deg(THETA_DEG, ref_c, n_src))
        d_b = max(abs(a - b) for a, b in zip(mine_b, py_b))
        d_c = max(abs(a - b) for a, b in zip(mine_m, py_c))
        lines.append(f"  {name:12s}: beamscan peaks "
                     f"{['%+.2f' % a for a in mine_b]} vs pyargus Bartlett "
                     f"{['%+.2f' % a for a in py_b]} -> max d = {d_b:.3f} deg")
        lines.append(f"  {'':12s}  MVDR     peaks "
                     f"{['%+.2f' % a for a in mine_m]} vs pyargus Capon    "
                     f"{['%+.2f' % a for a in py_c]} -> max d = {d_c:.3f} deg")
    return lines


def _fmt_bools(bools):
    return "".join("R" if b else "." for b in bools)


def run_checks(mods=None):
    m = mods or dict(sample_covariance=sample_covariance,
                     beamscan_spectrum=beamscan_spectrum,
                     mvdr_spectrum=mvdr_spectrum,
                     resolution_study=resolution_study,
                     chain_frames=chain_frames,
                     cpa_ttc=cpa_ttc,
                     alert_decision=alert_decision,
                     avoid_study=avoid_study)
    arr = ARRAY
    print("=" * 66)
    print("hw16 --check : measured facts (instrument, not grade)")
    print("=" * 66)
    print(f"array: N = {arr['n']}, f = {arr['f_hz']/1e9:.0f} GHz, "
          f"d = {arr['d_m']*1e3:.4f} mm = lambda/2, aperture "
          f"{(arr['n']-1)*arr['d_m']*1e3:.1f} mm")
    print(f"broadside HPBW (hw13 closed form) = {hpbw_deg(arr):.4f} deg; "
          f"1.5 beamwidths = {1.5*hpbw_deg(arr):.4f} deg")

    # --- module 1: DOA — beamscan, MVDR, the referee, the study ------------
    print("\n[module 1] sample_covariance / beamscan_spectrum / mvdr_spectrum")
    try:
        x1 = make_snapshots(arr, DOA_SCENES["one_drone"], N_SNAP, seed=1601)
        r1 = m["sample_covariance"](x1)
        tr = float(np.real(np.trace(r1))) / arr["n"]
        print(f"  R_hat: shape {r1.shape}, Hermitian residual "
              f"{np.abs(r1 - r1.conj().T).max():.2e}, tr/N = {tr:.3f} "
              f"(source 10 dB + noise -> expect ~{1 + undb(10.0):.1f})")
        p_b = m["beamscan_spectrum"](x1, arr, THETA_DEG)
        p_m = m["mvdr_spectrum"](x1, arr, THETA_DEG)
        pk_b = top_peaks_deg(THETA_DEG, p_b, 1)[0]
        pk_m = top_peaks_deg(THETA_DEG, p_m, 1)[0]
        print("  one drone planted at -12.00 deg, 10 dB:")
        print(f"    beamscan peak {pk_b:+.2f} deg, reads "
              f"{db(np.max(p_b)):+5.2f} dB (convention: p + 1/N)   | "
              f"MVDR peak {pk_m:+.2f} deg, reads {db(np.max(p_m)):+5.2f} dB "
              f"(convention: 1 + N*p = {db(1 + 16 * undb(10.0)):.2f})")
        # the jammer case — the interference-nulling picture, measured
        xj = make_snapshots(arr, DOA_SCENES["jammer"], N_SNAP, seed=1601)
        pj_b = m["beamscan_spectrum"](xj, arr, THETA_DEG)
        pj_m = m["mvdr_spectrum"](xj, arr, THETA_DEG)
        sel = np.abs(THETA_DEG - (-10.0)) <= 1.0     # around the drone
        i_dr = int(np.argmin(np.abs(THETA_DEG - (-10.0))))
        pks_b = top_peaks_deg(THETA_DEG, pj_b, 2)
        pks_m = top_peaks_deg(THETA_DEG, pj_m, 2)
        print(f"  jammer scene (drone -10 deg/10 dB, jammer +25 deg/50 dB):")
        print(f"    beamscan: 2 peaks at {['%+.2f' % a for a in pks_b]} deg; "
              f"spectrum at the drone {db(pj_b[i_dr]):+.2f} dB vs local "
              f"max off-jammer {db(pj_b[sel].max()):+.2f} dB")
        print(f"    MVDR:     2 peaks at {['%+.2f' % a for a in pks_m]} deg; "
              f"spectrum at the drone {db(pj_m[i_dr]):+.2f} dB")
        print("  pyargus referee (identical snapshots, identical grid; "
              "criterion 0.5 deg):")
        for line in _doa_referee_lines(m):
            print(line)
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\n[module 1] resolution_study  (the predict-first question, "
          "measured)")
    try:
        snr_grid = list(range(-15, 21, 3))
        for sep in (1.5, 0.7):
            rs = m["resolution_study"](arr, sep, snr_grid)
            print(f"  separation {sep} BW = {rs['sep_deg']:.2f} deg   "
                  f"(SNR {snr_grid[0]}..{snr_grid[-1]} dB, step 3):")
            print(f"    beamscan resolved: {_fmt_bools(rs['beamscan'])}"
                  f"   flip at {rs['flip_beamscan_db']} dB")
            print(f"    MVDR     resolved: {_fmt_bools(rs['mvdr'])}"
                  f"   flip at {rs['flip_mvdr_db']} dB")
            i20 = snr_grid.index(18)
            print(f"    dip at 18 dB SNR: beamscan "
                  f"{rs['dip_beamscan_db'][i20]:+.2f} dB, MVDR "
                  f"{rs['dip_mvdr_db'][i20]:+.2f} dB")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the chain -----------------------------------------------
    print("\n[module 2] chain_frames  ((R, v) + your theta, per frame)")
    try:
        frames = make_frames("crossing_drones")
        out = m["chain_frames"](frames, arr, method="beamscan")
        errs = []
        for fi, frame in enumerate(frames):
            t = frame["t_s"]
            for det, tgt in zip(frame["detections"], out[fi]):
                tr = TRACK_SCENES["crossing_drones"]["targets"][det["track_id"]]
                p = np.asarray(tr["p0_m"]) + np.asarray(tr["v_m_s"]) * t
                th_true = np.degrees(np.arctan2(p[0], p[1]))
                errs.append(abs(tgt["theta_deg"] - th_true))
        errs = np.asarray(errs)
        print(f"  crossing_drones, beamscan chain: theta error over "
              f"{errs.size} detections: mean {errs.mean():.3f} deg, "
              f"max {errs.max():.3f} deg  (HPBW = {hpbw_deg(arr):.2f})")
        fj = make_frames("jammed_crossing")
        jb = jammer_bearing_deg(fj)
        print(f"  jammed_crossing: toolkit jammer bearing = {jb:+.2f} deg "
              f"(planted {JAMMER_DEG:+.1f})")
        tr = TRACK_SCENES["jammed_crossing"]["targets"]["drone_j"]
        for meth, kw in (("beamscan", dict()),
                         ("mvdr", dict(load_db=10.0, mask_deg=3.0))):
            outj = m["chain_frames"](fj, arr, method=meth, **kw)
            ej = []
            for fi, frame in enumerate(fj):
                t = frame["t_s"]
                p = np.asarray(tr["p0_m"]) + np.asarray(tr["v_m_s"]) * t
                th_true = np.degrees(np.arctan2(p[0], p[1]))
                ej.append(abs(outj[fi][0]["theta_deg"] - th_true))
            ej = np.asarray(ej)
            print(f"    {meth:8s} chain: theta error mean {ej.mean():7.3f} "
                  f"deg, max {ej.max():7.3f} deg"
                  + ("   <- reads the jammer, not the drone"
                     if ej.mean() > 5 else ""))
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: avoid ----------------------------------------------------
    print("\n[module 3] cpa_ttc / alert_decision / avoid_study")
    try:
        # closed-form probes first (no scenes involved)
        t1, d1 = m["cpa_ttc"](np.array([30.0, 190.0]),
                              np.array([-9.0, -38.0]))
        tt, dt_ = cpa_truth("fast_intruder", "fixed_wing")
        print(f"  cpa_ttc on the intruder's TRUE state: t_cpa = {t1:.3f} s, "
              f"d_cpa = {d1:.3f} m  | closed-form referee ({tt:.3f}, "
              f"{dt_:.3f}) -> d = {abs(d1-dt_):.1e} m")
        t0, d0 = m["cpa_ttc"](np.array([25.0, 0.0]), np.array([0.0, 0.0]))
        print(f"  hovering edge case (|v| = 0): t_cpa = {t0}, d_cpa = {d0}")
        study = m["avoid_study"]()
        print(f"  the capstone table (alert rule: 0 < t_cpa <= "
              f"{ALERT['t_horizon_s']:.0f} s and d_cpa < "
              f"{ALERT['d_alert_m']:.0f} m):")
        print("    scene/target                 measured (t_cpa, d_cpa)"
              "    truth (t_cpa, d_cpa)   |dCPA|   alert  truth")
        n_match, worst = 0, 0.0
        for (sc, tid), res in study.items():
            tt, dd = cpa_truth(sc, tid)
            err = abs(res["d_cpa_m"] - dd)
            worst = max(worst, err)
            ok = res["alert"] == TRUTH_TABLE[(sc, tid)]
            n_match += ok
            print(f"    {sc + '/' + tid:28s} ({res['t_cpa_s']:7.2f} s, "
                  f"{res['d_cpa_m']:6.2f} m)    ({tt:7.2f} s, {dd:6.2f} m)"
                  f"   {err:5.2f} m   {str(res['alert']):5s}  "
                  f"{str(TRUTH_TABLE[(sc, tid)]):5s}"
                  f"{'' if ok else '   <- MISMATCH'}")
        print(f"  alert verdicts matching the instructor truth table: "
              f"{n_match}/{len(study)}   (criterion: all, including the "
              f"non-alerts); worst CPA error {worst:.2f} m (criterion 5 m)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(beamscan_spectrum=beamscan_spectrum,
                     mvdr_spectrum=mvdr_spectrum,
                     resolution_study=resolution_study,
                     chain_frames=chain_frames,
                     cpa_ttc=cpa_ttc,
                     alert_decision=alert_decision,
                     avoid_study=avoid_study)
    arr = ARRAY
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.6))

    # --- picture 1: two drones 1.5 BW apart, both spectra (Q1) -------------
    ax = axes[0, 0]
    try:
        srcs = DOA_SCENES["two_drones"]
        for snr, ls in ((0.0, "--"), (18.0, "-")):
            s2 = [dict(theta_deg=s["theta_deg"], p_db=snr) for s in srcs]
            x = make_snapshots(arr, s2, N_SNAP, seed=1620)
            for name, fn, color in (("beamscan", m["beamscan_spectrum"], "C0"),
                                    ("MVDR", m["mvdr_spectrum"], "C3")):
                p = fn(x, arr, THETA_DEG)
                ax.plot(THETA_DEG, db(p / p.max()), ls, color=color, lw=1.1,
                        label=f"{name}, {snr:.0f} dB" )
        for s in srcs:
            ax.axvline(s["theta_deg"], color="k", ls=":", alpha=0.5)
        ax.set_xlim(-20, 20)
        ax.set_ylim(-30, 2)
        ax.set_xlabel("theta (deg)")
        ax.set_ylabel("normalized spectrum (dB)")
        ax.set_title(f"two drones {_SEP_DEG:.1f} deg apart (1.5 beamwidths)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 1 not implemented")

    # --- picture 2: the jammer scene (Q2) ----------------------------------
    ax = axes[0, 1]
    try:
        x = make_snapshots(arr, DOA_SCENES["jammer"], N_SNAP, seed=1601)
        p_b = m["beamscan_spectrum"](x, arr, THETA_DEG)
        p_m = m["mvdr_spectrum"](x, arr, THETA_DEG)
        ax.plot(THETA_DEG, db(p_b), lw=1.1, label="beamscan")
        ax.plot(THETA_DEG, db(p_m), lw=1.1, label="MVDR")
        ax.axvline(-10, color="k", ls=":", alpha=0.6)
        ax.annotate("drone (10 dB)", (-10, 12), fontsize=8, ha="center")
        ax.axvline(25, color="r", ls=":", alpha=0.6)
        ax.annotate("jammer (50 dB)", (25, 52), fontsize=8, ha="center")
        ax.set_xlim(-60, 60)
        ax.set_xlabel("theta (deg)")
        ax.set_ylabel("spectrum (dB re per-element noise)")
        ax.set_title("the jammer case: sidelobes vs the adapted null")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 1 not implemented")

    # --- picture 3: resolution vs SNR (Q1's flip) --------------------------
    ax = axes[1, 0]
    try:
        snr_grid = list(range(-15, 21, 1))
        for sep, ls in ((1.5, "-"), (0.7, "--")):
            rs = m["resolution_study"](arr, sep, snr_grid)
            ax.plot(snr_grid, rs["dip_beamscan_db"], ls, color="C0", lw=1.1,
                    label=f"beamscan, {sep} BW")
            ax.plot(snr_grid, rs["dip_mvdr_db"], ls, color="C3", lw=1.1,
                    label=f"MVDR, {sep} BW")
        ax.axhline(0.0, color="k", lw=0.8, alpha=0.6)
        ax.set_xlabel("per-element SNR (dB)")
        ax.set_ylabel("dip depth (dB; > 0 = resolved)")
        ax.set_title("two-point resolution vs SNR (the flip)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 1 not implemented")

    # --- picture 4: the corridor — tracks, CPA, verdicts (Q4) --------------
    ax = axes[1, 1]
    try:
        study = m["avoid_study"]()
        colors = dict(crossing_drones="C0", fast_intruder="C3",
                      jammed_crossing="C2")
        for sc_name, sc in TRACK_SCENES.items():
            frames = make_frames(sc_name)
            kw = (dict(method="mvdr", load_db=10.0, mask_deg=3.0)
                  if sc["jammer"] else dict(method="beamscan"))
            out = m["chain_frames"](frames, arr, **kw)
            for tid, tgt in sc["targets"].items():
                p0, v = np.asarray(tgt["p0_m"]), np.asarray(tgt["v_m_s"])
                ts = np.array([f["t_s"] for f in frames])
                truth = p0[None, :] + v[None, :] * ts[:, None]
                ax.plot(truth[:, 0], truth[:, 1], "-", lw=0.9, alpha=0.5,
                        color=colors[sc_name])
                meas = []
                for fr in out:
                    d = next(d for d in fr if d["track_id"] == tid)
                    th = np.radians(d["theta_deg"])
                    meas.append((d["r_m"] * np.sin(th),
                                 d["r_m"] * np.cos(th)))
                meas = np.asarray(meas)
                ax.plot(meas[:, 0], meas[:, 1], ".", ms=3,
                        color=colors[sc_name])
                res = study[(sc_name, tid)]
                t_c, d_c = cpa_truth(sc_name, tid)
                cpa_pt = p0 + v * t_c
                ax.plot(*cpa_pt, "x", ms=8, color=colors[sc_name])
                ax.annotate(f"{tid}\n{'ALERT' if res['alert'] else 'ok'} "
                            f"d={res['d_cpa_m']:.0f} m",
                            (truth[0, 0], truth[0, 1]), fontsize=7,
                            textcoords="offset points", xytext=(4, 4))
        circ = plt.Circle((0, 0), ALERT["d_alert_m"], fill=False,
                          color="r", ls="--", alpha=0.6)
        ax.add_patch(circ)
        ax.plot(0, 0, "k^", ms=9)
        ax.annotate("sensor", (0, 0), textcoords="offset points",
                    xytext=(6, -12), fontsize=8)
        ax.set_xlim(-80, 80)
        ax.set_ylim(-10, 200)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m, corridor axis)")
        ax.set_title("the corridor: truth (lines), your chain (dots), "
                     "CPA (x)")
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("modules 2+3 not implemented")

    fig.tight_layout()
    fig.savefig("hw16_plots.png", dpi=130)
    print("wrote hw16_plots.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--plot", action="store_true",
                    help="the four pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.plot:
        make_plots()
    if not (args.check or args.plot):
        print(__doc__)


if __name__ == "__main__":
    main()
