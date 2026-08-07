"""Homework 14 starter — See it through the noise.

You implement the three modules marked TODO below. Everything else is the
toolkit: the course radar, the exact-statistics referees (Rayleigh closed
form, Marcum Q), the scene generator with planted ground truth, and the
checker.

Run from this directory:

    python hw14_starter.py --check    # measured facts per module (the instrument)
    python hw14_starter.py --plot     # the four pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbm` / `*_dbi` are decibel
quantities; `*_w`, `*_hz`, `*_m`, `*_m2` are SI. Detection statistics live
in two domains and the names say which: `*_amp` is an envelope AMPLITUDE
(volts-like, Rayleigh under noise), `power` / `*_pow` is a square-law POWER
(amplitude squared, exponential under noise). Mixing the two domains is
this lecture's deliberate bug. Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s
from scipy.constants import k as K_BOLTZ        # Boltzmann constant, J/K
from scipy.optimize import brentq
from scipy.stats import ncx2

T0_K = 290.0                                    # IEEE noise reference temperature

# ----------------------------------------------------------------------------
# The systems (instructor side — mirrors hw1's COURSE_RADAR and TARGETS,
# re-provided verbatim so this homework stands alone; lecture 1's measured
# detection ranges with the bare 13 dB bar: airliner 32.65 km, fighter
# 12.98 km, drone 4.11 km)
# ----------------------------------------------------------------------------
COURSE_RADAR = dict(
    f_hz=10e9,         # X-band
    p_t_w=10e3,        # transmit power, watts (10 kW)
    g_dbi=33.0,        # antenna gain, same dish for TX and RX (monostatic)
    b_hz=1e6,          # receiver noise bandwidth
    nf_db=3.0,         # receiver noise figure
    loss_db=6.0,       # total system losses (plumbing, processing, weather)
    snr_req_db=13.0,   # lecture 1's placeholder bar — TODAY it gets honest
)

TARGETS = {
    "airliner": 40.0,      # m^2  -- a 747-class body, broadside-ish
    "fighter":   1.0,      # m^2  -- clean supersonic airframe
    "drone":     0.01,     # m^2  -- small quadcopter, plastic + battery
}

# The detection spec this homework must meet (the story's contract).
DETECTION = dict(
    pfa=1e-6,          # design false-alarm probability, per decision cell
    pd=0.9,            # detection probability the customer actually wants
    n_trials_pfa=1_000_000,   # Monte Carlo trials for the P_fa measurement
)

# CA-CFAR (cell-averaging constant-false-alarm-rate) baseline parameters.
CFAR = dict(
    n_train=8,         # training cells PER SIDE (total N = 16)
    n_guard=2,         # guard cells per side
    pfa=1e-6,          # per-cell design P_fa (same contract as above)
)

# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> decibels (re-provided each lecture; course rule)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """Decibels -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def wavelength_m(f_hz):
    """Free-space wavelength lambda = c / f.  (Mirrors hw1's toolkit.)"""
    return C_M_S / np.asarray(f_hz, dtype=float)


def noise_floor_w(b_hz, nf_db):
    """Receiver noise power k*T0*B*F in WATTS.  (Mirrors hw1's toolkit.)"""
    return K_BOLTZ * T0_K * np.asarray(b_hz, dtype=float) * 10.0 ** (nf_db / 10.0)


def radar_snr_db(radar, sigma_m2, r_m):
    """Monostatic radar equation, forward. Mirrors hw1 module 2 (there you
    built it; this week it is plumbing). Single-pulse SNR in dB."""
    r = np.asarray(r_m, dtype=float)
    lam = wavelength_m(radar["f_hz"])
    num_db = (db(radar["p_t_w"]) + 2.0 * radar["g_dbi"]
              + db(lam**2) + db(sigma_m2))
    den_db = (db((4.0 * np.pi) ** 3) + db(r**4)
              + db(K_BOLTZ * T0_K * radar["b_hz"])
              + radar["nf_db"] + radar["loss_db"])
    return num_db - den_db


def radar_max_range_m(radar, sigma_m2, snr_req_db=None):
    """Closed-form inverse of the radar equation. Mirrors hw1 module 2, with
    one addition for this week: pass snr_req_db to override the radar's own
    bar (hw1 always used radar['snr_req_db']; default unchanged)."""
    if snr_req_db is None:
        snr_req_db = radar["snr_req_db"]
    lam = wavelength_m(radar["f_hz"])
    num = radar["p_t_w"] * undb(2.0 * radar["g_dbi"]) * lam**2 * sigma_m2
    den = ((4.0 * np.pi) ** 3 * K_BOLTZ * T0_K * radar["b_hz"]
           * undb(radar["nf_db"]) * undb(radar["loss_db"])
           * undb(snr_req_db))
    return float((num / den) ** 0.25)


