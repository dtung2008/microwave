"""Homework 9 starter — Copper at last.

You implement the three modules marked TODO below. Everything else is the
toolkit: the specs, the re-provided g-value engine, the ABCD machinery, the
coupled-line section, the dimension helper, the referees, and the checker.

Run from this directory:

    python hw9_starter.py --check    # measured facts per module (the instrument)
    python hw9_starter.py --sweep    # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and the formula card; ANSWERS.md has the
questions (two of them must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` decibels, `*_hz` hertz, `*_ohm` ohms,
`*_m` meters, `theta` radians. g-values are dimensionless prototype numbers.
Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
import os

import numpy as np
from scipy.constants import c as C_M_S            # speed of light, m/s
from scipy.optimize import brentq

# ----------------------------------------------------------------------------
# The specs (instructor side — what your filters are graded against)
# ----------------------------------------------------------------------------
# Warm-up: the stub lowpass. A 3 GHz anti-alias cleanup for the course
# radar's exciter chain — and the first filter you can actually etch.
SPEC_LPF = dict(
    n=3,                 # order (this homework's Kuroda chain is worked for N=3)
    ripple_db=0.5,       # chebyshev passband ripple
    f_c_hz=3e9,          # cutoff: the equal-ripple band edge
    z0_ohm=50.0,         # system impedance
)

# The main event: hw8's insertion-loss philosophy at microwave. A 2.4 GHz
# coupled-line bandpass on the course board (RO4350B, spec'd in hw5).
SPEC_BPF = dict(
    n=3,                 # order -> N+1 = 4 coupled-line sections
    ripple_db=0.5,       # chebyshev passband ripple
    f0_hz=2.4e9,         # center frequency (sections are lambda/4 here)
    fbw=0.10,            # fractional bandwidth Delta = (f2-f1)/f0
    z0_ohm=50.0,         # system impedance
)

# Measurement grids (2 MHz steps; f0, band edges, 2f0 and 3f0 land exactly).
F_BPF_HZ = np.linspace(0.1e9, 10e9, 4951)         # the syllabus's 0.1-10 GHz
F_LPF_HZ = np.linspace(0.05e9, 15e9, 7476)        # sees the LPF's second life

# The course board (mirrors hw5's stackup; dimensions helper works on it).
RO4350B = dict(name="RO4350B", ep_r=3.48, h_m=0.508e-3, tand=0.0037,
               t_m=35e-6)

# Module-3 reference input (so a broken module 2 never hides module 3):
# the SAME electrical design centered at 2.0 GHz — which makes it exactly
# Pozar's Example 8.8 table (0.5 dB ripple, N=3, 10%): a textbook you can
# hold your module 2 against, digit for digit.
REF_F0_HZ = 2.0e9
REF_BPF_Z0EO = np.array([[70.6048, 39.2355],
                         [56.6407, 44.7687],
                         [56.6407, 44.7687],
                         [70.6048, 39.2355]])

# The openEMS case study (instructor-run full-wave; students post-process).
# Drop the instructor's export at CASE_FILE; absent that, a LOUDLY-LABELED
# placeholder is generated from the ideal model with a documented,
# physically-motivated perturbation (see _write_placeholder).
CASE_FILE = "openems_coupled_bpf.s2p"
PLACEHOLDER_FILE = "PLACEHOLDER_coupled_bpf.s2p"
DELTA_MODE = 0.03    # placeholder even/odd eps_eff split: e x(1+d), o x(1-d)
DISP = 1.02          # placeholder dispersion: eps_eff(f0)/eps_eff(0) ~ +2%


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> dB. (You built this in hw1; provided here.)"""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """dB -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


_LN10 = np.log(10.0)


def g_values(family, n, ripple_db=None):
    """Lowpass prototype g-values — the INSTRUCTOR REFERENCE IMPLEMENTATION,
    mirroring the engine you built (by recursion) in hw8. Provided here so
    this homework stands alone; the checker still validates it against the
    scipy element-extraction referee every run. If your own hw8 engine
    disagrees with this one, believe the referee, then find out why."""
    if family == "butterworth":
        k = np.arange(1, n + 1)
        return np.concatenate([2.0 * np.sin((2 * k - 1) * np.pi / (2 * n)),
                               [1.0]])
    if family == "chebyshev":
        beta = np.log(1.0 / np.tanh(ripple_db * _LN10 / 40.0))
        gam = np.sinh(beta / (2.0 * n))
        a = np.sin((2.0 * np.arange(1, n + 1) - 1.0) * np.pi / (2.0 * n))
        b = gam ** 2 + np.sin(np.arange(1, n + 1) * np.pi / n) ** 2
        g = np.zeros(n)
        g[0] = 2.0 * a[0] / gam
        for k in range(1, n):
            g[k] = 4.0 * a[k - 1] * a[k] / (b[k - 1] * g[k - 1])
        load = 1.0 if n % 2 == 1 else 1.0 / np.tanh(beta / 4.0) ** 2
        return np.concatenate([g, [load]])
    raise ValueError(f"unknown family {family!r}")


def richards_omega(f_hz, f_c_hz):
    """The Richards frequency Omega = tan(theta) for commensurate lines cut
    lambda/8 at f_c (theta = 45 deg there): Omega(f_c) = 1 = the prototype
    band edge. Periodic in f — that periodicity is this lecture."""
    return np.tan(0.25 * np.pi * np.asarray(f_hz, dtype=float) / f_c_hz)


def cheb_atten_db(n, ripple_db, omega):
    """Analytic Chebyshev attenuation at prototype frequency omega (band
    edge = 1) — hw8's closed-form referee, re-provided. Feed it
    richards_omega(f) and it referees a stub filter across the whole sweep."""
    e2 = 10.0 ** (ripple_db / 10.0) - 1.0
    om = np.abs(np.asarray(omega, dtype=float))
    cn = np.where(om >= 1.0, np.cosh(n * np.arccosh(np.maximum(om, 1.0))),
                  np.cos(n * np.arccos(np.minimum(om, 1.0))))
    return 10.0 * np.log10(1.0 + e2 * cn ** 2)


# --- ABCD machinery (lecture 4's algebra, vectorized over theta) -------------
def abcd_line(z0_ohm, theta):
    """ABCD of a transmission line: char impedance z0_ohm, electrical length
    theta (radians, array ok)."""
    th = np.asarray(theta, dtype=float)
    m = np.zeros(th.shape + (2, 2), dtype=complex)
    m[..., 0, 0] = np.cos(th)
    m[..., 0, 1] = 1j * z0_ohm * np.sin(th)
    m[..., 1, 0] = 1j * np.sin(th) / z0_ohm
    m[..., 1, 1] = np.cos(th)
    return m


def abcd_shunt_open_stub(z0_ohm, theta):
    """ABCD of a shunt OPEN-circuited stub: Y_in = j*tan(theta)/z0."""
    th = np.asarray(theta, dtype=float)
    m = np.zeros(th.shape + (2, 2), dtype=complex)
    m[..., 0, 0] = 1.0
    m[..., 1, 0] = 1j * np.tan(th) / z0_ohm
    m[..., 1, 1] = 1.0
    return m


def abcd_series_short_stub(z0_ohm, theta):
    """ABCD of a series SHORT-circuited stub: Z_in = j*z0*tan(theta).
    (Richards makes these out of inductors; microstrip cannot build them —
    which is why Kuroda exists, and why your module 1 must remove them.)"""
    th = np.asarray(theta, dtype=float)
    m = np.zeros(th.shape + (2, 2), dtype=complex)
    m[..., 0, 0] = 1.0
    m[..., 0, 1] = 1j * z0_ohm * np.tan(th)
    m[..., 1, 1] = 1.0
    return m


def abcd_cascade(*ms):
    """Cascade ABCD matrices left to right (source side first)."""
    out = ms[0]
    for m in ms[1:]:
        out = out @ m
    return out


def abcd_to_s(m, z0_ohm):
    """ABCD (npts, 2, 2) -> (s11, s21), equal reference z0 both ports."""
    a, b = m[..., 0, 0], m[..., 0, 1]
    c, d = m[..., 1, 0], m[..., 1, 1]
    den = a + b / z0_ohm + c * z0_ohm + d
    return (a + b / z0_ohm - c * z0_ohm - d) / den, 2.0 / den


_STUB_BUILDERS = {"line": abcd_line, "shunt_open": abcd_shunt_open_stub,
                  "series_short": abcd_series_short_stub}


def sweep_stub_filter(elements, f_c_hz, f_hz, z0_ohm):
    """Sweep a commensurate stub filter: `elements` is a list of
    (kind, z_ohm) with kind in {"line", "shunt_open", "series_short"}, every
    element lambda/8 at f_c_hz (theta = 45 deg there). Returns (s11, s21).
    This is the measurement bench for your module 1 — plumbing, not core."""
    theta = 0.25 * np.pi * np.asarray(f_hz, dtype=float) / f_c_hz
    ms = [_STUB_BUILDERS[kind](z, theta) for kind, z in elements]
    return abcd_to_s(abcd_cascade(*ms), z0_ohm)


def richards_series_form(ripple_db, z0_ohm):
    """The Richards network BEFORE Kuroda, N=3 chebyshev: series-L-first
    prototype mapped element-for-element (series short stubs g1, g3 and the
    shunt open stub 1/g2). Unbuildable in microstrip — module 1's job is to
    produce its buildable equal. The checker measures |S21| of both; Q3 asks
    what the measured difference means."""
    g1, g2, g3, _ = g_values("chebyshev", 3, ripple_db)
    return [("series_short", z0_ohm * g1),
            ("shunt_open",   z0_ohm / g2),
            ("series_short", z0_ohm * g3)]


def coupled_section_abcd(z0e_ohm, z0o_ohm, theta_e, theta_o=None):
    """ABCD of one coupled-line section, bandpass connection (through ports
    diagonal, other two ends open) — lecture 7's even/odd investment, cashed:
    Z11 = -j(Z0e*cot(th_e) + Z0o*cot(th_o))/2, Z12 = -j(Z0e/sin(th_e)
    - Z0o/sin(th_o))/2, written in sin/cos form so theta -> 180 deg stays
    numerically tame. theta_o defaults to theta_e (ideal TEM); the case-study
    placeholder passes different mode angles. Plumbing, not core — the core
    is knowing what Z0e/Z0o to feed it."""
    te = np.asarray(theta_e, dtype=float)
    to = te if theta_o is None else np.asarray(theta_o, dtype=float)
    se, ce = np.sin(te), np.cos(te)
    so, co = np.sin(to), np.cos(to)
    den = z0e_ohm * so - z0o_ohm * se
    m = np.zeros(np.broadcast(te, to).shape + (2, 2), dtype=complex)
    m[..., 0, 0] = (z0e_ohm * ce * so + z0o_ohm * co * se) / den
    m[..., 1, 1] = m[..., 0, 0]
    m[..., 1, 0] = 2j * se * so / den
    m[..., 0, 1] = 0.5j * ((z0e_ohm ** 2 + z0o_ohm ** 2) * se * so
                           - 2.0 * z0e_ohm * z0o_ohm * (1.0 + ce * co)) / den
    return m


# --- microstrip dimensions (quasi-static; mirrors hw5's Hammerstad) ----------
def eps_eff_of_u(u, er):
    """Hammerstad quasi-static effective permittivity, shape ratio u = w/h
    (zero-thickness form — the Akhtarzad mapping below assumes thin strips)."""
    return (er + 1.0) / 2.0 + (er - 1.0) / 2.0 / np.sqrt(1.0 + 12.0 / u)


def z0_of_u(u, er):
    """Hammerstad quasi-static Z0(u) — both regimes (hw5's formula card)."""
    ee = eps_eff_of_u(u, er)
    if u <= 1.0:
        return 60.0 / np.sqrt(ee) * np.log(8.0 / u + u / 4.0)
    return 120.0 * np.pi / (np.sqrt(ee) * (u + 1.393
                                           + 0.667 * np.log(u + 1.444)))


def u_for_z0(z0_ohm, er):
    """Inverse-Hammerstad: the shape ratio u = w/h at which z0_of_u reports
    z0_ohm (numeric root — hw5's synthesis move, re-provided)."""
    return brentq(lambda u: z0_of_u(u, er) - z0_ohm, 1e-3, 40.0, xtol=1e-12)


def _akhtarzad_ratios(w_h, s_h, er):
    """Akhtarzad's single-line equivalence, ANALYSIS direction: a coupled
    pair (w/h, s/h) behaves, mode by mode, like two single microstrips whose
    shape ratios these formulas return (even, odd). Akhtarzad-Rowbotham-Johns
    1975, as reproduced in Garg et al.; the odd-mode correction term is the
    er <~ 6 branch (RO4350B qualifies)."""
    g = np.cosh(0.5 * np.pi * s_h)
    d = np.cosh(np.pi * w_h + 0.5 * np.pi * s_h)
    wh_se = (2.0 / np.pi) * np.arccosh((2.0 * d - g + 1.0) / (g + 1.0))
    wh_so = ((2.0 / np.pi) * np.arccosh((2.0 * d - g - 1.0) / (g - 1.0))
             + (4.0 / (np.pi * (1.0 + er / 2.0)))
             * np.arccosh(1.0 + 2.0 * w_h / s_h))
    return wh_se, wh_so


def coupled_dims(z0e_ohm, z0o_ohm, sub):
    """The dimension helper: (Z0e, Z0o) -> (w_m, s_m) on substrate `sub`.

    Method (Akhtarzad, 1975): each mode of the pair is matched to a SINGLE
    microstrip at half the mode impedance (inverse-Hammerstad gives its
    shape ratio), then the coupled geometry is the 2-D numeric root of the
    equivalence formulas above. Quasi-static and thin-strip — expect
    several-percent truth error; a real tapeout closes this loop with a
    field solver, which is exactly this lecture's ideal-vs-EM story."""
    er = sub["ep_r"]
    wh_se_t = u_for_z0(z0e_ohm / 2.0, er)
    wh_so_t = u_for_z0(z0o_ohm / 2.0, er)

    def w_given_s(s_h):
        return brentq(lambda w_h:
                      _akhtarzad_ratios(w_h, s_h, er)[0] - wh_se_t,
                      1e-4, 40.0, xtol=1e-13)

    def odd_resid(s_h):
        return _akhtarzad_ratios(w_given_s(s_h), s_h, er)[1] - wh_so_t

    s_h = brentq(odd_resid, 1e-3, 20.0, xtol=1e-13)
    w_h = w_given_s(s_h)
    return w_h * sub["h_m"], s_h * sub["h_m"]


def quarter_wave_len_m(f0_hz, w_m, sub):
    """Physical lambda_g/4 at f0 for a section of width w_m: the guided
    wavelength uses the SINGLE-LINE quasi-static eps_eff at that width (the
    documented approximation — the two modes actually travel at different
    speeds, and the case study prices what that costs)."""
    ee = eps_eff_of_u(w_m / sub["h_m"], sub["ep_r"])
    return C_M_S / (4.0 * f0_hz * np.sqrt(ee))


# --- the openEMS case study --------------------------------------------------
def _write_placeholder(z0eo, f0_hz):
    """Generate the LOUDLY-LABELED placeholder 'reality': the ideal model
    with two documented, physically-motivated perturbations —
      (1) mode split: even mode eps_eff x(1+DELTA_MODE), odd x(1-DELTA_MODE)
          (in microstrip the odd mode lives more in air, so it runs faster;
          representative split for er ~ 3.5 coupled pairs), and
      (2) dispersion: both modes x DISP (quasi-static -> f0 rise ~ 2%),
          while the lengths stay cut at the quasi-static value — hour 2's
          war story, re-enacted in miniature.
    NOT field-solved. Drop the instructor's real openEMS export at CASE_FILE
    and this function never runs."""
    import skrf as rf

    theta = 0.5 * np.pi * F_BPF_HZ / f0_hz
    re_, ro_ = np.sqrt(DISP * (1 + DELTA_MODE)), np.sqrt(DISP * (1 - DELTA_MODE))
    ms = [coupled_section_abcd(ze, zo, theta * re_, theta * ro_)
          for ze, zo in np.asarray(z0eo, dtype=float)]
    s11, s21 = abcd_to_s(abcd_cascade(*ms), SPEC_BPF["z0_ohm"])
    s = np.zeros((len(F_BPF_HZ), 2, 2), dtype=complex)
    s[:, 0, 0] = s[:, 1, 1] = s11
    s[:, 0, 1] = s[:, 1, 0] = s21
    freq = rf.Frequency.from_f(F_BPF_HZ, unit="hz")
    ntw = rf.Network(frequency=freq, s=s, z0=SPEC_BPF["z0_ohm"],
                     name="PLACEHOLDER_coupled_bpf")
    ntw.write_touchstone(PLACEHOLDER_FILE.replace(".s2p", ""), dir=".")


def load_case_study(z0eo=None):
    """Load the case-study two-port: the instructor's openEMS export if
    CASE_FILE exists, else the placeholder (generated from z0eo, default =
    the reference design). Returns (network, source_string, is_placeholder).
    The post-processing downstream is identical either way — that is the
    point (lecture 5 set this precedent)."""
    import skrf as rf

    if os.path.exists(CASE_FILE):
        return rf.Network(CASE_FILE), f"instructor openEMS export ({CASE_FILE})", False
    z0eo = REF_BPF_Z0EO * 1.0 if z0eo is None else z0eo
    _write_placeholder(z0eo, SPEC_BPF["f0_hz"])
    src = (f"PLACEHOLDER ({PLACEHOLDER_FILE}: ideal model + documented "
           f"eps_eff perturbation, mode split {DELTA_MODE:+.0%}/"
           f"{-DELTA_MODE:+.0%}, dispersion x{DISP} — NOT field-solved; "
           f"drop the real openEMS export at {CASE_FILE} and rerun)")
    return rf.Network(PLACEHOLDER_FILE), src, True


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def stub_lowpass(ripple_db, z0_ohm):
    """Module 1 (warm-up) — the Richards/Kuroda stub lowpass, N=3 chebyshev.

    Return the BUILDABLE element list for sweep_stub_filter: five
    (kind, z_ohm) tuples using only "shunt_open" and "line" — no
    "series_short" anywhere (microstrip cannot make one). The chain hour 1
    worked on the board: prototype g-values (series-L first) -> Richards
    (L -> series short stub, C -> shunt open stub) -> add a unit element at
    each end -> Kuroda, once per end, to trade every series stub across a
    unit element for a shunt stub. All elements are commensurate (lambda/8
    at f_c — the sweep bench enforces that convention; your job is only the
    impedances, which do not depend on f_c). Exactness is the contract: at
    f_c the checker expects the ripple value to the microvolt."""
    raise NotImplementedError


def coupled_bpf_z0eo(n, ripple_db, fbw, z0_ohm):
    """Module 2 (the core) — coupled-line bandpass synthesis.

    From the chebyshev prototype (toolkit g_values), return an (n+1, 2)
    array of [Z0e, Z0o] per coupled section, source to load. Hour 2's
    three-line procedure: g-values -> the N+1 admittance-inverter constants
    J (end sections carry square roots, interior sections do not) -> each
    section's even/odd impedances from J*Z0. The design is frequency-free
    until the sections are CUT to lambda/4 at f0 — that is why f0 is not an
    argument. Sanity anchors: your (Z0e - Z0o)/2 is each inverter's K, and
    REF_BPF_Z0EO is this exact spec's textbook table."""
    raise NotImplementedError


def bpf_sweep(z0eo, f0_hz, f_hz, z0_ohm):
    """Module 3 — the ideal sweep. Cascade the coupled sections (toolkit:
    coupled_section_abcd -> abcd_cascade -> abcd_to_s) with every section
    lambda/4 at f0_hz, and return (s11, s21) over f_hz. One decision is
    yours and it is the whole module: theta(f)."""
    raise NotImplementedError


def bpf_spec_report(f_hz, s21, f0_hz, fbw):
    """Module 3 — measure the spec table from a sweep. Return a dict:
      il_f0_db       : insertion loss at f0 (positive dB)
      worst_pass_db  : worst attenuation anywhere in the DESIGN band
                       f0*(1 -+ fbw/2) (positive dB)
      bw_ripple_pct  : measured equal-ripple bandwidth — the contiguous band
                       around f0 where attenuation <= ripple (0.5 dB) — as a
                       percent of f0 (the number Q4 reconciles against fbw)
      atten_2f0_db   : attenuation at exactly 2*f0 (positive dB; large)
    Interpolation or nearest-grid is your choice; the grid was built so the
    special frequencies land on it."""
    raise NotImplementedError


def find_reentrant(f_hz, s21, f0_hz):
    """Module 3 — locate the first reentrant passband: return its center
    frequency in Hz. Contract: the first passband lying entirely ABOVE
    1.5*f0. Method is yours (peak of |S21| there, or the midpoint of the
    -3 dB crossings — defend the choice in ANSWERS.md). Q1 predicted this
    number before you ran anything; the checker prints the error."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
def _scipy_g_referee(family, n, ripple_db=None):
    """g-values by element extraction from scipy's analog prototypes — the
    same independent referee hw8 used, re-provided so the toolkit's g_values
    is validated on every run (never trusted silently)."""
    from numpy.polynomial import chebyshev as _cheb
    from scipy.signal import buttap, cheb1ap

    if family == "butterworth":
        _, p, k = buttap(n)
        f_poly = np.zeros(n + 1)
        f_poly[0] = 1.0
    elif family == "chebyshev":
        _, p, k = cheb1ap(n, ripple_db)
        eps = np.sqrt(10.0 ** (ripple_db / 10.0) - 1.0)
        cn = _cheb.cheb2poly(np.eye(n + 1)[n])[::-1]
        f_poly = (cn * (-1j) ** np.arange(n, -1, -1)) * (1j ** n)
        f_poly = f_poly.real * np.sign(f_poly.real[0]) * eps * k
    else:
        raise ValueError(f"unknown family {family!r}")
    d_poly = np.real(np.poly(p))

    def trim(poly, tol=1e-9):
        big = np.max(np.abs(poly)) or 1.0
        i = 0
        while i < len(poly) - 1 and abs(poly[i]) < tol * big:
            i += 1
        return poly[i:]

    a = np.polyadd(d_poly, f_poly)
    b = trim(np.polysub(d_poly, f_poly))
    gs = []
    for _ in range(n):
        q = a[0] / b[0]
        gs.append(q)
        a, b = b, trim(np.polysub(a, np.concatenate([q * b, [0.0]])))
    gs.append(a[-1] / b[-1])
    return np.array(gs)


def _skrf_stub_referee(elements, f_c_hz, f_hz, z0_ohm):
    """The stub filter swept by scikit-rf's own media — an implementation
    your ABCD cascade never touches. Field notes honored: DefinedGammaZ0
    gets gamma = j*omega/c EXPLICITLY (its default is dispersionless in the
    wrong way for lines cut in meters), and lines are cut in meters."""
    import skrf as rf
    from skrf.media import DefinedGammaZ0

    f = np.asarray(f_hz, dtype=float)
    freq = rf.Frequency.from_f(f, unit="hz")
    gamma = 1j * 2.0 * np.pi * f / C_M_S
    l8_m = C_M_S / (8.0 * f_c_hz)
    net = None
    for kind, z in elements:
        med = DefinedGammaZ0(frequency=freq, z0=z, gamma=gamma)
        if kind == "line":
            two = med.line(l8_m, unit="m")
        elif kind == "shunt_open":
            two = med.shunt(med.delay_open(l8_m, unit="m"))
        else:
            raise ValueError(f"skrf referee cannot build {kind!r} "
                             "(neither can microstrip — that is the point)")
        net = two if net is None else net ** two
    net.renormalize(z0_ohm)
    return net.s[:, 0, 0], net.s[:, 1, 0]


def _skrf_coupled_referee(z0eo, f0_hz, f_hz, z0_ohm):
    """The coupled-line filter swept via scikit-rf: each section's 2-port Z
    is the even/odd combination of two PLAIN skrf line networks (one cut at
    Z0e, one at Z0o), then z2s and cascade — a code path independent of the
    toolkit's cot/csc algebra."""
    import skrf as rf
    from skrf.media import DefinedGammaZ0
    from skrf.network import z2s

    f = np.asarray(f_hz, dtype=float)
    freq = rf.Frequency.from_f(f, unit="hz")
    gamma = 1j * 2.0 * np.pi * f / C_M_S
    lq_m = C_M_S / (4.0 * f0_hz)
    net = None
    for z0e, z0o in np.asarray(z0eo, dtype=float):
        ze = DefinedGammaZ0(frequency=freq, z0=z0e,
                            gamma=gamma).line(lq_m, unit="m").z
        zo = DefinedGammaZ0(frequency=freq, z0=z0o,
                            gamma=gamma).line(lq_m, unit="m").z
        z = np.zeros_like(ze)
        z[:, 0, 0] = 0.5 * (ze[:, 0, 0] + zo[:, 0, 0])
        z[:, 1, 1] = 0.5 * (ze[:, 1, 1] + zo[:, 1, 1])
        z[:, 0, 1] = 0.5 * (ze[:, 0, 1] - zo[:, 0, 1])
        z[:, 1, 0] = 0.5 * (ze[:, 1, 0] - zo[:, 1, 0])
        two = rf.Network(frequency=freq, s=z2s(z, z0=z0_ohm), z0=z0_ohm)
        net = two if net is None else net ** two
    return net.s[:, 0, 0], net.s[:, 1, 0]


def _s_db(s):
    return 20.0 * np.log10(np.abs(s) + 1e-300)


def _band_3db_center_hz(f_hz, s21, lo_hz, hi_hz):
    """Midpoint of the -3 dB span inside [lo, hi] (case-study center metric)."""
    w = (f_hz >= lo_hz) & (f_hz <= hi_hz)
    fw, sw = f_hz[w], _s_db(s21)[w]
    ok = fw[sw >= sw.max() - 3.0]
    return 0.5 * (ok.min() + ok.max())


def _mods_default():
    return dict(stub_lowpass=stub_lowpass, coupled_bpf_z0eo=coupled_bpf_z0eo,
                bpf_sweep=bpf_sweep, bpf_spec_report=bpf_spec_report,
                find_reentrant=find_reentrant)


def run_checks(mods=None):
    m = mods or _mods_default()
    print("=" * 64)
    print("hw9 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- toolkit self-check: the re-provided g engine ----------------------
    print("\n[toolkit] g_values (hw8's engine, re-provided) vs scipy referee")
    worst = max(float(np.max(np.abs(g_values(fam, n, rp)
                                    - _scipy_g_referee(fam, n, rp))))
                for fam, rp in [("butterworth", None), ("chebyshev", 0.5),
                                ("chebyshev", 3.0)]
                for n in range(1, 9))
    g3 = g_values("chebyshev", 3, 0.5)
    print(f"  worst |g - scipy extraction| over N=1..8, both families: "
          f"{worst:.2e}")
    print(f"  chebyshev 0.5 dB N=3: g = {np.array2string(g3, precision=4)}"
          "   (hw8's classic row)")

    # --- module 1: the stub lowpass ----------------------------------------
    print("\n[module 1] stub_lowpass -- Richards + Kuroda, N=3 at 3 GHz")
    try:
        els = m["stub_lowpass"](SPEC_LPF["ripple_db"], SPEC_LPF["z0_ohm"])
        kinds = [k for k, _ in els]
        l8_mm = C_M_S / (8.0 * SPEC_LPF["f_c_hz"]) * 1e3
        print(f"  elements (all lambda/8 = {l8_mm:.4f} mm ideal at "
              f"{SPEC_LPF['f_c_hz']/1e9:.0f} GHz):")
        for kind, z in els:
            print(f"    {kind:12s} Z = {z:9.4f} ohm")
        if "series_short" in kinds:
            print("  NOTE: series_short present -- not buildable in "
                  "microstrip; Kuroda not finished")
        f = F_LPF_HZ
        s11, s21 = sweep_stub_filter(els, SPEC_LPF["f_c_hz"], f,
                                     SPEC_LPF["z0_ohm"])
        s21_db = _s_db(s21)
        i_c = np.argmin(np.abs(f - SPEC_LPF["f_c_hz"]))
        print(f"  |S21| at f_c = {s21_db[i_c]:+.6f} dB   (theory: exactly "
              f"-{SPEC_LPF['ripple_db']:.4f} -- the equal-ripple edge)")
        theory_db = -cheb_atten_db(SPEC_LPF["n"], SPEC_LPF["ripple_db"],
                                   richards_omega(f, SPEC_LPF["f_c_hz"]))
        mask = theory_db > -80.0            # skip the pole's numeric noise
        print(f"  vs mapped-chebyshev closed form (atten < 80 dB): "
              f"max |delta| = {np.max(np.abs(s21_db - theory_db)[mask]):.2e} dB")
        _, s21_ref = _skrf_stub_referee(els, SPEC_LPF["f_c_hz"], f,
                                        SPEC_LPF["z0_ohm"])
        print(f"  vs skrf referee: max |dS21| = "
              f"{np.max(np.abs(s21 - s21_ref)):.2e}")
        _, s21_ser = sweep_stub_filter(
            richards_series_form(SPEC_LPF["ripple_db"], SPEC_LPF["z0_ohm"]),
            SPEC_LPF["f_c_hz"], f, SPEC_LPF["z0_ohm"])
        print(f"  Kuroda equivalence, yours vs the unbuildable series form: "
              f"max ||S21|-|S21||= {np.max(np.abs(np.abs(s21) - np.abs(s21_ser))):.2e}"
              "   (Q3's number)")
        i_2fc = np.argmin(np.abs(f - 2.0 * SPEC_LPF["f_c_hz"]))
        print(f"  at 2 f_c = {f[i_2fc]/1e9:.0f} GHz: |S21| = "
              f"{s21_db[i_2fc]:.0f} dB (every stub lambda/4 -- the "
              "attenuation pole)")
        hi = f > 2.0 * SPEC_LPF["f_c_hz"]
        under = f[hi][(-s21_db[hi]) <= SPEC_LPF["ripple_db"] + 1e-9]
        print(f"  the filter's second life: atten <= ripple again over "
              f"{under.min()/1e9:.4f} - {under.max()/1e9:.4f} GHz "
              "(the Richards circle come back around)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: coupled-line synthesis ----------------------------------
    print("\n[module 2] coupled_bpf_z0eo -- the synthesis chain")
    try:
        z0eo = np.asarray(m["coupled_bpf_z0eo"](SPEC_BPF["n"],
                                                SPEC_BPF["ripple_db"],
                                                SPEC_BPF["fbw"],
                                                SPEC_BPF["z0_ohm"]))
        print("  section   Z0e (ohm)   Z0o (ohm)   K=(Z0e-Z0o)/2   "
              "w (mm)   s (mm)   len (mm)")
        for i, (ze, zo) in enumerate(z0eo, 1):
            w_m, s_m = coupled_dims(ze, zo, RO4350B)
            ln_m = quarter_wave_len_m(SPEC_BPF["f0_hz"], w_m, RO4350B)
            print(f"    {i}      {ze:9.4f}   {zo:9.4f}     {0.5*(ze-zo):8.4f}"
                  f"      {w_m*1e3:6.4f}   {s_m*1e3:6.4f}   {ln_m*1e3:7.3f}")
        d_ref = np.max(np.abs(z0eo - REF_BPF_Z0EO))
        print(f"  vs the textbook table for this spec (Pozar Ex 8.8): "
              f"max |delta| = {d_ref:.2e} ohm")
        wh_se, wh_so = _akhtarzad_ratios(
            *(np.array(coupled_dims(*z0eo[0], RO4350B)) / RO4350B["h_m"]),
            RO4350B["ep_r"])
        t_se = u_for_z0(z0eo[0][0] / 2.0, RO4350B["ep_r"])
        t_so = u_for_z0(z0eo[0][1] / 2.0, RO4350B["ep_r"])
        print(f"  dimension helper round trip (section 1): "
              f"|d(w/h)_se| = {abs(wh_se - t_se):.1e}, "
              f"|d(w/h)_so| = {abs(wh_so - t_so):.1e}"
              "   (internally consistent; truth error is the EM gap)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the sweep, the spec table, the reentrance ---------------
    print("\n[module 3] bpf_sweep / bpf_spec_report / find_reentrant")
    try:
        f = F_BPF_HZ
        s11r, s21r = m["bpf_sweep"](REF_BPF_Z0EO, REF_F0_HZ, f,
                                    SPEC_BPF["z0_ohm"])
        k11, k21 = _skrf_coupled_referee(REF_BPF_Z0EO, REF_F0_HZ, f,
                                         SPEC_BPF["z0_ohm"])
        print("  reference filter (textbook table at 2.0 GHz, provided): "
              f"max |dS21| vs skrf = {np.max(np.abs(s21r - k21)):.2e}, "
              f"max |dS11| = {np.max(np.abs(s11r - k11)):.2e}")
        fre = float(m["find_reentrant"](f, s21r, REF_F0_HZ))
        print(f"  its reentrant passband: {fre/1e9:.4f} GHz "
              f"(3 f0 = {3*REF_F0_HZ/1e9:.1f}; "
              f"error {abs(fre - 3*REF_F0_HZ)/(3*REF_F0_HZ)*100:.3f}%)")
        try:
            z0eo = np.asarray(m["coupled_bpf_z0eo"](SPEC_BPF["n"],
                                                    SPEC_BPF["ripple_db"],
                                                    SPEC_BPF["fbw"],
                                                    SPEC_BPF["z0_ohm"]))
            s11, s21 = m["bpf_sweep"](z0eo, SPEC_BPF["f0_hz"], f,
                                      SPEC_BPF["z0_ohm"])
            _, k21b = _skrf_coupled_referee(z0eo, SPEC_BPF["f0_hz"], f,
                                            SPEC_BPF["z0_ohm"])
            print(f"  your 2.4 GHz design: max |dS21| vs skrf = "
                  f"{np.max(np.abs(s21 - k21b)):.2e}")
            rep = m["bpf_spec_report"](f, s21, SPEC_BPF["f0_hz"],
                                       SPEC_BPF["fbw"])
            print("  spec table (measured from the ideal sweep):")
            print(f"    IL at f0                  = {rep['il_f0_db']:8.4f} dB")
            print(f"    worst atten, design band  = {rep['worst_pass_db']:8.4f} dB"
                  f"   (ripple budget {SPEC_BPF['ripple_db']}; the overshoot"
                  " at the edges is Q4)")
            print(f"    0.5-dB ripple bandwidth   = {rep['bw_ripple_pct']:8.4f} %"
                  f"   (designed {SPEC_BPF['fbw']*100:.0f}%)")
            print(f"    atten at 2 f0 (4.8 GHz)   = {rep['atten_2f0_db']:8.1f} dB"
                  "   (the ideal transmission zero -- Q2)")
            fre2 = float(m["find_reentrant"](f, s21, SPEC_BPF["f0_hz"]))
            err = abs(fre2 - 3*SPEC_BPF["f0_hz"]) / (3*SPEC_BPF["f0_hz"])
            i_re = np.argmin(np.abs(f - fre2))
            print(f"    first reentrant passband  = {fre2/1e9:8.4f} GHz"
                  f"   (|S21| there {_s_db(s21)[i_re]:.2f} dB; "
                  f"3 f0 error {err*100:.3f}%)")
            # --- the case study ------------------------------------------
            case, src, is_ph = load_case_study(z0eo)
            print(f"\n  case study source: {src}")
            fc_ = case.frequency.f
            sc21 = case.s[:, 1, 0]
            c_ideal = _band_3db_center_hz(f, s21, 2.0e9, 3.0e9)
            c_case = _band_3db_center_hz(fc_, sc21, 2.0e9, 3.0e9)
            i0c = np.argmin(np.abs(fc_ - SPEC_BPF["f0_hz"]))
            i0i = np.argmin(np.abs(f - SPEC_BPF["f0_hz"]))
            w_i = (f >= 4.2e9) & (f <= 5.4e9)
            w_c = (fc_ >= 4.2e9) & (fc_ <= 5.4e9)
            tag = " [PLACEHOLDER numbers]" if is_ph else ""
            print(f"  ideal-vs-case deltas{tag}:")
            print(f"    passband center (-3 dB midpoint): ideal "
                  f"{c_ideal/1e9:.4f} GHz, case {c_case/1e9:.4f} GHz "
                  f"(shift {(c_case-c_ideal)/1e6:+.1f} MHz = "
                  f"{(c_case-c_ideal)/c_ideal*100:+.2f}%)")
            print(f"    |S21| at 2.4 GHz: ideal {_s_db(s21)[i0i]:+.3f} dB, "
                  f"case {_s_db(sc21)[i0c]:+.3f} dB")
            print(f"    worst |S21| in 4.2-5.4 GHz: ideal "
                  f"{_s_db(s21)[w_i].max():+.1f} dB, case "
                  f"{_s_db(sc21)[w_c].max():+.1f} dB   (the 2 f0 spur -- Q2)")
        except NotImplementedError:
            print("  spec table needs module 2 as well -- skipped")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_sweep_plot(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or _mods_default()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    # --- picture 1: the BPF's whole life, 0.1-10 GHz (Q1/Q2's picture) ------
    try:
        f = F_BPF_HZ
        z0eo = np.asarray(m["coupled_bpf_z0eo"](SPEC_BPF["n"],
                                                SPEC_BPF["ripple_db"],
                                                SPEC_BPF["fbw"],
                                                SPEC_BPF["z0_ohm"]))
        _, s21 = m["bpf_sweep"](z0eo, SPEC_BPF["f0_hz"], f,
                                SPEC_BPF["z0_ohm"])
        ax = axes[0]
        ax.plot(f / 1e9, np.maximum(_s_db(s21), -90), label="ideal sweep")
        try:
            case, src, is_ph = load_case_study(z0eo)
            lab = "case study" + (" (PLACEHOLDER)" if is_ph else " (openEMS)")
            ax.plot(case.frequency.f / 1e9,
                    np.maximum(_s_db(case.s[:, 1, 0]), -90),
                    alpha=0.65, label=lab)
        except Exception:                                     # noqa: BLE001
            pass
        f0 = SPEC_BPF["f0_hz"]
        ax.axvspan((1 - SPEC_BPF["fbw"]/2) * f0 / 1e9,
                   (1 + SPEC_BPF["fbw"]/2) * f0 / 1e9, alpha=0.15,
                   color="C2", label="design band")
        try:
            fre = float(m["find_reentrant"](f, s21, f0)) / 1e9
            ax.axvline(fre, color="C3", ls="--", alpha=0.7)
            ax.annotate(f"reentrant\n{fre:.2f} GHz", (fre + 0.1, -25),
                        fontsize=9, color="C3")
        except NotImplementedError:
            pass
        ax.axvline(2 * f0 / 1e9, color="gray", ls=":", alpha=0.6)
        ax.annotate("2f0 zero", (2 * f0 / 1e9 + 0.05, -85), fontsize=8,
                    color="gray")
        ax.set_xlabel("frequency (GHz)")
        ax.set_ylabel("|S21| (dB)")
        ax.set_ylim(-90, 3)
        ax.set_title("the coupled-line BPF's whole life (0.1-10 GHz)")
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("modules 2+3 not implemented")

    # --- picture 2: the stub LPF vs the mapped prototype (Q3's picture) -----
    try:
        f = F_LPF_HZ
        els = m["stub_lowpass"](SPEC_LPF["ripple_db"], SPEC_LPF["z0_ohm"])
        _, s21 = sweep_stub_filter(els, SPEC_LPF["f_c_hz"], f,
                                   SPEC_LPF["z0_ohm"])
        ax = axes[1]
        ax.plot(f / 1e9, np.maximum(_s_db(s21), -80),
                label="stub filter (measured)")
        th = -cheb_atten_db(SPEC_LPF["n"], SPEC_LPF["ripple_db"],
                            richards_omega(f, SPEC_LPF["f_c_hz"]))
        ax.plot(f[::100] / 1e9, np.maximum(th[::100], -80), "k.", ms=4,
                label="chebyshev thru Richards map")
        ax.axvline(SPEC_LPF["f_c_hz"] / 1e9, color="gray", ls=":", alpha=0.6)
        ax.axvline(2 * SPEC_LPF["f_c_hz"] / 1e9, color="gray", ls=":",
                   alpha=0.6)
        ax.set_xlabel("frequency (GHz)")
        ax.set_ylabel("|S21| (dB)")
        ax.set_ylim(-80, 3)
        ax.set_title("the stub lowpass and its second life")
        ax.legend(loc="lower left", fontsize=9)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 1 not implemented")

    fig.tight_layout()
    fig.savefig("hw9_sweep.png", dpi=130)
    print("wrote hw9_sweep.png")
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
        make_sweep_plot()
    if not (args.check or args.sweep):
        print(__doc__)


if __name__ == "__main__":
    main()
