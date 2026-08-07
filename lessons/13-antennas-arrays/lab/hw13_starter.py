"""Homework 13 starter — The aperture.

You implement the three modules marked TODO below. Everything else is the
toolkit: the course array, the two-target scene, the closed-form referees,
plotting, and the checker.

Run from this directory:

    python hw13_starter.py --check    # measured facts per module (the instrument)
    python hw13_starter.py --plot     # the four pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbi` are decibel quantities; `*_m`,
`*_hz` are SI; and — this lecture's own felony — `*_deg` / `*_rad` label
every angle. `np.sin` eats radians. Hour 3's deliberate bug is what happens
when it eats degrees instead.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
import warnings

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s
from scipy.optimize import minimize_scalar
from scipy.signal.windows import chebwin        # the DSP homecoming

# scipy warns that chebwin(at < 45 dB) is unsuitable for SPECTRAL ANALYSIS
# (its noise bandwidth stops growing monotonically). We are pointing
# antennas, not estimating PSDs; the -30 dB equal-ripple guarantee is
# exactly the property we want, and it holds. Silence the false alarm.
warnings.filterwarnings("ignore", message="This window is not suitable")

# ----------------------------------------------------------------------------
# The systems (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
def wavelength_m(f_hz):
    """Free-space wavelength lambda = c / f."""
    return C_M_S / np.asarray(f_hz, dtype=float)


# The course radar's next antenna: a 16-element uniform linear array (ULA)
# at 10 GHz, element spacing d = lambda/2 = 14.99 mm. Lecture 1 gave the
# radar a 33 dBi dish; this is the first slice of its electronically
# steered replacement (the full planar story is Q4).
COURSE_ARRAY = dict(
    f_hz=10e9,                          # X-band, lambda = 29.98 mm
    n=16,                               # element count
    d_m=wavelength_m(10e9) / 2.0,       # element spacing, m (= lambda/2)
)

# The two-target scene (module 2). Relative echo powers come straight from
# lecture 1's radar equation: airliner sigma = 40 m^2 at 10 km, drone
# sigma = 0.01 m^2 at 3.5 km (inside its 4.11 km detection range) —
#   P_drone/P_airliner = (0.01/40) x (10/3.5)^4  ->  -17.78 dB.
# 15 deg of separation puts the drone in the SIDELOBE region of both
# tapers (the -30 dB Chebyshev main lobe ends at 10.7 deg) — the contest
# is sidelobe floor vs drone echo, which is the point of module 2.
SCENE = dict(
    airliner=dict(theta_deg=0.0, p_db=0.0),
    drone=dict(theta_deg=15.0,
               p_db=-(10.0 * np.log10(40.0 / 0.01)
                      - 40.0 * np.log10(10.0 / 3.5))),
)

# The course pattern grid: 0.001 deg steps — fine enough that plain linear
# interpolation meets every accuracy target in this homework.
THETA_DEG = np.linspace(-90.0, 90.0, 180001)


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> decibels (re-provided; lecture 1's warm-up)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """Decibels -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def integrate_pattern_dbi(theta_deg, af_abs):
    """Directivity (dBi) of a linear-array pattern by integrating the
    sampled |AF| over the visible sphere.

    For an array of isotropic elements along the axis, the pattern depends
    only on the angle from the axis, so the sphere integral collapses to
    D = 2 |AF|_max^2 / integral(|AF(u)|^2 du), u = sin(theta) in [-1, 1].
    Feed it the full THETA_DEG grid, or the integral is missing energy.
    """
    u = np.sin(np.radians(np.asarray(theta_deg, dtype=float)))
    p = np.abs(np.asarray(af_abs, dtype=float)) ** 2
    d_lin = 2.0 * p.max() / np.trapz(p, u)
    return db(d_lin)


