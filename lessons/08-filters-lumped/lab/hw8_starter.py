"""Homework 8 starter — Clean the band.

You implement the three modules marked TODO below. Everything else is the
toolkit: the spec, ABCD machinery, the scipy element-extraction referee,
the skrf ladder referee, plotting, and the checker.

Run from this directory:

    python hw8_starter.py --check    # measured facts per module (the instrument)
    python hw8_starter.py --sweep    # S21/S11 + group delay, the spec picture

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` are decibel quantities; `*_hz`, `*_ohm`,
henries and farads are SI. g-values are dimensionless prototype numbers.
Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np

# ----------------------------------------------------------------------------
# The spec (instructor side — what your filter is graded against)
# ----------------------------------------------------------------------------
# The course radar's IF (intermediate frequency) strip runs at 60 MHz. The
# frequency plan (lecture 12's business) parks two known aggressors at
# +-25 MHz from the center: the second mixer's image band and a co-site VHF
# comms transmitter. The IF bandpass filter must protect the strip:
SPEC = dict(
    f1_hz=55e6,          # lower passband edge
    f2_hz=65e6,          # upper passband edge (10 MHz passband on the 60 MHz IF)
    ripple_db=0.5,       # max attenuation anywhere in the passband
    stop_lo_hz=35e6,     # lower rejection point (center - 25 MHz)
    stop_hi_hz=85e6,     # upper rejection point (center + 25 MHz)
    reject_db=40.0,      # required rejection at BOTH stop frequencies
    r0_ohm=50.0,         # source and load impedance
)

# Default measurement grid for the sweep (55e6 and 65e6 land exactly on it).
F_SWEEP_HZ = np.linspace(20e6, 120e6, 8001)


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> dB. (You built this in hw1; provided here.)"""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """dB -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def abcd_series_z(z):
    """ABCD matrix of a series impedance z (complex array, shape (npts,)).
    Returns shape (npts, 2, 2)."""
    z = np.asarray(z, dtype=complex)
    m = np.zeros(z.shape + (2, 2), dtype=complex)
    m[..., 0, 0] = 1.0
    m[..., 0, 1] = z
    m[..., 1, 1] = 1.0
    return m


def abcd_shunt_y(y):
    """ABCD matrix of a shunt admittance y (complex array, shape (npts,))."""
    y = np.asarray(y, dtype=complex)
    m = np.zeros(y.shape + (2, 2), dtype=complex)
    m[..., 0, 0] = 1.0
    m[..., 1, 0] = y
    m[..., 1, 1] = 1.0
    return m


def abcd_cascade(*ms):
    """Cascade ABCD matrices left to right (source side first)."""
    out = ms[0]
    for m in ms[1:]:
        out = out @ m
    return out


def abcd_to_s(m, z0):
    """ABCD (npts, 2, 2) -> (s11, s21) with equal reference z0 both ports."""
    a, b = m[..., 0, 0], m[..., 0, 1]
    c, d = m[..., 1, 0], m[..., 1, 1]
    den = a + b / z0 + c * z0 + d
    return (a + b / z0 - c * z0 - d) / den, 2.0 / den


def group_delay_s(f_hz, s21):
    """Group delay tau_g = -d(phase)/d(omega) in seconds, from a swept S21."""
    phase = np.unwrap(np.angle(s21))
    return -np.gradient(phase, 2.0 * np.pi * np.asarray(f_hz, dtype=float))


def cheb_atten_db(n, ripple_db, omega):
    """Analytic Chebyshev attenuation 10*log10(1 + eps^2 * C_n^2(omega)) at
    prototype frequency omega (band edge = 1). The closed-form referee for
    your swept stopband numbers."""
    e2 = 10.0 ** (ripple_db / 10.0) - 1.0
    om = np.abs(np.asarray(omega, dtype=float))
    cn = np.where(om >= 1.0, np.cosh(n * np.arccosh(np.maximum(om, 1.0))),
                  np.cos(n * np.arccos(np.minimum(om, 1.0))))
    return 10.0 * np.log10(1.0 + e2 * cn ** 2)


# A known-good reference ladder so module 3 is checkable even if module 2
# is not done yet: a Butterworth N=3 bandpass at the classic 10.7 MHz FM IF
# (10.2-11.2 MHz, 50 ohm). Values precomputed; every branch tunes to
# sqrt(10.2 * 11.2) MHz = 10.6884 MHz.
REF_LADDER = [
    ("series", 7.957747155e-06, 2.786326035e-11),
    ("shunt",  3.482907543e-08, 6.366197724e-09),
    ("series", 7.957747155e-06, 2.786326035e-11),
]


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def g_values(family, n, ripple_db=None):
    """Module 1 (the core) — lowpass prototype element values by RECURSION.

    family is "butterworth" or "chebyshev"; n is the order; ripple_db is the
    passband ripple (chebyshev only). Return a length-(n+1) array:
    g1..gn are the ladder elements, g_{n+1} is the load. Butterworth comes
    from the closed form 2*sin(...); chebyshev from the beta/gamma recursion
    hour 1 derived. Not a lookup table — any n must work. The checker
    referees you against element extraction from scipy's prototypes.
    """
    raise NotImplementedError


def min_order(family, edge_atten_db, reject_db, omega_s):
    """Module 2 — smallest order whose prototype attenuation reaches
    reject_db at prototype frequency omega_s, given edge_atten_db of
    attenuation allowed at the band edge (omega = 1). Same contract for
    both families: for chebyshev, edge_atten_db is the ripple; for
    butterworth it pins where omega = 1 sits on the response. Return an int
    (hour 2 turned the nomogram into one closed form per family)."""
    raise NotImplementedError


def bandpass_ladder(gs, f1_hz, f2_hz, r0_ohm):
    """Module 2 — impedance/frequency scaling + lowpass->bandpass
    transformation. From prototype g-values, build the bandpass ladder for
    passband f1..f2 in an r0 system. Return a list of branches
    [(kind, L_henries, C_farads), ...] with kind "series" (series L-C in
    the series arm) or "shunt" (parallel L-C to ground), starting with a
    series branch at the source. Every branch must resonate at the SAME
    frequency — the checker measures which one you chose. (Hour 3 showed
    what the wrong center does; HOMEWORK.md names the trap.)"""
    raise NotImplementedError


def ladder_sweep(branches, f_hz):
    """Module 3 — S-parameters of the ladder by ABCD cascade. Return
    (s11, s21) arrays over f_hz, reference SPEC['r0_ohm'] both ports.
    Build each branch's impedance/admittance and use the toolkit's
    abcd_* helpers; the skrf referee sweeps the same branches
    independently."""
    raise NotImplementedError


def spec_report(f_hz, s11, s21):
    """Module 3 — measure the spec table from a sweep. Return a dict:
      worst_pass_db  : worst attenuation anywhere in 55-65 MHz (positive dB)
      reject_lo_db   : attenuation at 35 MHz (positive dB)
      reject_hi_db   : attenuation at 85 MHz (positive dB)
      gd_center_ns   : group delay at the filter center (which center?)
      gd_edge_ns     : worst group delay at the two passband edges
    Interpolate off-grid frequencies; the toolkit's group_delay_s helps."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
