"""Homework 6 starter — The impossible spec.

You implement the three modules marked TODO below. Everything else is the
toolkit: the client's spec, the load models, the exact cascade sweep, the
synthetic resonator bench, the skrf referees, and the checker.

Run from this directory:

    python hw6_starter.py --check    # measured facts per module (the instrument)
    python hw6_starter.py --sweep    # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` is decibels; `*_hz`, `*_m`, `*_ohm`,
`*_farad` are SI. Return loss RL = -20*log10(|Gamma|) is a POSITIVE dB
number. |S21| in the coupling formula is LINEAR, never dB.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
import zlib

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s

# ----------------------------------------------------------------------------
# The job (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
# The client's matching spec: bring a 12.5-ohm load up to the 50-ohm world,
# 20 dB return loss, one full octave. f0 is the synchronous frequency: each
# transformer section is a quarter wave there.
CLIENT_SPEC = dict(
    z0_ohm=50.0,       # system impedance
    zl_ohm=12.5,       # the load (a 4:1 ratio -- this is what makes it hard)
    f1_hz=2.0e9,       # band start
    f2_hz=4.0e9,       # band end (an octave: f2 = 2*f1)
    f0_hz=3.0e9,       # synchronous frequency (f1+f2)/2; sections are λ/4 here
    rl_spec_db=20.0,   # required return loss everywhere in [f1, f2]
)

# Three versions of the client's load, for the Bode-Fano verdict (module 1).
# The 12.5-ohm termination always carries some shunt pad capacitance;
# how much decides whether the spec is physics or fiction.
LOAD_MODELS = {
    "ideal_pad":   0.0,      # farads -- the datasheet fantasy: pure 12.5 ohm
    "revised_pad": 2.2e-12,  # farads -- the client's respin, measured
    "first_board": 10e-12,   # farads -- the client's first board, measured
}

# The client's bench also sent three swept resonator measurements (module 3):
# candidate resonators for the oscillator that will sit behind this match.
# name: (f0_hz, q_u, insertion loss at resonance, dB). The generator below
# turns these into "measured" S21 sweeps with bench noise; your job is to
# get the numbers BACK out of the sweep, which is harder than putting them in.
RESONATOR_BENCH = {
    "A_microstrip_halfwave": (2.5e9, 150.0, 10.0),
    "B_coax_quarterwave":    (3.0e9, 800.0, 6.0),
    "C_cavity":              (3.6e9, 12000.0, 0.35),
}


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def rl_db(gamma):
    """|Gamma| (linear, scalar or array) -> return loss in POSITIVE dB."""
    return -20.0 * np.log10(np.abs(gamma))


def cheb_t(n, x):
    """Chebyshev polynomial T_n(x), valid inside AND outside |x| <= 1.
    (Outside, T_n(x) = cosh(n*arccosh|x|), signed. This is the polynomial
    whose flat-then-explosive growth the equal-ripple design exploits.)"""
    x = np.asarray(x, dtype=float)
    inside = np.cos(n * np.arccos(np.clip(x, -1.0, 1.0)))
    outside = np.cosh(n * np.arccosh(np.maximum(np.abs(x), 1.0)))
    out = np.where(np.abs(x) <= 1.0, inside, outside)
    return out * np.where(x < -1.0, (-1.0) ** n, 1.0)


def theta_m_rad(spec):
    """Band-edge electrical length theta_m = (pi/2)*(f1/f0). For this octave
    it is 60 degrees, and sec(theta_m) = 2."""
    return np.pi / 2.0 * spec["f1_hz"] / spec["f0_hz"]


def cascade_sweep_gamma(z_sections_ohm, f_hz, spec=CLIENT_SPEC):
    """EXACT input reflection coefficient of the transformer: ABCD cascade
    of the quarter-wave (at f0) sections, terminated in zl_ohm, referenced
    to z0_ohm. This is lecture 4's cascade machinery, provided. Returns
    complex Gamma(f)."""
    f = np.atleast_1d(np.asarray(f_hz, dtype=float))
    th = np.pi / 2.0 * f / spec["f0_hz"]
    gamma = np.empty_like(f, dtype=complex)
    for i, t in enumerate(th):
        abcd = np.eye(2, dtype=complex)
        for z in z_sections_ohm:
            abcd = abcd @ np.array(
                [[np.cos(t), 1j * z * np.sin(t)],
                 [1j * np.sin(t) / z, np.cos(t)]])
        zin = ((abcd[0, 0] * spec["zl_ohm"] + abcd[0, 1])
               / (abcd[1, 0] * spec["zl_ohm"] + abcd[1, 1]))
        gamma[i] = (zin - spec["z0_ohm"]) / (zin + spec["z0_ohm"])
    return gamma


def band_f_hz(spec=CLIENT_SPEC, npts=801):
    """A frequency grid covering exactly the specified band [f1, f2]."""
    return np.linspace(spec["f1_hz"], spec["f2_hz"], npts)


def worst_inband_rl_db(z_sections_ohm, spec=CLIENT_SPEC, npts=801):
    """Worst-case (minimum) return loss of the exact cascade over the band."""
    g = cascade_sweep_gamma(z_sections_ohm, band_f_hz(spec, npts), spec)
    return float(rl_db(np.abs(g).max()))


def resonator_dataset(name):
    """One 'bench measurement': (f_hz, s21) for a transmission-coupled
    resonator, 801 points, small fixed-seed bench noise. Deterministic."""
    f0_hz, q_u, il_db = RESONATOR_BENCH[name]
    d = 10.0 ** (-il_db / 20.0)              # |S21| at resonance (linear)
    q_l = q_u * (1.0 - d)                    # loading by the two couplings
    bw_hz = f0_hz / q_l
    f = np.linspace(f0_hz - 6.0 * bw_hz, f0_hz + 6.0 * bw_hz, 801)
    x = f / f0_hz - f0_hz / f                # exact detuning, not narrowband
    s21 = d / (1.0 + 1j * q_l * x)
    rng = np.random.default_rng(zlib.crc32(name.encode()))  # deterministic
    s21 = s21 + 5e-4 * (rng.standard_normal(f.size)
                        + 1j * rng.standard_normal(f.size))
    return f, s21


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def bode_fano_best_rl_db(r_ohm, c_farad, f1_hz, f2_hz):
    """Module 1 — the physics ceiling. For a parallel-RC load, the Bode-Fano
    criterion caps the reflection budget:

        integral_0^inf ln(1/|Gamma|) d(omega)  <=  pi / (R*C)

    Spend the whole budget uniformly on [f1, f2] (|Gamma| = Gamma_m in band,
    1 outside — the best any matching network can even aim for) and return
    the best achievable return loss in dB. Return np.inf when c_farad == 0
    (no stored energy, no ceiling)."""
    raise NotImplementedError


def bode_fano_max_c_farad(r_ohm, f1_hz, f2_hz, rl_spec_db):
    """Module 1 — the same ceiling read backwards: the largest shunt C
    (farads) for which rl_spec_db over [f1, f2] is still physically
    possible. One line once you have the budget equation on paper."""
    raise NotImplementedError


def cheb_gamma_m(n, spec=CLIENT_SPEC):
    """Module 2 (the core) — small-reflection Chebyshev theory: the in-band
    ripple |Gamma_m| of an n-section transformer over the spec band.

    Theory of small reflections (lecture + Pozar 5.7):
        Gamma_m * T_n(sec theta_m) = (1/2) |ln(zl/z0)|
    Use the toolkit's cheb_t and theta_m_rad."""
    raise NotImplementedError