def scan_response_db(af_func, w, arr, scene, theta_scan_deg):
    """Receive-beam scan across the two-target scene (module 2's overlay).

    Steers a beam with weights `w` to every angle in theta_scan_deg and
    returns the total received power (dB, relative to the beam pointing
    straight at a 0 dB target). Uses YOUR array_factor via the identity
    AF(w, phases for target t, scan theta_s) = AF(w * v_t, -theta_s) where
    v_t is the target's steering phasor — plumbing, not physics.
    """
    ts = np.asarray(theta_scan_deg, dtype=float)
    k = 2.0 * np.pi / wavelength_m(arr["f_hz"])
    n_idx = np.arange(arr["n"])
    peak = np.abs(np.sum(np.abs(w))) ** 2          # beam-on-target reference
    y_lin = np.zeros_like(ts)
    for tgt in scene.values():
        v_t = np.exp(1j * k * arr["d_m"] * n_idx
                     * np.sin(np.radians(tgt["theta_deg"])))
        af = af_func(np.asarray(w) * v_t, arr["d_m"], arr["f_hz"], -ts)
        y_lin = y_lin + undb(tgt["p_db"]) * np.abs(af) ** 2 / peak
    return db(y_lin)


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def array_factor(w, d_m, f_hz, theta_deg, phases_rad=None):
    """Module 1 (the core) — complex array factor of an N-element linear
    array with complex weights `w` (length N), element spacing d_m, at
    angles theta_deg measured FROM BROADSIDE. Optional per-element phases
    phases_rad (length N) add to the geometric phase — module 3 steers
    with them. Vectorized over theta_deg; returns the raw complex sum
    (do not normalize here — the diagnostics normalize).

    Convention (the toolkit's scan overlay relies on it): element n sits
    at x = n*d, so its geometric phase is +k*d*n*sin(theta); steering to
    theta0 therefore uses phases_rad = -k*d*n*sin(theta0).

    Hour 2 derived this twice; hour 3 wrote it in ten lines. Radians into
    np.sin — hour 3's deliberate bug is the other choice.
    """
    raise NotImplementedError


def pattern_stats(theta_deg, af_abs):
    """Module 1 — measured diagnostics from a SAMPLED pattern (no closed
    forms in here; the closed forms are the instrument's job). Return a
    dict with keys:

      peak_deg   : angle of the pattern maximum
      hpbw_deg   : -3 dB (half-power) beamwidth of the main lobe,
                   interpolated between grid points
      sll_db     : highest sidelobe relative to the main-lobe peak (dB, <0)
      alarm_deg  : list of angles of secondary lobes within 3 dB of the
                   peak — the grating-lobe alarm (empty list when clean)
    """
    raise NotImplementedError


def taper_study(arr=COURSE_ARRAY):
    """Module 2 — uniform vs -30 dB Chebyshev (scipy chebwin(n, at=30)).

    For each taper: evaluate YOUR array_factor on THETA_DEG, measure
    hpbw_deg / sll_db with YOUR pattern_stats, and get directivity from
    the toolkit's integrate_pattern_dbi. Return a dict:

      uniform    : dict(hpbw_deg, sll_db, d_dbi)
      cheb30     : dict(hpbw_deg, sll_db, d_dbi)
      broadening : cheb30 hpbw / uniform hpbw
      d_cost_db  : uniform d_dbi - cheb30 d_dbi
    """
    raise NotImplementedError


def steer_study(arr=COURSE_ARRAY, theta0_deg=45.0):
    """Module 3 — steer the beam to theta0_deg with a linear phase front,
    then measure what steering costs. Return a dict:

      peak_deg         : measured steered-beam peak angle (d = lambda/2)
      hpbw0_deg        : measured broadside HPBW (d = lambda/2)
      hpbw45_deg       : measured HPBW steered to theta0_deg (d = lambda/2)
      broadening       : hpbw45_deg / hpbw0_deg
      worst_at_half_db : worst secondary lobe at d = lambda/2, steered
                         (grating check: should still be ordinary sidelobe)
      d_max_m          : largest spacing with NO grating lobe when steered
                         to theta0_deg (closed form: d = lambda/(1+sin t0))
      grating_deg      : measured angle of the grating lobe at d = 0.65
                         lambda, steered to theta0_deg (from alarm_deg)
      grating_db       : its measured level relative to the main beam
    """
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# The referees below never look at your sampled pattern: closed forms for
# the uniform ULA (beamwidth, first-null, grating onset), the exact
# finite-N first sidelobe from the AF's own closed form, and chebwin's
# equal-ripple guarantee. Your measurements and these formulas are
# independent; if they disagree, one of you is wrong about the physics.
# ----------------------------------------------------------------------------
X_HALF_POWER = 1.39155738     # solves sin(x)/x = 1/sqrt(2)
SINC_SLL_DB = -13.2615        # first sidelobe of sin(x)/x — the N -> inf story