def _scipy_g_referee(family, n, ripple_db=None):
    """g-values by ELEMENT EXTRACTION from the scipy analog prototypes —
    a path fully independent of the recursion. scipy's poles give the
    Hurwitz polynomial D(s); the reflection numerator F(s) comes from
    |S11|^2 = 1 - |S21|^2 (spectral factor: s^n for butterworth,
    eps*C_n(-js) for chebyshev, via numpy's Chebyshev basis); then
    Z(s) = (D+F)/(D-F) and a Cauer continued-fraction expansion peels off
    g1..gn and the load. Read it after you finish module 1 — it is the
    g-recursion's derivation, executed by machine."""
    from numpy.polynomial import chebyshev as _cheb
    from scipy.signal import buttap, cheb1ap

    if family == "butterworth":
        _, p, k = buttap(n)
        f_poly = np.zeros(n + 1)
        f_poly[0] = 1.0
    elif family == "chebyshev":
        _, p, k = cheb1ap(n, ripple_db)
        eps = np.sqrt(10.0 ** (ripple_db / 10.0) - 1.0)
        cn = _cheb.cheb2poly(np.eye(n + 1)[n])[::-1]       # C_n(x), high first
        f_poly = (cn * (-1j) ** np.arange(n, -1, -1)) * (1j ** n)
        f_poly = f_poly.real * np.sign(f_poly.real[0]) * eps * k
    else:
        raise ValueError(f"unknown family {family!r}")
    d_poly = np.real(np.poly(p))                            # monic Hurwitz

    def trim(poly, tol=1e-9):
        big = np.max(np.abs(poly)) or 1.0
        i = 0
        while i < len(poly) - 1 and abs(poly[i]) < tol * big:
            i += 1
        return poly[i:]

    a = np.polyadd(d_poly, f_poly)                          # Z numerator
    b = trim(np.polysub(d_poly, f_poly))                    # Z denominator
    gs = []
    for _ in range(n):
        q = a[0] / b[0]                                     # coefficient of s
        gs.append(q)
        a, b = b, trim(np.polysub(a, np.concatenate([q * b, [0.0]])))
    gs.append(a[-1] / b[-1])                                # load resistance
    return np.array(gs)