def marcum_pd(snr_db, pfa):
    """EXACT single-pulse P_d for a nonfluctuating target, linear detector:
    Marcum's Q function, evaluated through the noncentral chi-square
    survival function. This is module 2's referee — the library checks your
    Monte Carlo; it never plays for you."""
    snr = undb(snr_db)
    return ncx2.sf(2.0 * np.log(1.0 / pfa), df=2, nc=2.0 * snr)


def snr_required_exact_db(pd, pfa):
    """EXACT SNR (dB) that delivers (pd, pfa) — inverts marcum_pd. The
    referee Albersheim's approximation is judged against."""
    return brentq(lambda s: marcum_pd(s, pfa) - pd, -15.0, 35.0, xtol=1e-9)


def binom_3sigma(p, n_trials):
    """3-sigma binomial error bar on a probability measured with n trials."""
    return 3.0 * np.sqrt(p * (1.0 - p) / n_trials)


def cfar_alpha(n_train_total, pfa):
    """Closed-form CA-CFAR threshold multiplier (on the MEAN of the training
    cells, square-law power domain): alpha = N * (pfa^(-1/N) - 1).
    As N -> infinity this tends to ln(1/pfa), the known-noise multiplier."""
    n = float(n_train_total)
    return n * (pfa ** (-1.0 / n) - 1.0)


def cfar_loss_db(n_train_total, pfa):
    """CFAR loss: how much higher the adaptive threshold sits above the
    known-noise ideal, 10*log10(alpha_N / ln(1/pfa)). The price of
    estimating the noise from N cells instead of knowing it."""
    return float(db(cfar_alpha(n_train_total, pfa) / np.log(1.0 / pfa)))


# ----------------------------------------------------------------------------
# Scenes (provided — planted ground truth; the referee for module 3)
#
# Powers are normalized to a unit thermal floor (mean noise power = 1), so
# "SNR" and "power" are the same numbers in dB. Targets are nonfluctuating:
# a fixed amplitude added to complex noise, then square-law detected.
# Clutter is modeled as a raised noise floor (Rayleigh clutter) — honest for
# today; real clutter has longer tails (the war story's sea spikes).
# ----------------------------------------------------------------------------
N_CELLS = 2000
SCENES = ("clean", "clutter_edge", "two_drones")
_SCENE_SEED = {"clean": 1401, "clutter_edge": 1402, "two_drones": 1403,
               "two_drones_solo": 1403}   # solo shares the seed on purpose


def make_scene(name, seed=None):
    """Build a named range profile with planted truth.

    Returns dict(name, power, targets, clutter):
      power   : (N_CELLS,) square-law power profile, unit thermal floor
      targets : list of (cell, snr_db) — snr_db is vs the LOCAL noise floor
      clutter : (start_cell, stop_cell, level_db) or None
    'two_drones_solo' is 'two_drones' with the strong drone deleted but the
    SAME noise draw — the masking experiment's control arm.
    """
    if seed is None:
        seed = _SCENE_SEED[name]
    rng = np.random.default_rng(seed)
    noise = (rng.standard_normal(N_CELLS)
             + 1j * rng.standard_normal(N_CELLS)) * np.sqrt(0.5)
    floor = np.ones(N_CELLS)                       # local noise power, linear
    clutter = None
    if name == "clean":
        targets = [(400, 20.0), (1400, 15.0)]
    elif name == "clutter_edge":
        clutter = (1000, 2000, 30.0)               # the ground turns on here
        targets = [(995, 15.0), (1500, 20.0)]      # near-edge / deep-in
    elif name == "two_drones":
        targets = [(1000, 22.0), (1006, 15.0)]     # 6 cells apart
    elif name == "two_drones_solo":
        targets = [(1006, 15.0)]
    else:
        raise ValueError(f"unknown scene {name!r}")
    if clutter is not None:
        lo, hi, lvl_db = clutter
        floor[lo:hi] = undb(lvl_db)
    sig = noise * np.sqrt(floor)                   # raise the floor
    for cell, snr_db in targets:
        sig[cell] += np.sqrt(undb(snr_db) * floor[cell])
    return dict(name=name, power=np.abs(sig) ** 2, targets=targets,
                clutter=clutter)


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def rayleigh_threshold(pfa, noise_w=1.0):
    """Module 1 (the exact inverse) — the amplitude threshold T such that
    noise alone crosses it with probability pfa.

    noise_w is the mean-square envelope — the same noise power the lecture-1
    budget computes as k*T0*B*F. Hour 2 derived the Rayleigh false-alarm
    closed form; invert it on paper first, then type the one line. Mind
    which sigma the formula wants: the per-channel one, not the power.
    """
    raise NotImplementedError