def cheb_min_n(spec=CLIENT_SPEC):
    """Module 2 (the core) — the smallest n whose THEORY ripple meets the
    spec: rl_db(cheb_gamma_m(n)) >= spec['rl_spec_db']. (Whether the exact
    sweep of that design agrees is the whole point of this homework —
    the checker measures it.)"""
    raise NotImplementedError


def cheb_transformer(n, spec=CLIENT_SPEC):
    """Module 2 (the core) — design the n-section Chebyshev transformer by
    the small-reflection recursion. Return the n section impedances (ohms),
    ordered from the z0 side to the zl side.

    The recipe (lecture 1.4 / Pozar 5.7): write
        Gamma(theta) = 2 e^{-j n theta} [G0 cos(n theta) + G1 cos((n-2)theta)
                        + ...]   (even-n middle term counts ONCE, not twice)
    match it to  Gamma_m * T_n(sec(theta_m) * cos(theta))  term by term to
    get the partial reflections G_k, then step the impedances:
        ln(Z_{k+1}/Z_k) = 2*G_k
    HOW you expand T_n(sec*cos theta) into cos multiples is your choice —
    the slide-11 identities (n <= 3), a symbolic tool, or a numeric
    cosine-series projection all work. Two invariants to check yourself:
    sum of all steps: 2*sum(G_k) = ln(zl/z0); and symmetry G_k = G_{n-k}.
    Mind the sign — this load steps DOWN."""
    raise NotImplementedError