def _skrf_ladder_referee(branches, f_hz):
    """The same ladder, swept by scikit-rf's own lumped-element media —
    an implementation your ABCD cascade never touches. Returns (s11, s21)."""
    import skrf as rf
    from skrf.media import DefinedGammaZ0

    freq = rf.Frequency.from_f(np.asarray(f_hz, dtype=float), unit="hz")
    med = DefinedGammaZ0(frequency=freq, z0=SPEC["r0_ohm"])
    net = None
    for kind, l_h, c_f in branches:
        if kind == "series":
            two = med.inductor(l_h) ** med.capacitor(c_f)
        else:
            two = med.shunt_inductor(l_h) ** med.shunt_capacitor(c_f)
        net = two if net is None else net ** two
    return net.s[:, 0, 0], net.s[:, 1, 0]


def _bp_omega(f_hz, f1_hz, f2_hz):
    """The lowpass<->bandpass frequency map (toolkit's own, for the checker)."""
    f0 = np.sqrt(f1_hz * f2_hz)
    delta = (f2_hz - f1_hz) / f0
    f = np.asarray(f_hz, dtype=float)
    return (f / f0 - f0 / f) / delta


def _student_ladder(m):
    """Chebyshev design from the student's own modules 1+2 (or raise)."""
    n = m["min_order"]("chebyshev", SPEC["ripple_db"], SPEC["reject_db"],
                       abs(_bp_omega(SPEC["stop_hi_hz"],
                                     SPEC["f1_hz"], SPEC["f2_hz"])))
    gs = m["g_values"]("chebyshev", n, SPEC["ripple_db"])
    return n, m["bandpass_ladder"](gs, SPEC["f1_hz"], SPEC["f2_hz"],
                                   SPEC["r0_ohm"])