def monte_carlo_pfa(threshold_amp, noise_w=1.0, n_trials=1_000_000, seed=141):
    """Module 1 (the measurement) — draw n_trials envelope samples of pure
    receiver noise (complex Gaussian, total power noise_w), count how many
    cross threshold_amp, return the measured P_fa (a float).

    Use np.random.default_rng(seed) so the run is reproducible. The point
    of this function is that it does NOT trust module 1's formula — it
    watches the noise do what the formula claims.
    """
    raise NotImplementedError


def albersheim_snr_db(pd, pfa, n_pulses=1):
    """Module 2 (the workhorse) — Albersheim's approximation: the single- or
    N-pulse SNR (dB, per pulse) required for (pd, pfa) with a linear
    detector and a nonfluctuating target. The formula is on the hour-2
    slide (and in HOMEWORK.md). Published accuracy: ~0.2 dB for
    1e-7 <= pfa <= 1e-3, 0.1 <= pd <= 0.9, 1 <= N <= 8096.
    """
    raise NotImplementedError


def monte_carlo_pd(snr_db, pfa, n_trials=200_000, seed=1414):
    """Module 2 (the measurement) — measured P_d: plant a nonfluctuating
    target of the given SNR in complex noise (unit noise power), envelope-
    detect, compare against YOUR rayleigh_threshold(pfa), return the
    fraction detected. Reproducible via the seed.
    """
    raise NotImplementedError


def honest_ranges(radar, targets, pd, pfa):
    """Module 2 (the payoff) — lecture 1's detection ranges, redone
    honestly: replace the bare 13 dB bar with the SNR that Albersheim says
    (pd, pfa) actually costs, and return {name: max range in meters} using
    the toolkit's closed-form inverse.
    """
    raise NotImplementedError


