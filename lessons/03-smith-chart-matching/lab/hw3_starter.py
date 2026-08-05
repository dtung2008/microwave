"""Homework 3 starter — Match the antenna, twice.

You implement the three modules marked TODO below. Everything else is the
toolkit: the antenna, the skrf cascade referee, the Smith-chart plotting,
and the checker.

Run from this directory:

    python hw3_starter.py --check    # measured facts per module (the instrument)
    python hw3_starter.py --smith    # the chart + sweep pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): `*_hz` is hertz,
`*_ohm` ohms, `*_s` siemens, `*_lam` lengths in wavelengths at f0 (so a
design is frequency-independent until the referee sweeps it). Lowercase
z, y are normalized (z = Z/Z0, y = Y0/Y... careful: y = Y/Y0 = Z0/Z).
Lines are ideal and lossless, Z0 = 50 ohm (skrf DefinedGammaZ0).
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
import skrf as rf
from skrf.media import DefinedGammaZ0
from scipy.constants import c as C_M_S          # speed of light, m/s

# ----------------------------------------------------------------------------
# The patient (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
F0_HZ = 2.4e9                      # design frequency (lecture 2's antenna)
Z0_OHM = 50.0                      # system / line characteristic impedance
Z_ANT = 36.0 - 21.0j               # the antenna that lied, back for its match
LAM0_M = C_M_S / F0_HZ             # free-space wavelength at f0 (124.914 mm)
F_BAND_HZ = np.linspace(2.0e9, 2.8e9, 801)   # the comparison window

# A second load in the OTHER chart region (R_L > Z0), so the checker can see
# that your L-section designer chooses its topology by load region, not luck.
Z_REGION_CHECK = 120.0 + 90.0j


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> dB (lecture 1's, re-provided)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """dB -> linear power ratio (lecture 1's, re-provided)."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def gamma_of_z(z_ohm, z0_ohm=Z0_OHM):
    """Reflection coefficient of an impedance: (Z - Z0)/(Z + Z0)."""
    z = np.asarray(z_ohm, dtype=complex)
    return (z - z0_ohm) / (z + z0_ohm)


def z_of_gamma(gamma, z0_ohm=Z0_OHM):
    """The inverse map: Z = Z0 (1 + Gamma)/(1 - Gamma)."""
    g = np.asarray(gamma, dtype=complex)
    return z0_ohm * (1 + g) / (1 - g)


def swr_of_gamma(gamma):
    """Standing wave ratio (1 + |G|)/(1 - |G|)."""
    m = np.abs(gamma)
    return (1 + m) / (1 - m)


def return_loss_db(gamma):
    """Return loss = -20 log10 |Gamma|, in dB (positive for passive loads)."""
    return -20.0 * np.log10(np.abs(gamma))


def zin_line(z_load_ohm, z0_ohm, d_lam):
    """Input impedance of a lossless line, length d in wavelengths, terminated
    in z_load (lecture 2's tangent transformation, re-provided):
    Z_in = Z0 (Z_L + j Z0 tan(beta d)) / (Z0 + j Z_L tan(beta d))."""
    t = np.tan(2.0 * np.pi * np.asarray(d_lam, dtype=float))
    zl = complex(z_load_ohm)
    return z0_ohm * (zl + 1j * z0_ohm * t) / (z0_ohm + 1j * zl * t)


def element_of_x(x_ohm, f0_hz=F0_HZ):
    """A series reactance at f0 as a component: ('L', henries) if x > 0,
    ('C', farads) if x < 0."""
    w0 = 2.0 * np.pi * f0_hz
    return ("L", x_ohm / w0) if x_ohm > 0 else ("C", -1.0 / (w0 * x_ohm))


def element_of_b(b_s, f0_hz=F0_HZ):
    """A shunt susceptance at f0 as a component: ('C', farads) if b > 0,
    ('L', henries) if b < 0."""
    w0 = 2.0 * np.pi * f0_hz
    return ("C", b_s / w0) if b_s > 0 else ("L", -1.0 / (w0 * b_s))


def _media(f_hz):
    """Ideal lossless 50-ohm line medium (skrf DefinedGammaZ0, beta = w/c)."""
    frq = rf.Frequency.from_f(np.atleast_1d(np.asarray(f_hz, dtype=float)),
                              unit="hz")
    return DefinedGammaZ0(frequency=frq, z0=Z0_OHM,
                          gamma=1j * frq.w / C_M_S), frq


def _load_1port(med, frq, z_load_ohm):
    g = complex(gamma_of_z(z_load_ohm))
    return med.load(np.tile(g, (frq.npoints, 1, 1)))


def _lumped(med, where, kind, value):
    """One lumped element as a 2-port: where = 'series' | 'shunt'."""
    if where == "series":
        return med.inductor(value) if kind == "L" else med.capacitor(value)
    return (med.shunt_inductor(value) if kind == "L"
            else med.shunt_capacitor(value))


def gamma_in_lsection(design, f_hz, z_load_ohm=Z_ANT):
    """THE REFEREE (L-section): cascade the design in scikit-rf and return the
    complex Gamma seen from the generator, at each frequency in f_hz.

    `design` is a dict with keys:
      topology : 'series-first' (series element at the load; R_L < Z0 region)
                 or 'shunt-first' (shunt element at the load; R_L > Z0 region)
      series   : ('L', henries) or ('C', farads)
      shunt    : ('L', henries) or ('C', farads)
    """
    med, frq = _media(f_hz)
    ser = _lumped(med, "series", *design["series"])
    shn = _lumped(med, "shunt", *design["shunt"])
    load = _load_1port(med, frq, z_load_ohm)
    if design["topology"] == "series-first":      # gen - shunt - series - load
        ntwk = shn ** ser ** load
    else:                                         # gen - series - shunt - load
        ntwk = ser ** shn ** load
    return ntwk.s[:, 0, 0]


def gamma_in_stub(design, f_hz, z_load_ohm=Z_ANT):
    """THE REFEREE (single shunt stub): cascade [shunt stub] - [line d] - load
    in scikit-rf and return the complex Gamma at each frequency in f_hz.

    `design` is a dict with keys:
      d_lam : line length from the load to the stub, in wavelengths at f0
      l_lam : stub length, in wavelengths at f0
      kind  : 'open' or 'short' (the stub's far-end termination)
    """
    med, frq = _media(f_hz)
    line = med.line(design["d_lam"] * LAM0_M, unit="m")
    if design["kind"] == "open":
        stub = med.shunt_delay_open(design["l_lam"] * LAM0_M, unit="m")
    else:
        stub = med.shunt_delay_short(design["l_lam"] * LAM0_M, unit="m")
    load = _load_1port(med, frq, z_load_ohm)
    return (stub ** line ** load).s[:, 0, 0]


# Instructor reference designs (hard-coded MEASUREMENTS, not formulas — they
# exist so module 3 and --smith work before modules 1-2 do; they answer
# nothing about how to design for a general load, which is your job).
REF_LSECTION = [
    dict(topology="series-first", series=("L", 2.881364e-9),
         shunt=("C", 0.827088e-12)),                 # X=+43.450, B=+12.472 mS
    dict(topology="series-first", series=("C", 45.735935e-12),
         shunt=("L", 5.316993e-9)),                  # X=-1.450,  B=-12.472 mS
]
REF_STUB = [
    dict(d_lam=0.495274, l_lam=0.414589, kind="open"),
    dict(d_lam=0.199260, l_lam=0.085411, kind="open"),
]


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def lsection_match(z_load_ohm, z0_ohm, f0_hz):
    """Module 1 — the L-section designer.

    Return a LIST of design dicts (see gamma_in_lsection for the keys), one
    per valid solution. Choose the topology by load region: 'series-first'
    when R_L < Z0 (the load sits outside the 1+jx circle), 'shunt-first'
    when R_L > Z0 (inside it); each valid topology has two +- solutions.
    Convert X and B to components with element_of_x / element_of_b.
    Hour 2 derived both closed forms from the chart geometry.
    """
    raise NotImplementedError


def stub_match(z_load_ohm, z0_ohm, kind="open"):
    """Module 2 (the core) — the single shunt-stub designer, analytic.

    Return a LIST of two design dicts (see gamma_in_stub for the keys):
    the two solutions for the line length d that lands the ADMITTANCE on
    the g = 1 circle, each with the stub length l that cancels the
    remaining susceptance. All lengths in wavelengths, in [0, 0.5).
    The design is a pure geometry problem — no frequency appears in it;
    that is why d_lam and l_lam are the deliverables.
    """
    raise NotImplementedError


def rl_bandwidth_hz(f_hz, gamma, f0_hz, rl_db=10.0):
    """Module 3 — measure the rl_db return-loss band around f0 from a sweep.

    Given f_hz (ascending) and complex (or magnitude) gamma of a matched
    system, walk outward from f0 to the first frequencies where |Gamma|
    crosses 10**(-rl_db/20), interpolating between samples. Return
    (f_lo_hz, f_hi_hz); use None for an edge that never crosses inside the
    sweep (edge-limited — it happens in this homework, and Q5 asks why).
    """
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
def _fmt_element(el):
    kind, val = el
    return (f"{val*1e9:8.4f} nH" if kind == "L" else f"{val*1e12:8.4f} pF")


def _x_of_element(el, f0_hz=F0_HZ):
    kind, val = el
    w0 = 2.0 * np.pi * f0_hz
    return w0 * val if kind == "L" else -1.0 / (w0 * val)


def _b_of_element(el, f0_hz=F0_HZ):
    kind, val = el
    w0 = 2.0 * np.pi * f0_hz
    return w0 * val if kind == "C" else -1.0 / (w0 * val)


def _fmt_edge(f_edge, side):
    if f_edge is None:
        return "<=2.000 (edge-limited)" if side == "lo" else \
               ">=2.800 (edge-limited)"
    return f"{f_edge/1e9:7.4f}"


def run_checks(mods=None):
    m = mods or dict(lsection_match=lsection_match, stub_match=stub_match,
                     rl_bandwidth_hz=rl_bandwidth_hz)
    print("=" * 72)
    print("hw3 --check : measured facts (instrument, not grade)")
    print("=" * 72)
    gl = complex(gamma_of_z(Z_ANT))
    print(f"the patient: Z_L = {Z_ANT.real:.0f}{Z_ANT.imag:+.0f}j ohm at "
          f"{F0_HZ/1e9:.1f} GHz -> |Gamma| = {abs(gl):.4f}, "
          f"SWR = {float(swr_of_gamma(gl)):.4f}, "
          f"RL = {float(return_loss_db(gl)):.2f} dB "
          f"(delivered {100*(1-abs(gl)**2):.1f}% unmatched)")

    # --- module 1: the L-section designer ----------------------------------
    print("\n[module 1] lsection_match")
    try:
        designs = m["lsection_match"](Z_ANT, Z0_OHM, F0_HZ)
        for i, d in enumerate(designs, 1):
            g0 = gamma_in_lsection(d, F0_HZ)
            x = _x_of_element(d["series"])
            z_mid = (Z_ANT + 1j * x) / Z0_OHM if d["topology"] == "series-first" \
                else None
            mid = (f", intermediate Re(y) = {(1/z_mid).real:.9f}"
                   if z_mid is not None else "")
            print(f"  sol {i} [{d['topology']}]: series {d['series'][0]} ="
                  f"{_fmt_element(d['series'])}, shunt {d['shunt'][0]} ="
                  f"{_fmt_element(d['shunt'])}"
                  f"  | skrf cascade |Gamma(f0)| = {abs(g0[0]):.2e}{mid}")
        other = m["lsection_match"](Z_REGION_CHECK, Z0_OHM, F0_HZ)
        for i, d in enumerate(other, 1):
            g0 = gamma_in_lsection(d, F0_HZ, z_load_ohm=Z_REGION_CHECK)
            print(f"  region check Z_L = 120+90j (R_L > Z0), sol {i} "
                  f"[{d['topology']}]: |Gamma(f0)| = {abs(g0[0]):.2e}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the stub designer ---------------------------------------
    print("\n[module 2] stub_match")
    try:
        sols = m["stub_match"](Z_ANT, Z0_OHM, kind="open")
        for i, d in enumerate(sols, 1):
            g0 = gamma_in_stub(d, F0_HZ)
            y_plane = Z0_OHM / zin_line(Z_ANT, Z0_OHM, d["d_lam"])
            print(f"  sol {i} ({d['kind']}): d = {d['d_lam']:.6f} lam "
                  f"({d['d_lam']*LAM0_M*1e3:6.2f} mm), l = {d['l_lam']:.6f} lam"
                  f" ({d['l_lam']*LAM0_M*1e3:6.2f} mm)"
                  f"  | y at stub plane = {y_plane.real:.6f}"
                  f"{y_plane.imag:+.6f}j | |Gamma(f0)| = {abs(g0[0]):.2e}")
        short = m["stub_match"](Z_ANT, Z0_OHM, kind="short")
        g0 = gamma_in_stub(short[-1], F0_HZ)
        print(f"  short-stub variant, sol {len(short)}: l = "
              f"{short[-1]['l_lam']:.6f} lam | |Gamma(f0)| = {abs(g0[0]):.2e}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the bandwidth measurer, then the comparison -------------
    print("\n[module 3] rl_bandwidth_hz")
    try:
        # planted analytic truth: |Gamma| = |f - f0| / 1 GHz crosses the
        # rl_db threshold at exactly f0 +- 1 GHz * 10^(-rl_db/20).
        f_syn = np.linspace(1.4e9, 3.4e9, 2001)
        g_syn = (f_syn - F0_HZ) / 1e9
        for rl in (10.0, 15.0):
            lo, hi = m["rl_bandwidth_hz"](f_syn, g_syn, F0_HZ, rl_db=rl)
            true_half = 1e9 * 10 ** (-rl / 20.0)
            err = max(abs(lo - (F0_HZ - true_half)), abs(hi - (F0_HZ + true_half)))
            print(f"  planted |Gamma| = |f-f0|/GHz, {rl:.0f}-dB edges: "
                  f"[{lo/1e9:.6f}, {hi/1e9:.6f}] GHz "
                  f"| vs closed form: err = {err:.2e} Hz")
        print("  the four designs, swept 2.0-2.8 GHz by the skrf referee:")
        table = [("L-section 1 (ser L, sh C)",
                  gamma_in_lsection(REF_LSECTION[0], F_BAND_HZ)),
                 ("L-section 2 (ser C, sh L)",
                  gamma_in_lsection(REF_LSECTION[1], F_BAND_HZ)),
                 ("stub 1 (d=0.495, open)",
                  gamma_in_stub(REF_STUB[0], F_BAND_HZ)),
                 ("stub 2 (d=0.199, open)",
                  gamma_in_stub(REF_STUB[1], F_BAND_HZ))]
        for name, g in table:
            worst = float(np.max(np.abs(g)))
            lo10, hi10 = m["rl_bandwidth_hz"](F_BAND_HZ, g, F0_HZ, rl_db=10.0)
            lo15, hi15 = m["rl_bandwidth_hz"](F_BAND_HZ, g, F0_HZ, rl_db=15.0)
            print(f"    {name:26s}: 10-dB edges [{_fmt_edge(lo10,'lo')}, "
                  f"{_fmt_edge(hi10,'hi')}] GHz | 15-dB edges "
                  f"[{_fmt_edge(lo15,'lo')}, {_fmt_edge(hi15,'hi')}] GHz | "
                  f"worst in-band RL = {return_loss_db(worst):5.2f} dB")
        print("  (raw unmatched load: RL = 10.90 dB flat — already past 10 dB."
              "\n   That is why edges go edge-limited; Q5 is about this.)")
        f_wide = np.linspace(0.5e9, 4.5e9, 4001)
        print("  wide sweep 0.5-4.5 GHz — where the 10-dB edges really live:")
        wide = [("L-section 1", gamma_in_lsection(REF_LSECTION[0], f_wide)),
                ("L-section 2", gamma_in_lsection(REF_LSECTION[1], f_wide)),
                ("stub 1", gamma_in_stub(REF_STUB[0], f_wide)),
                ("stub 2", gamma_in_stub(REF_STUB[1], f_wide))]
        for name, g in wide:
            lo, hi = m["rl_bandwidth_hz"](f_wide, g, F0_HZ, rl_db=10.0)
            lo_s = f"{lo/1e9:6.4f}" if lo is not None else "never (<0.5)"
            hi_s = f"{hi/1e9:6.4f}" if hi is not None else "never (>4.5)"
            bw = (f"BW = {(hi-lo)/1e6:7.1f} MHz"
                  if (lo is not None and hi is not None) else "BW = one-sided")
            print(f"    {name:12s}: 10-dB edges [{lo_s}, {hi_s}] GHz | {bw}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


# ----------------------------------------------------------------------------
# --smith : the pictures (chart trajectories + the band sweep)
# ----------------------------------------------------------------------------
def _gamma_of_y(y_norm):
    y = np.asarray(y_norm, dtype=complex)
    return (1 - y) / (1 + y)


def _traj_series(z_load_ohm, x_ohm, n=120):
    """Gamma path as a series reactance grows 0 -> x (constant-r arc)."""
    t = np.linspace(0.0, 1.0, n)
    return gamma_of_z(z_load_ohm + 1j * x_ohm * t)


def _traj_shunt_from(y_norm_start, b_norm, n=120):
    """Gamma path as normalized shunt susceptance grows 0 -> b (const-g arc)."""
    t = np.linspace(0.0, 1.0, n)
    return _gamma_of_y(y_norm_start + 1j * b_norm * t)


def _traj_rotate(gamma_load, d_lam, n=200):
    """Gamma path moving toward the generator along a line: const-|G| arc."""
    t = np.linspace(0.0, 1.0, n)
    return gamma_load * np.exp(-1j * 4.0 * np.pi * d_lam * t)


def make_smith(mods=None, show=True):
    import matplotlib.pyplot as plt
    from skrf.plotting import smith

    m = mods or dict(lsection_match=lsection_match, stub_match=stub_match,
                     rl_bandwidth_hz=rl_bandwidth_hz)
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.4))

    # --- panel 1: the chart, with both match trajectories ------------------
    ax = axes[0]
    smith(ax=ax, draw_labels=True)
    gl = complex(gamma_of_z(Z_ANT))
    ax.plot(gl.real, gl.imag, "ko", ms=7, zorder=5)
    ax.annotate("$z_L$", (gl.real, gl.imag), textcoords="offset points",
                xytext=(8, -12), fontsize=11)
    th = np.linspace(0, 2 * np.pi, 361)
    ax.plot(abs(gl) * np.cos(th), abs(gl) * np.sin(th), "k--", lw=0.8,
            alpha=0.5, label=f"SWR circle (|$\\Gamma$|={abs(gl):.3f})")
    ax.plot(-0.5 + 0.5 * np.cos(th), 0.5 * np.sin(th), "-", color="#2e7d32",
            lw=1.0, alpha=0.6, label="g = 1 circle (the target rail)")

    note = []
    try:
        lsec = m["lsection_match"](Z_ANT, Z0_OHM, F0_HZ)
    except NotImplementedError:
        lsec = REF_LSECTION
        note.append("module 1")
    try:
        stub = m["stub_match"](Z_ANT, Z0_OHM, kind="open")
    except NotImplementedError:
        stub = REF_STUB
        note.append("module 2")

    # L-section (first solution): series arc to g=1 circle, shunt arc home
    d0 = lsec[0]
    x = _x_of_element(d0["series"])
    b = _b_of_element(d0["shunt"]) * Z0_OHM         # normalized shunt b
    tr1 = _traj_series(Z_ANT, x)
    z_mid = (Z_ANT + 1j * x) / Z0_OHM
    tr2 = _traj_shunt_from(1.0 / z_mid, b)
    ax.plot(tr1.real, tr1.imag, "-", color="#0f62fe", lw=2.2,
            label="L-section: series arc")
    ax.plot(tr2.real, tr2.imag, "-", color="#7bb0ff", lw=2.2,
            label="L-section: shunt arc")
    gm = complex(gamma_of_z(z_mid * Z0_OHM))
    ax.plot(gm.real, gm.imag, "s", color="#0f62fe", ms=6, zorder=5)

    # stub (solution with the shortest d): rotate, then cancel along g=1
    dsel = min(stub, key=lambda s: s["d_lam"])
    tr3 = _traj_rotate(gl, dsel["d_lam"])
    y_plane = Z0_OHM / zin_line(Z_ANT, Z0_OHM, dsel["d_lam"])
    tr4 = _traj_shunt_from(y_plane, -y_plane.imag)
    ax.plot(tr3.real, tr3.imag, "-", color="#b3261e", lw=2.2,
            label=f"stub: line d={dsel['d_lam']:.3f}$\\lambda$ (rotation)")
    ax.plot(tr4.real, tr4.imag, "-", color="#ff9d9d", lw=2.2,
            label="stub: shunt-stub arc")
    gp = complex(_gamma_of_y(y_plane))
    ax.plot(gp.real, gp.imag, "d", color="#b3261e", ms=6, zorder=5)
    ax.plot(0, 0, "k+", ms=10, zorder=6)

    # the referee's own view: Gamma(f) of both finished designs over the band
    g_band_l = gamma_in_lsection(d0, F_BAND_HZ)
    g_band_s = gamma_in_stub(dsel, F_BAND_HZ)
    ax.plot(g_band_l.real, g_band_l.imag, ":", color="#0f62fe", lw=1.2,
            label="L-section, 2.0-2.8 GHz")
    ax.plot(g_band_s.real, g_band_s.imag, ":", color="#b3261e", lw=1.2,
            label="stub, 2.0-2.8 GHz")
    ttl = "the match trajectories (markers = intermediate points on g=1)"
    if note:
        ttl += ("\n" + " + ".join(note)
                + " not implemented — instructor design shown")
    ax.set_title(ttl, fontsize=10)
    ax.legend(fontsize=7.5, loc="lower left", framealpha=0.9)

    # --- panel 2: |Gamma(f)| as return loss, the product comparison --------
    ax = axes[1]
    f_ghz = F_BAND_HZ / 1e9
    for name, g, color in (("L-section (sol 1)", g_band_l, "#0f62fe"),
                           ("shunt stub (short-d sol)", g_band_s, "#b3261e")):
        ax.plot(f_ghz, return_loss_db(g), color=color, label=name)
    ax.axhline(return_loss_db(abs(gl)), color="gray", ls="-.", lw=1,
               label=f"unmatched load ({float(return_loss_db(gl)):.1f} dB)")
    ax.axhline(10.0, color="k", ls=":", lw=1, label="10-dB RL threshold")
    ax.axhline(15.0, color="k", ls=":", lw=0.7, alpha=0.5,
               label="15-dB RL threshold")
    try:
        for g, color in ((g_band_l, "#0f62fe"), (g_band_s, "#b3261e")):
            for rl in (10.0, 15.0):
                lo, hi = m["rl_bandwidth_hz"](F_BAND_HZ, g, F0_HZ, rl_db=rl)
                for edge in (lo, hi):
                    if edge is not None:
                        ax.axvline(edge / 1e9, color=color, ls="--",
                                   lw=0.8, alpha=0.5)
    except NotImplementedError:
        ax.set_title("module 3 not implemented (no measured edges)",
                     fontsize=10)
    ax.axvline(2.4, color="gray", lw=0.6, alpha=0.5)
    ax.set_xlabel("frequency (GHz)")
    ax.set_ylabel(r"return loss $-20\log_{10}|\Gamma|$ (dB)")
    ax.set_ylim(0, 45)
    ax.invert_yaxis()          # deeper match plots downward, RF convention
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="upper right")
    if not ax.get_title():
        ax.set_title("two products, one antenna", fontsize=10)

    fig.tight_layout()
    fig.savefig("hw3_smith.png", dpi=130)
    print("wrote hw3_smith.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--smith", action="store_true",
                    help="the chart + sweep pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.smith:
        make_smith()
    if not (args.check or args.smith):
        print(__doc__)


if __name__ == "__main__":
    main()