def run_checks(mods=None):
    m = mods or dict(g_values=g_values, min_order=min_order,
                     bandpass_ladder=bandpass_ladder,
                     ladder_sweep=ladder_sweep, spec_report=spec_report)
    print("=" * 64)
    print("hw8 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: the g-value engine vs scipy element extraction ----------
    print("\n[module 1] g_values -- recursion vs scipy element extraction")
    try:
        worst = {}
        for fam, rp in [("butterworth", None), ("chebyshev", 0.5),
                        ("chebyshev", 3.0)]:
            key = fam if rp is None else f"{fam} {rp} dB"
            worst[key] = max(
                float(np.max(np.abs(np.asarray(m["g_values"](fam, n, rp))
                                    - _scipy_g_referee(fam, n, rp))))
                for n in range(1, 9))
        for key, val in worst.items():
            print(f"  {key:18s} N=1..8: worst |g - scipy referee| = {val:.2e}")
        g3 = np.asarray(m["g_values"]("chebyshev", 3, 0.5))
        print(f"  chebyshev 0.5 dB N=3: g = {np.array2string(g3, precision=4)}"
              "   (the classic 1.5963 / 1.0967 row)")
        g2 = np.asarray(m["g_values"]("chebyshev", 2, 0.5))
        print(f"  chebyshev 0.5 dB N=2: load g3 = {g2[-1]:.4f}"
              "   (not 1 -- even N wants unequal terminations)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: order estimate + the bandpass ladder --------------------
    print("\n[module 2] min_order / bandpass_ladder -- the synthesizer")
    try:
        om_lo = _bp_omega(SPEC["stop_lo_hz"], SPEC["f1_hz"], SPEC["f2_hz"])
        om_hi = _bp_omega(SPEC["stop_hi_hz"], SPEC["f1_hz"], SPEC["f2_hz"])
        print(f"  mapped stop frequencies: Omega(35 MHz) = {om_lo:+.4f}, "
              f"Omega(85 MHz) = {om_hi:+.4f}  (smaller |Omega| binds)")
        n_c = m["min_order"]("chebyshev", SPEC["ripple_db"],
                             SPEC["reject_db"], abs(om_hi))
        n_b = m["min_order"]("butterworth", SPEC["ripple_db"],
                             SPEC["reject_db"], abs(om_hi))
        print(f"  min order: chebyshev 0.5 dB = {n_c}, butterworth = {n_b}"
              f"   (Q1's numbers)")
        n_c2, lad = _student_ladder(m)
        f0 = np.sqrt(SPEC["f1_hz"] * SPEC["f2_hz"])
        print(f"  your chebyshev N={n_c2} ladder (f0 = {f0/1e6:.4f} MHz):")
        worst_res = 0.0
        for kind, l_h, c_f in lad:
            f_res = 1.0 / (2.0 * np.pi * np.sqrt(l_h * c_f))
            worst_res = max(worst_res, abs(f_res - f0) / f0)
            print(f"    {kind:6s} L = {l_h*1e9:10.3f} nH   C = {c_f*1e12:9.4f}"
                  f" pF   resonates {f_res/1e6:.4f} MHz")
        print(f"  worst branch resonance offset from sqrt(f1*f2): "
              f"{worst_res:.2e} relative   (every branch must tune to f0)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the sweep and the spec table ----------------------------
    print("\n[module 3] ladder_sweep / spec_report -- the sweep")
    try:
        f = F_SWEEP_HZ
        s11r, s21r = m["ladder_sweep"](REF_LADDER, f)
        k11, k21 = _skrf_ladder_referee(REF_LADDER, f)
        print("  reference ladder (10.7 MHz FM-IF butterworth, provided): "
              f"max |dS21| vs skrf = {np.max(np.abs(s21r - k21)):.2e}, "
              f"max |dS11| = {np.max(np.abs(s11r - k11)):.2e}")
        try:
            n_c2, lad = _student_ladder(m)
            s11, s21 = m["ladder_sweep"](lad, f)
            _, k21b = _skrf_ladder_referee(lad, f)
            print(f"  your ladder: max |dS21| vs skrf = "
                  f"{np.max(np.abs(s21 - k21b)):.2e}")
            rep = m["spec_report"](f, s11, s21)
            om_hi = abs(_bp_omega(SPEC["stop_hi_hz"],
                                  SPEC["f1_hz"], SPEC["f2_hz"]))
            om_lo = abs(_bp_omega(SPEC["stop_lo_hz"],
                                  SPEC["f1_hz"], SPEC["f2_hz"]))
            ana_hi = float(cheb_atten_db(n_c2, SPEC["ripple_db"], om_hi))
            ana_lo = float(cheb_atten_db(n_c2, SPEC["ripple_db"], om_lo))
            print("  spec table (your ladder, measured from the sweep):")
            marg = round(SPEC["ripple_db"] - rep["worst_pass_db"], 4) + 0.0
            print(f"    worst passband attenuation = {rep['worst_pass_db']:7.4f} dB"
                  f"   (spec <= {SPEC['ripple_db']}, margin {marg:+.4f} dB)")
            print(f"    rejection @ 35 MHz         = {rep['reject_lo_db']:7.2f} dB"
                  f"   (spec >= {SPEC['reject_db']:.0f}, "
                  f"margin {rep['reject_lo_db']-SPEC['reject_db']:+.2f} dB; "
                  f"analytic {ana_lo:.2f}, delta {rep['reject_lo_db']-ana_lo:+.1e})")
            print(f"    rejection @ 85 MHz         = {rep['reject_hi_db']:7.2f} dB"
                  f"   (spec >= {SPEC['reject_db']:.0f}, "
                  f"margin {rep['reject_hi_db']-SPEC['reject_db']:+.2f} dB; "
                  f"analytic {ana_hi:.2f}, delta {rep['reject_hi_db']-ana_hi:+.1e})")
            print(f"    group delay                = {rep['gd_center_ns']:.1f} ns"
                  f" center, {rep['gd_edge_ns']:.1f} ns worst edge"
                  "   (Q4's numbers)")
        except NotImplementedError:
            print("  spec table needs modules 1+2 as well -- skipped")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_sweep_plot(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(g_values=g_values, min_order=min_order,
                     bandpass_ladder=bandpass_ladder,
                     ladder_sweep=ladder_sweep, spec_report=spec_report)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    try:
        f = F_SWEEP_HZ
        _, lad = _student_ladder(m)
        s11, s21 = m["ladder_sweep"](lad, f)
        fm = f / 1e6
        axes[0].plot(fm, 20 * np.log10(np.abs(s21) + 1e-300), label="|S21|")
        axes[0].plot(fm, 20 * np.log10(np.abs(s11) + 1e-300), alpha=0.6,
                     label="|S11|")
        # the spec mask
        axes[0].plot([SPEC["f1_hz"] / 1e6, SPEC["f2_hz"] / 1e6],
                     [-SPEC["ripple_db"]] * 2, "k-", lw=2.5)
        for fs in (SPEC["stop_lo_hz"], SPEC["stop_hi_hz"]):
            axes[0].plot([fs / 1e6 - 2, fs / 1e6 + 2],
                         [-SPEC["reject_db"]] * 2, "r-", lw=2.5)
        axes[0].set_xlabel("frequency (MHz)")
        axes[0].set_ylabel("dB")
        axes[0].set_ylim(-80, 5)
        axes[0].set_title("the spec, faced (bars = mask)")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        gd = group_delay_s(f, s21) * 1e9
        band = (f >= SPEC["f1_hz"] - 5e6) & (f <= SPEC["f2_hz"] + 5e6)
        axes[1].plot(fm[band], gd[band])
        for fe in (SPEC["f1_hz"], SPEC["f2_hz"]):
            axes[1].axvline(fe / 1e6, color="gray", ls="--", alpha=0.5)
        axes[1].set_xlabel("frequency (MHz)")
        axes[1].set_ylabel("group delay (ns)")
        axes[1].set_title("what the steep skirts cost (Q4)")
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("modules 1+2+3 not implemented yet")
    fig.tight_layout()
    fig.savefig("hw8_sweep.png", dpi=130)
    print("wrote hw8_sweep.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--sweep", action="store_true",
                    help="S21/S11 + group delay against the spec mask")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.sweep:
        make_sweep_plot()
    if not (args.check or args.sweep):
        print(__doc__)


if __name__ == "__main__":
    main()