def ca_cfar(power_profile, n_train, n_guard, pfa):
    """Module 3 (the core) — cell-averaging CFAR on a square-law POWER
    profile.

    For each cell under test: estimate the local noise as the mean of
    n_train training cells on EACH side, separated from the cell by
    n_guard guard cells on each side; scale the estimate by the multiplier
    that buys the design pfa (hour 2's closed-form alpha — the toolkit's
    cfar_alpha is the referee, so derive/reuse it consciously); declare a
    detection where the cell's power exceeds the threshold.

    Contract (lecture 15 imports this exact interface):
      power_profile : 1-D array, square-law power samples
      n_train       : training cells per side
      n_guard       : guard cells per side
      pfa           : per-cell design false-alarm probability
      returns       : (detections, threshold) — boolean array and float
                      array, both the same length as power_profile
    At the array edges, use the training cells that exist (truncate the
    window) and recompute alpha for the actual count, so the design pfa
    holds everywhere.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
_EXACT_T1 = np.sqrt(np.log(1e6))          # planted truth: T(pfa=1e-6, N=1 W)


def _edge_ensemble(cfar_fn, n_train, n_guard, pfa, n_tiles=800, seed=1441):
    """Q1's instrument: many clutter edges, measured per-zone false-alarm
    rates. Tiles of 150 clear + 150 clutter (30 dB) cells, no targets; every
    detection is a false alarm. Returns (rates dict, FAs per edge crossed).
    """
    rng = np.random.default_rng(seed)
    n = n_tiles * 300
    floor = np.tile(np.concatenate([np.ones(150), np.full(150, 1e3)]),
                    n_tiles)
    power = (np.abs((rng.standard_normal(n) + 1j * rng.standard_normal(n))
                    * np.sqrt(0.5)) ** 2) * floor
    det, _ = cfar_fn(power, n_train, n_guard, pfa)
    pos = np.arange(n) % 300
    w = n_train + n_guard
    zones = {"clear": (pos >= 30) & (pos < 140),
             "edge": (pos >= 150) & (pos < 150 + w),
             "deep clutter": (pos >= 200) & (pos < 290),
             "blind (after clutter)": pos < w}
    rates = {z: float(det[mask].mean()) for z, mask in zones.items()}
    per_edge = float(det[zones["edge"]].sum()) / n_tiles
    return rates, per_edge


def _scene_verdict(scene, det):
    """Hits / misses / false alarms of a detection map vs planted truth."""
    target_cells = {c for c, _ in scene["targets"]}
    hits = sorted(c for c in target_cells if det[c])
    misses = sorted(c for c in target_cells if not det[c])
    fa = sorted(int(i) for i in np.flatnonzero(det) if i not in target_cells)
    return hits, misses, fa


def run_checks(mods=None):
    m = mods or dict(rayleigh_threshold=rayleigh_threshold,
                     monte_carlo_pfa=monte_carlo_pfa,
                     albersheim_snr_db=albersheim_snr_db,
                     monte_carlo_pd=monte_carlo_pd,
                     honest_ranges=honest_ranges,
                     ca_cfar=ca_cfar)
    print("=" * 66)
    print("hw14 --check : measured facts (instrument, not grade)")
    print("=" * 66)

    # --- module 1: the threshold and the measured P_fa ---------------------
    print("\n[module 1] rayleigh_threshold / monte_carlo_pfa")
    try:
        t = float(m["rayleigh_threshold"](1e-6, 1.0))
        print(f"  T(pfa=1e-6, noise 1 W) = {t:.6f}"
              f"   | vs exact Rayleigh inverse: d = {t - _EXACT_T1:+.2e}")
        print(f"  threshold sits {db(t**2):.2f} dB above the mean noise power"
              f"   ({t / 1.0:.3f}x the rms envelope)")
        for pfa, seed in ((1e-2, 141), (1e-3, 142), (1e-6, 143)):
            thr = float(m["rayleigh_threshold"](pfa, 1.0))
            meas = float(m["monte_carlo_pfa"](thr, 1.0,
                                              DETECTION["n_trials_pfa"], seed))
            n = DETECTION["n_trials_pfa"]
            bar = binom_3sigma(pfa, n)
            inside = "inside" if abs(meas - pfa) <= bar else "OUTSIDE"
            print(f"  design pfa = {pfa:7.0e}: measured {meas:.2e} "
                  f"({int(round(meas * n))} of {n:.0e} trials)  "
                  f"| 3-sigma band +/-{bar:.1e} -> {inside}")
        print("  (at 1e-6 the expected count is 1 — to MEASURE a pfa you"
              " need >= ~10/pfa trials; Q3 material)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: Albersheim, Monte Carlo P_d, honest ranges --------------
    print("\n[module 2] albersheim_snr_db / monte_carlo_pd / honest_ranges")
    try:
        m["albersheim_snr_db"](0.9, 1e-6)         # probe before any output
        print("  Albersheim vs exact (Marcum) — published envelope ~0.2 dB"
              " for 1e-7 <= pfa <= 1e-3, 0.1 <= pd <= 0.9:")
        for pd_, pfa_ in ((0.9, 1e-6), (0.5, 1e-6), (0.9, 1e-3), (0.1, 1e-7)):
            alb = float(m["albersheim_snr_db"](pd_, pfa_))
            ex = snr_required_exact_db(pd_, pfa_)
            note = "   <- the envelope's corner frays; measure, don't worship" \
                if abs(alb - ex) > 0.2 else ""
            print(f"    (pd={pd_:4.2f}, pfa={pfa_:7.0e}): "
                  f"Albersheim {alb:6.2f} dB, exact {ex:6.2f} dB, "
                  f"d = {alb - ex:+.3f} dB{note}")
        print("  Monte Carlo P_d vs exact, SNR 6..16 dB (2e5 trials/point):")
        worst_dpd, worst_ddb = 0.0, 0.0
        for i, snr in enumerate(range(6, 17, 2)):
            meas = float(m["monte_carlo_pd"](float(snr), 1e-6,
                                             200_000, 1414 + i))
            ex = float(marcum_pd(float(snr), 1e-6))
            worst_dpd = max(worst_dpd, abs(meas - ex))
            line = (f"    SNR = {snr:2d} dB: measured P_d = {meas:.4f}, "
                    f"exact {ex:.4f}, d = {meas - ex:+.4f}")
            if 0.1 <= meas <= 0.9:      # Albersheim's envelope: dB distance
                alb_at = float(m["albersheim_snr_db"](meas, 1e-6))
                line += f"   | Albersheim puts this P_d at {alb_at:.2f} dB" \
                        f" (d = {alb_at - snr:+.2f} dB)"
                worst_ddb = max(worst_ddb, abs(alb_at - snr))
            print(line)
        print(f"  worst |dP_d| vs exact = {worst_dpd:.4f}; worst horizontal"
              f" gap vs Albersheim (inside envelope) = {worst_ddb:.2f} dB")
        hr = m["honest_ranges"](COURSE_RADAR, TARGETS,
                                DETECTION["pd"], DETECTION["pfa"])
        snr_h = float(m["albersheim_snr_db"](DETECTION["pd"], DETECTION["pfa"]))
        print(f"  honest bar for (pd=0.9, pfa=1e-6): {snr_h:.2f} dB"
              f"   (lecture 1 hand-waved {COURSE_RADAR['snr_req_db']:.0f})")
        for name, sig in TARGETS.items():
            r13 = radar_max_range_m(COURSE_RADAR, sig)
            print(f"    {name:8s}: honest {hr[name] / 1e3:6.2f} km"
                  f"   (13 dB bar said {r13 / 1e3:6.2f} km,"
                  f"   x{hr[name] / r13:.4f})")
        pd_at_bar = float(marcum_pd(13.0, 1e-6))
        print(f"  at lecture 1's ranges (SNR = exactly 13 dB) the actual"
              f" P_d = {pd_at_bar:.4f} — the hand-wave was nearly honest,"
              " and now you know what it meant")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: CA-CFAR on the three scenes -----------------------------
    print("\n[module 3] ca_cfar")
    try:
        nt, ng, pfa = CFAR["n_train"], CFAR["n_guard"], CFAR["pfa"]
        m["ca_cfar"](np.ones(64), nt, ng, pfa)    # probe before any output
        a16 = cfar_alpha(2 * nt, pfa)
        print(f"  closed form: alpha(N=16, pfa=1e-6) = {a16:.3f}"
              f" ({db(a16):.2f} dB); known-noise multiplier ln(1e6) ="
              f" {np.log(1e6):.3f}; CFAR loss = {cfar_loss_db(16, pfa):.2f} dB"
              f" (N=32: {cfar_loss_db(32, pfa):.2f} dB)")
        # does the student's CFAR keep its P_fa promise? (measured rate)
        rng = np.random.default_rng(1440)
        n_noise = 200_000
        pure = np.abs((rng.standard_normal(n_noise)
                       + 1j * rng.standard_normal(n_noise))
                      * np.sqrt(0.5)) ** 2
        det, thr = m["ca_cfar"](pure, nt, ng, 1e-3)
        rate = det.mean()
        print(f"  measured CFAR P_fa on {n_noise:.0e} pure-noise cells at"
              f" design 1e-3: {rate:.2e} ({int(det.sum())} crossings;"
              f" 3-sigma band +/-{binom_3sigma(1e-3, n_noise):.1e})")
        mid = thr[100:-100]
        print(f"  mean threshold / mean noise = {mid.mean():.2f}"
              f"   (alpha(N=16, 1e-3) = {cfar_alpha(2 * nt, 1e-3):.2f})")
        for name in SCENES:
            sc = make_scene(name)
            det, thr = m["ca_cfar"](sc["power"], nt, ng, pfa)
            hits, misses, fa = _scene_verdict(sc, det)
            print(f"  scene {name:12s}: targets {sc['targets']}")
            print(f"    hits {hits}  misses {misses}  false alarms"
                  f" {len(fa)} {fa if len(fa) <= 12 else fa[:12] + ['...']}")
        # the masking control arm: same noise, strong drone deleted
        solo = make_scene("two_drones_solo")
        det_s, _ = m["ca_cfar"](solo["power"], nt, ng, pfa)
        print(f"    masking check: weak drone (cell 1006, 15 dB) alone ->"
              f" detected = {bool(det_s[1006])}; next to the 22 dB drone ->"
              f" detected = "
              f"{bool(m['ca_cfar'](make_scene('two_drones')['power'], nt, ng, pfa)[0][1006])}")
        # Q1's instrument: many edges, measured per-zone P_fa (design 1e-3
        # here so the counts are measurable), then double the window.
        print("  clutter-edge ensemble (800 edges, design pfa = 1e-3):")
        for nt_q in (nt, 2 * nt):
            rates, per_edge = _edge_ensemble(m["ca_cfar"], nt_q, ng, 1e-3)
            print(f"    n_train = {nt_q:2d}/side: "
                  + "  ".join(f"{z} {r:.1e}" for z, r in rates.items()))
            print(f"                     false alarms per edge crossed ="
                  f" {per_edge:.3f}; CFAR loss"
                  f" {cfar_loss_db(2 * nt_q, 1e-3):.2f} dB")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(rayleigh_threshold=rayleigh_threshold,
                     albersheim_snr_db=albersheim_snr_db,
                     monte_carlo_pd=monte_carlo_pd,
                     honest_ranges=honest_ranges,
                     ca_cfar=ca_cfar)
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.6))

    # --- picture 1: P_d vs SNR — Monte Carlo, Albersheim, exact (Q1) -------
    ax = axes[0, 0]
    try:
        snr = np.arange(6.0, 16.01, 1.0)
        ax.plot(snr, [marcum_pd(s, 1e-6) for s in snr], "k-", lw=1.2,
                label="exact (Marcum)")
        pd_grid = np.linspace(0.1, 0.9, 33)
        ax.plot([m["albersheim_snr_db"](p, 1e-6) for p in pd_grid], pd_grid,
                "--", label="Albersheim")
        meas = [float(m["monte_carlo_pd"](float(s), 1e-6, 100_000, 1450 + i))
                for i, s in enumerate(snr)]
        ax.plot(snr, meas, "o", ms=4, label="Monte Carlo (1e5)")
        ax.axhline(0.9, color="gray", ls=":", alpha=0.7)
        ax.set_xlabel("single-pulse SNR (dB)")
        ax.set_ylabel(r"$P_d$ at $P_{fa}=10^{-6}$")
        ax.set_title("detection is a probability, not a verdict")
        ax.legend()
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 2 not implemented")

    # --- picture 2: lecture 1's range curves, redrawn honestly (Q1) --------
    ax = axes[0, 1]
    try:
        r = np.linspace(1e3, 45e3, 700)
        hr = m["honest_ranges"](COURSE_RADAR, TARGETS,
                                DETECTION["pd"], DETECTION["pfa"])
        for name, sig in TARGETS.items():
            snr_r = radar_snr_db(COURSE_RADAR, sig, r)
            pd_r = np.array([marcum_pd(s, DETECTION["pfa"]) for s in snr_r])
            (ln,) = ax.plot(r / 1e3, pd_r, label=f"{name} ({sig} m$^2$)")
            ax.axvline(hr[name] / 1e3, color=ln.get_color(), ls="--",
                       alpha=0.5)
            ax.axvline(radar_max_range_m(COURSE_RADAR, sig) / 1e3,
                       color=ln.get_color(), ls=":", alpha=0.5)
        ax.axhline(DETECTION["pd"], color="k", ls=":", alpha=0.6,
                   label="$P_d$ = 0.9")
        ax.set_xlabel("range (km)")
        ax.set_ylabel("$P_d$")
        ax.set_title("honest ranges (--) vs the 13 dB bar (:)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 2 not implemented")

    # --- pictures 3+4: CFAR on the edge and masking scenes (Q2, Q4) --------
    for ax, name in ((axes[1, 0], "clutter_edge"), (axes[1, 1], "two_drones")):
        try:
            sc = make_scene(name)
            det, thr = m["ca_cfar"](sc["power"], CFAR["n_train"],
                                    CFAR["n_guard"], CFAR["pfa"])
            cells = np.arange(N_CELLS)
            ax.plot(cells, db(sc["power"]), lw=0.5, alpha=0.6,
                    label="power profile")
            ax.plot(cells, db(thr), "r-", lw=1.2, label="CFAR threshold")
            hit = np.flatnonzero(det)
            ax.plot(hit, db(sc["power"][hit]), "kv", ms=6,
                    label="detections")
            for c, s in sc["targets"]:
                ax.annotate(f"{s:.0f} dB", (c, db(sc["power"][c]) + 3),
                            fontsize=8, ha="center")
            if name == "two_drones":
                ax.set_xlim(900, 1100)
            ax.set_xlabel("range cell")
            ax.set_ylabel("power (dB re thermal)")
            ax.set_title(f"scene: {name}")
            ax.legend(fontsize=8, loc="upper left")
            ax.grid(True, alpha=0.3)
        except NotImplementedError:
            ax.set_title("module 3 not implemented")

    fig.tight_layout()
    fig.savefig("hw14_plots.png", dpi=130)
    print("wrote hw14_plots.png")
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