def _hpbw_closed_form_deg(n, d_m, f_hz, theta0_deg=0.0):
    """Uniform-ULA half-power beamwidth, closed form (Balanis 4e eq. 6-22
    generalized to a steered beam in u = sin(theta) space)."""
    lam = wavelength_m(f_hz)
    s0 = np.sin(np.radians(theta0_deg))
    du = X_HALF_POWER * lam / (np.pi * n * d_m)
    hi = np.degrees(np.arcsin(np.clip(s0 + du, -1.0, 1.0)))
    lo = np.degrees(np.arcsin(np.clip(s0 - du, -1.0, 1.0)))
    return hi - lo


def _first_null_deg(n, d_m, f_hz):
    """Broadside first null: sin(theta) = lambda / (N d)."""
    return np.degrees(np.arcsin(wavelength_m(f_hz) / (n * d_m)))


def _first_sll_exact_db(n):
    """Exact first-sidelobe level of the uniform N-element AF, from the
    closed form sin(N psi/2) / (N sin(psi/2)) — NOT the sinc asymptote.
    The finite-N denominator (N sin instead of N x) lifts the sidelobe;
    at N = 16 the correction is about +0.11 dB."""
    def neg_af(x):                                  # x = psi/2
        return -abs(np.sin(n * x) / (n * np.sin(x)))
    res = minimize_scalar(neg_af, bounds=(np.pi / n, 2 * np.pi / n),
                          method="bounded",
                          options=dict(xatol=1e-12))
    return float(db((-res.fun) ** 2))


def _grating_angle_deg(d_m, f_hz, theta0_deg):
    """Grating-lobe angle when steered to theta0: sin(theta_g) =
    sin(theta0) - lambda/d (the first one to enter visible space on the
    far side). Returns None while it is still outside sin = +/-1."""
    s = np.sin(np.radians(theta0_deg)) - wavelength_m(f_hz) / d_m
    if abs(s) > 1.0:
        return None
    return float(np.degrees(np.arcsin(s)))


def _fmt(x, unit="", w=8, p=2):
    return f"{x:{w}.{p}f}{unit}"