def q_extract_3db(f_hz, s21):
    """Module 3 — the 3-dB method, done honestly. From a swept transmission
    S21 of a resonator, extract and return a dict with keys:
        f0_hz    : resonant frequency (peak of |S21|)
        q_l      : LOADED Q = f0 / (3-dB bandwidth)  — what the sweep gives
        q_u      : UNLOADED Q = q_l / (1 - |S21(f0)|)  — |S21(f0)| LINEAR
        s21_peak : |S21(f0)|, linear
    Interpolate the half-power crossings (|S21| = peak/sqrt(2)) between
    samples; the grid alone is too coarse for the 2% agreement the checker
    measures. The coupling correction is the whole difference between
    reporting the resonator and slandering it (dataset C)."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Two independent referees: scikit-rf re-sweeps your transformer as a real
# cascade of Network objects (media -> line -> renormalize -> **), and
# skrf.qfactor.Qfactor re-fits your resonators by the NLQFIT6 method of
# NPL report MAT 58 — a fitting method that shares no code and no idea
# with your 3-dB ruler. Agreement is evidence; disagreement is a lead.
# ----------------------------------------------------------------------------
def _skrf_cascade_referee(z_sections_ohm, f_hz, spec=CLIENT_SPEC):
    """|Gamma(f)| of the transformer, computed entirely inside scikit-rf:
    ideal lines (DefinedGammaZ0, vp = c), quarter-wave at f0, renormalized
    to z0 and cascaded with **, terminated in the load. No ABCD of ours."""
    import skrf as rf
    from skrf.media import DefinedGammaZ0

    freq = rf.Frequency.from_f(np.asarray(f_hz, dtype=float), unit="hz")
    l_m = C_M_S / spec["f0_hz"] / 4.0        # quarter wave at f0, vp = c
    gamma_prop = 1j * 2.0 * np.pi * freq.f / C_M_S
    total = None
    for z in z_sections_ohm:
        med = DefinedGammaZ0(frequency=freq, z0=z, gamma=gamma_prop)
        line = med.line(l_m, unit="m")
        line.renormalize(spec["z0_ohm"])
        total = line if total is None else total ** line
    med0 = DefinedGammaZ0(frequency=freq, z0=spec["z0_ohm"], gamma=gamma_prop)
    load = med0.load((spec["zl_ohm"] - spec["z0_ohm"])
                     / (spec["zl_ohm"] + spec["z0_ohm"]))
    return np.abs((total ** load).s[:, 0, 0])


def _skrf_qfactor_referee(f_hz, s21):
    """(q_l, q_u, f0_hz) fitted by skrf.qfactor.Qfactor (MAT 58 NLQFIT6).
    Transmission resonance type; Q_unloaded needs the scaling factor A=1
    (S21 here is already calibrated: through-line = 1)."""
    import skrf as rf
    from skrf.qfactor import Qfactor

    freq = rf.Frequency.from_f(np.asarray(f_hz, dtype=float), unit="hz")
    ntwk = rf.Network(frequency=freq, s=np.asarray(s21).reshape(-1, 1, 1),
                      z0=50.0)
    qf = Qfactor(ntwk, res_type="transmission")
    res = qf.fit()
    return float(qf.Q_L), float(qf.Q_unloaded(res, A=1.0)), float(qf.f_L)


def run_checks(mods=None):
    m = mods or dict(bode_fano_best_rl_db=bode_fano_best_rl_db,
                     bode_fano_max_c_farad=bode_fano_max_c_farad,
                     cheb_gamma_m=cheb_gamma_m, cheb_min_n=cheb_min_n,
                     cheb_transformer=cheb_transformer,
                     q_extract_3db=q_extract_3db)
    spec = CLIENT_SPEC
    print("=" * 64)
    print("hw6 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: Bode-Fano feasibility verdict ---------------------------
    print("\n[module 1] bode_fano_best_rl_db / bode_fano_max_c_farad")
    try:
        for name, c_f in LOAD_MODELS.items():
            best = float(m["bode_fano_best_rl_db"](
                spec["zl_ohm"], c_f, spec["f1_hz"], spec["f2_hz"]))
            verdict = ("no ceiling" if np.isinf(best) else
                       f"ceiling {best:6.2f} dB -> spec "
                       + ("FEASIBLE" if best >= spec["rl_spec_db"]
                          else "IMPOSSIBLE — no network can do it"))
            print(f"  {name:13s} C = {c_f*1e12:5.1f} pF: {verdict}")
        cmax = float(m["bode_fano_max_c_farad"](
            spec["zl_ohm"], spec["f1_hz"], spec["f2_hz"],
            spec["rl_spec_db"]))
        print(f"  largest C that keeps {spec['rl_spec_db']:.0f} dB over the"
              f" octave physical: {cmax*1e12:.3f} pF")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the Chebyshev designer ----------------------------------
    print("\n[module 2] cheb_gamma_m / cheb_min_n / cheb_transformer")
    try:
        print("  theory ripple (small reflections) vs exact swept cascade:")
        for n in (1, 2, 3, 4):
            gm = float(m["cheb_gamma_m"](n, spec))
            z = np.asarray(m["cheb_transformer"](n, spec), dtype=float)
            worst = worst_inband_rl_db(z, spec)
            print(f"    N={n}: theory RL = {rl_db(gm):6.2f} dB | exact sweep"
                  f" worst in-band RL = {worst:6.2f} dB"
                  f"  (gap {rl_db(gm) - worst:+5.2f} dB)")
        nmin = int(m["cheb_min_n"](spec))
        z = np.asarray(m["cheb_transformer"](nmin, spec), dtype=float)
        print(f"  minimum N by THEORY = {nmin}; its section impedances:"
              f" {np.round(z, 3)} ohm")
        step_sum = np.log(np.prod(
            np.r_[z, spec['zl_ohm']] / np.r_[spec['z0_ohm'], z]))
        print(f"  invariant sum(ln steps) = {step_sum:+.6f}"
              f"  (ln(zl/z0) = {np.log(spec['zl_ohm']/spec['z0_ohm']):+.6f})")
        worst = worst_inband_rl_db(z, spec)
        print(f"  exact sweep of that design: worst in-band RL ="
              f" {worst:.2f} dB vs the {spec['rl_spec_db']:.0f} dB spec"
              f" -> {'MEETS' if worst >= spec['rl_spec_db'] else 'MISSES'}")
        # find the minimum N that the EXACT sweep certifies
        n_sweep = next(nn for nn in range(1, 9) if worst_inband_rl_db(
            np.asarray(m["cheb_transformer"](nn, spec), dtype=float), spec)
            >= spec["rl_spec_db"])
        print(f"  minimum N by EXACT SWEEP = {n_sweep}  <- the deliverable")
        # referee: skrf re-sweeps the sweep-certified design
        zbest = np.asarray(m["cheb_transformer"](n_sweep, spec), dtype=float)
        f_band = band_f_hz(spec)
        g_hand = np.abs(cascade_sweep_gamma(zbest, f_band, spec))
        g_skrf = _skrf_cascade_referee(zbest, f_band, spec)
        print(f"  skrf cascade referee, N={n_sweep}: max |Gamma| delta ="
              f" {np.abs(g_hand - g_skrf).max():.2e}"
              f"  (worst RL {rl_db(g_skrf.max()):.2f} dB)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the resonator lab ---------------------------------------
    print("\n[module 3] q_extract_3db  (vs skrf.qfactor MAT58 fit)")
    try:
        for name in RESONATOR_BENCH:
            f, s21 = resonator_dataset(name)
            ext = m["q_extract_3db"](f, s21)
            ql_fit, qu_fit, f0_fit = _skrf_qfactor_referee(f, s21)
            dql = (ext["q_l"] / ql_fit - 1.0) * 100.0
            dqu = (ext["q_u"] / qu_fit - 1.0) * 100.0
            print(f"  {name:22s} |S21(f0)| = {ext['s21_peak']:.3f}"
                  f"  Q_L = {ext['q_l']:8.1f} ({dql:+.2f}% vs fit)"
                  f"  Q_u = {ext['q_u']:8.1f} ({dqu:+.2f}% vs fit)")
        f, s21 = resonator_dataset("C_cavity")
        ext = m["q_extract_3db"](f, s21)
        print(f"  the trap, quantified: C_cavity Q_u / Q_L ="
              f" {ext['q_u']/ext['q_l']:.1f}x — the 3-dB number alone"
              f" understates the cavity by that factor")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(cheb_transformer=cheb_transformer,
                     q_extract_3db=q_extract_3db)
    spec = CLIENT_SPEC
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    # --- picture 1: the transformer family vs the spec (Q1's picture) ------
    try:
        f = np.linspace(1e9, 5e9, 1201)
        for n in (1, 2, 3, 4):
            z = np.asarray(m["cheb_transformer"](n, spec), dtype=float)
            g = np.abs(cascade_sweep_gamma(z, f, spec))
            axes[0].plot(f / 1e9, rl_db(np.maximum(g, 1e-9)),
                         label=f"N = {n}")
        axes[0].axhline(spec["rl_spec_db"], color="k", ls=":", alpha=0.7,
                        label="20 dB spec")
        axes[0].axvspan(spec["f1_hz"] / 1e9, spec["f2_hz"] / 1e9,
                        color="tab:blue", alpha=0.08, label="the octave")
        axes[0].set_xlabel("frequency (GHz)")
        axes[0].set_ylabel("return loss (dB)")
        axes[0].set_ylim(0, 60)
        axes[0].set_title("Chebyshev 50 → 12.5 Ω: exact swept cascades")
        axes[0].legend(loc="upper right", fontsize=8)
        axes[0].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 2 not implemented")

    # --- picture 2: the three resonators (Q2's picture) --------------------
    try:
        for name in RESONATOR_BENCH:
            f, s21 = resonator_dataset(name)
            ext = m["q_extract_3db"](f, s21)
            bw = ext["f0_hz"] / ext["q_l"]
            x = (f - ext["f0_hz"]) / bw
            axes[1].plot(x, 20 * np.log10(np.abs(s21)),
                         label=f"{name.split('_')[0]}: "
                               f"Q_L={ext['q_l']:.0f}, Q_u={ext['q_u']:.0f}")
        axes[1].set_xlabel("detuning from f₀ (3-dB bandwidths)")
        axes[1].set_ylabel("|S21| (dB)")
        axes[1].set_xlim(-6, 6)
        axes[1].set_title("three resonators on a common Q_L axis")
        axes[1].legend(loc="lower center", fontsize=8)
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 3 not implemented")

    fig.tight_layout()
    fig.savefig("hw6_sweep.png", dpi=130)
    print("wrote hw6_sweep.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--sweep", action="store_true",
                    help="the two pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.sweep:
        make_plots()
    if not (args.check or args.sweep):
        print(__doc__)


if __name__ == "__main__":
    main()