def run_checks(mods=None):
    m = mods or dict(array_factor=array_factor, pattern_stats=pattern_stats,
                     taper_study=taper_study, steer_study=steer_study)
    arr = COURSE_ARRAY
    print("=" * 64)
    print("hw13 --check : measured facts (instrument, not grade)")
    print("=" * 64)
    print(f"array: N = {arr['n']}, f = {arr['f_hz']/1e9:.0f} GHz, "
          f"d = {arr['d_m']*1e3:.4f} mm = lambda/2")

    # --- module 1: the AF engine and its diagnostics -----------------------
    print("\n[module 1] array_factor / pattern_stats  (uniform, broadside)")
    try:
        w = np.ones(arr["n"])
        af = np.abs(m["array_factor"](w, arr["d_m"], arr["f_hz"], THETA_DEG))
        st = m["pattern_stats"](THETA_DEG, af)
        hp_ref = _hpbw_closed_form_deg(arr["n"], arr["d_m"], arr["f_hz"])
        sll_ref = _first_sll_exact_db(arr["n"])
        print(f"  peak at {st['peak_deg']:+7.3f} deg  "
              f"(broadside; |AF|max = {af.max():.4f}, N = {arr['n']})")
        print(f"  HPBW = {st['hpbw_deg']:.4f} deg   | closed form "
              f"{hp_ref:.4f} -> rel err "
              f"{abs(st['hpbw_deg']-hp_ref)/hp_ref*100:.3f}%")
        print(f"  SLL  = {st['sll_db']:.4f} dB  | exact finite-N referee "
              f"{sll_ref:.4f} -> d = {st['sll_db']-sll_ref:+.2e} dB")
        print(f"    (sinc asymptote {SINC_SLL_DB} dB — the finite-N "
              f"correction is {st['sll_db']-SINC_SLL_DB:+.2f} dB at N=16)")
        print(f"  first null: formula asin(lambda/Nd) = "
              f"{_first_null_deg(arr['n'], arr['d_m'], arr['f_hz']):.3f} deg")
        print(f"  grating alarm (secondary lobes within 3 dB of peak): "
              f"{st['alarm_deg'] if st['alarm_deg'] else 'none'}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the taper study -----------------------------------------
    print("\n[module 2] taper_study  (uniform vs chebwin(16, at=30))")
    try:
        ts = m["taper_study"](arr)
        u_, c_ = ts["uniform"], ts["cheb30"]
        print(f"  uniform: HPBW {u_['hpbw_deg']:.4f} deg, "
              f"SLL {u_['sll_db']:.2f} dB, D = {u_['d_dbi']:.4f} dBi"
              f"   | invariant D = N: delta = "
              f"{u_['d_dbi'] - db(arr['n']):+.2e} dB")
        print(f"  cheb30 : HPBW {c_['hpbw_deg']:.4f} deg, "
              f"SLL {c_['sll_db']:.2f} dB, D = {c_['d_dbi']:.4f} dBi"
              f"   | chebwin guarantee -30 dB: delta = "
              f"{c_['sll_db'] + 30.0:+.3f} dB")
        print(f"  beamwidth cost: x{ts['broadening']:.4f}"
              f"   directivity cost: {ts['d_cost_db']:.4f} dB")
        # the two-target overlay, measured at the drone's direction
        drone = SCENE["drone"]["theta_deg"]
        sel = np.abs(THETA_DEG - drone) <= 2.0
        for name, wts in (("uniform", np.ones(arr["n"])),
                          ("cheb30", chebwin(arr["n"], at=30.0))):
            y = scan_response_db(m["array_factor"], wts, arr, SCENE,
                                 THETA_DEG)
            y_air = scan_response_db(m["array_factor"], wts, arr,
                                     dict(airliner=SCENE["airliner"]),
                                     THETA_DEG)
            bump = y[sel].max()
            floor = y_air[sel].max()
            verdict = "revealed" if bump - floor > 3.0 else "buried"
            print(f"  scene/{name:7s}: drone-direction response "
                  f"{bump:6.2f} dB vs airliner-only floor {floor:6.2f} dB"
                  f" -> {verdict} (margin {bump-floor:+.2f} dB)")
        print(f"    (drone echo is {SCENE['drone']['p_db']:.2f} dB "
              f"vs airliner — lecture 1 arithmetic, see SCENE)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: steering ------------------------------------------------
    print("\n[module 3] steer_study  (scan to 45 deg)")
    try:
        ss = m["steer_study"](arr, 45.0)
        hp45_ref = _hpbw_closed_form_deg(arr["n"], arr["d_m"], arr["f_hz"],
                                         45.0)
        lam = wavelength_m(arr["f_hz"])
        print(f"  steered peak at {ss['peak_deg']:7.3f} deg  (asked: 45)")
        print(f"  HPBW broadside {ss['hpbw0_deg']:.4f} deg -> at 45 deg "
              f"{ss['hpbw45_deg']:.4f} deg   | closed form {hp45_ref:.4f}"
              f" -> rel err "
              f"{abs(ss['hpbw45_deg']-hp45_ref)/hp45_ref*100:.3f}%")
        print(f"  broadening x{ss['broadening']:.4f}"
              f"   (1/cos(45 deg) = {1/np.cos(np.radians(45)):.4f};"
              f" exact arcsin form is the referee)")
        print(f"  d = lambda/2 steered: worst secondary lobe "
              f"{ss['worst_at_half_db']:.2f} dB — no grating lobe")
        print(f"  no-grating spacing limit: d_max = {ss['d_max_m']*1e3:.4f}"
              f" mm = {ss['d_max_m']/lam:.4f} lambda"
              f"   (formula lambda/(1+sin 45) = "
              f"{lam/(1+np.sin(np.radians(45)))*1e3:.4f} mm)")
        g_ref = _grating_angle_deg(0.65 * lam, arr["f_hz"], 45.0)
        print(f"  d = 0.65 lambda steered 45: grating lobe measured at "
              f"{ss['grating_deg']:8.3f} deg, {ss['grating_db']:6.2f} dB"
              f"   | formula {g_ref:8.3f} deg -> d = "
              f"{abs(ss['grating_deg']-g_ref):.4f} deg")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(array_factor=array_factor, pattern_stats=pattern_stats,
                     taper_study=taper_study, steer_study=steer_study)
    arr = COURSE_ARRAY
    lam = wavelength_m(arr["f_hz"])
    n_idx = np.arange(arr["n"])
    k = 2.0 * np.pi / lam
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2))

    def norm_db(af_abs):
        return 20.0 * np.log10(np.maximum(np.abs(af_abs), 1e-12)
                               / np.abs(af_abs).max())

    # --- picture 1: uniform vs Chebyshev pattern (Q1's picture) ------------
    try:
        for name, wts in (("uniform", np.ones(arr["n"])),
                          ("chebwin -30 dB", chebwin(arr["n"], at=30.0))):
            af = m["array_factor"](wts, arr["d_m"], arr["f_hz"], THETA_DEG)
            axes[0, 0].plot(THETA_DEG, norm_db(af), label=name, lw=1.2)
        axes[0, 0].axhline(-13.15, color="gray", ls=":", alpha=0.7)
        axes[0, 0].axhline(-30, color="gray", ls=":", alpha=0.7)
        axes[0, 0].set_ylim(-60, 2)
        axes[0, 0].set_xlim(-90, 90)
        axes[0, 0].set_title("the taper trade: sidelobes vs beamwidth")
        axes[0, 0].legend(loc="upper right", fontsize=9)
    except NotImplementedError:
        axes[0, 0].set_title("module 1 not implemented")

    # --- picture 2: the two-target overlay (Q3's picture) ------------------
    try:
        for name, wts in (("uniform", np.ones(arr["n"])),
                          ("chebwin -30 dB", chebwin(arr["n"], at=30.0))):
            y = scan_response_db(m["array_factor"], wts, arr, SCENE,
                                 THETA_DEG)
            axes[0, 1].plot(THETA_DEG, y, label=name, lw=1.2)
        axes[0, 1].axvline(SCENE["drone"]["theta_deg"], color="k", ls="--",
                           alpha=0.5)
        axes[0, 1].annotate("drone here",
                            (SCENE["drone"]["theta_deg"], -5),
                            textcoords="offset points", xytext=(8, 0),
                            fontsize=9)
        axes[0, 1].set_ylim(-45, 5)
        axes[0, 1].set_xlim(-40, 50)
        axes[0, 1].set_title("scan the beam: airliner at 0, drone at "
                             f"{SCENE['drone']['theta_deg']:.0f} deg "
                             f"({SCENE['drone']['p_db']:.1f} dB)")
        axes[0, 1].legend(loc="upper right", fontsize=9)
    except NotImplementedError:
        axes[0, 1].set_title("module 1 not implemented")

    # --- picture 3: steering at d = lambda/2 (Q2's picture) ----------------
    try:
        for t0 in (0.0, 25.0, 45.0):
            ph = -k * arr["d_m"] * n_idx * np.sin(np.radians(t0))
            af = m["array_factor"](np.ones(arr["n"]), arr["d_m"],
                                   arr["f_hz"], THETA_DEG, phases_rad=ph)
            axes[1, 0].plot(THETA_DEG, norm_db(af),
                            label=f"steered {t0:.0f} deg", lw=1.2)
        axes[1, 0].set_ylim(-40, 2)
        axes[1, 0].set_xlim(-90, 90)
        axes[1, 0].set_title("steering = linear phase (d = lambda/2: "
                             "beam broadens, no grating lobe)")
        axes[1, 0].legend(loc="lower left", fontsize=9)
    except NotImplementedError:
        axes[1, 0].set_title("module 1 not implemented")

    # --- picture 4: the d > lambda/2 crime (Q2's picture) ------------------
    try:
        for frac in (0.5, 0.65):
            d = frac * lam
            ph = -k * d * n_idx * np.sin(np.radians(45.0))
            af = m["array_factor"](np.ones(arr["n"]), d, arr["f_hz"],
                                   THETA_DEG, phases_rad=ph)
            axes[1, 1].plot(THETA_DEG, norm_db(af),
                            label=f"d = {frac} lambda", lw=1.2)
        g = _grating_angle_deg(0.65 * lam, arr["f_hz"], 45.0)
        axes[1, 1].axvline(g, color="k", ls="--", alpha=0.5)
        axes[1, 1].annotate(f"formula: {g:.2f} deg", (g, 1),
                            textcoords="offset points", xytext=(6, 2),
                            fontsize=9)
        axes[1, 1].set_ylim(-40, 2)
        axes[1, 1].set_xlim(-90, 90)
        axes[1, 1].set_title("steered to 45 deg: the grating lobe walks in")
        axes[1, 1].legend(loc="lower left", fontsize=9)
    except NotImplementedError:
        axes[1, 1].set_title("module 1 not implemented")

    for ax in axes.flat:
        ax.set_xlabel("theta from broadside (deg)")
        ax.set_ylabel("dB")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("hw13_plots.png", dpi=130)
    print("wrote hw13_plots.png")
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
