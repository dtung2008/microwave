"""Homework 11 starter — Your first LNA.

A real vendor MMIC (Mini-Circuits PGA-103+, student-downloaded .s2p — see
HOMEWORK.md step 0) must become a single-stage 2.4 GHz low-noise amplifier.
You implement the three modules marked TODO below: the stability audit, the
gain design, and the gain-vs-noise trade. Everything else is the toolkit:
device loading (with an offline synthetic fallback), the instructor noise
model, L-section realization, the skrf referee, plotting, and the checker.

Run from this directory:

    python hw11_starter.py --check    # measured facts per module (the instrument)
    python hw11_starter.py --plot     # the three pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Conventions: S arrays are numpy (nf, 2, 2) complex, frequency-major, 50-ohm
reference, exactly as in hw4. Module-1 functions take the whole (nf, 2, 2)
stack; design happens at one frequency, so module-2/3 functions take a single
2x2 matrix `s1` (use S[at(f_hz, F0_HZ)]). Reflection coefficients are complex
Gammas in the source (Gamma_S) or load (Gamma_L) plane. `*_db` means decibels;
everything else is linear. |S12*S21| means abs of the product — taking abs of
each factor first is harmless here, but |S22 - D*conj(S11)| is one number, not
two: read every formula twice before typing it once.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
from pathlib import Path

import numpy as np

Z0_OHM = 50.0                     # course reference impedance
F0_HZ = 2.4e9                     # the LNA's design frequency
VENDOR_S2P = "PGA-103+_5V_Plus25DegC.s2p"   # HOMEWORK.md step 0 tells you how


# ----------------------------------------------------------------------------
# Toolkit — the device (provided; think in these nouns)
# ----------------------------------------------------------------------------
def demo_device():
    """Synthetic stand-in device — CLEARLY LABELED SYNTHETIC.

    A plausible conditionally-stable E-PHEMT-flavored two-port, 0.05-6 GHz:
    one-pole gain rolloff with transit-delay phase, reverse leakage growing
    with f (the C_gd feedback path), capacitive input reflection. Built so the
    whole homework runs offline; its numbers are NOT the PGA-103+'s. Returns
    a scikit-rf Network.
    """
    import skrf
    f_hz = np.arange(0.05e9, 6.0e9 + 1.0, 0.05e9)
    g = f_hz / 1e9
    s = np.zeros((len(f_hz), 2, 2), dtype=complex)
    s[:, 1, 0] = 13.0 / (1 + 1j * g / 1.1) * np.exp(-1j * 2 * np.pi * g * 0.06)
    s[:, 0, 1] = 0.033 * (g / 2.4) ** 0.8 * np.exp(1j * np.radians(62 - 8 * g))
    s[:, 0, 0] = 0.90 / (1 + 1j * g / 2.2) * np.exp(-1j * 2 * np.pi * g * 0.055)
    s[:, 1, 1] = 0.60 / (1 + 1j * g / 3.0) * np.exp(-1j * 2 * np.pi * g * 0.042)
    nt = skrf.Network(frequency=skrf.Frequency.from_f(f_hz, unit="hz"),
                      s=s, z0=Z0_OHM)
    nt.name = "demo_device (synthetic)"
    return nt


def the_device():
    """The homework's device: the vendor file if you downloaded it (step 0),
    else the synthetic fallback. Returns (Network, label)."""
    import skrf
    path = Path(__file__).resolve().parent / VENDOR_S2P
    if path.exists():
        nt = skrf.Network(str(path))
        return nt, f"vendor: {VENDOR_S2P} ({len(nt.f)} pts, " \
                   f"{nt.f[0]/1e6:.0f} MHz-{nt.f[-1]/1e9:.0f} GHz)"
    return demo_device(), (f"file not found: {VENDOR_S2P} — download step 0 "
                           "first; using demo_device() (synthetic)")


def at(f_grid_hz, f_hz):
    """Index of the grid point nearest f_hz. S[at(nt.f, F0_HZ)] is 'S at f0'."""
    return int(np.argmin(np.abs(np.asarray(f_grid_hz) - f_hz)))


# ----------------------------------------------------------------------------
# Toolkit — instructor noise model (provided)
#
# Vendor .s2p files carry NO noise data. The table below is INSTRUCTOR-
# MODELED: a plausible (F_min, Gamma_opt, R_n) set for a PGA-103+-class
# E-PHEMT MMIC, calibrated so that NF at Gamma_S = 0 reproduces the PGA-103+
# datasheet's 50-ohm noise-figure column (0.5 / 0.5 / 0.6 / 0.9 / 1.2 /
# 1.5 dB at 0.05 / 0.4 / 1 / 2 / 3 / 4 GHz, Vd = +5 V). It is teaching data,
# not vendor data — outside 0.05-4 GHz the interpolation clamps.
# ----------------------------------------------------------------------------
NOISE_TABLE = dict(
    f_hz=np.array([0.05e9, 0.4e9, 1.0e9, 2.0e9, 3.0e9, 4.0e9]),
    nfmin_db=np.array([0.227, 0.239, 0.360, 0.690, 1.014, 1.340]),
    gopt_mag=np.array([0.478, 0.462, 0.435, 0.390, 0.345, 0.300]),
    gopt_deg=np.array([19.2, 27.6, 42.0, 66.0, 90.0, 114.0]),
    rn_norm=np.array([0.160, 0.156, 0.150, 0.140, 0.130, 0.120]),  # R_n / Z0
)


def noise_params_at(f_hz):
    """(F_min linear, Gamma_opt complex, r_n = R_n/Z0) at frequency f_hz,
    linearly interpolated from NOISE_TABLE (clamped outside 0.05-4 GHz)."""
    t = NOISE_TABLE
    fmin = 10.0 ** (np.interp(f_hz, t["f_hz"], t["nfmin_db"]) / 10.0)
    mag = np.interp(f_hz, t["f_hz"], t["gopt_mag"])
    ang = np.radians(np.interp(f_hz, t["f_hz"], t["gopt_deg"]))
    rn = np.interp(f_hz, t["f_hz"], t["rn_norm"])
    return fmin, mag * np.exp(1j * ang), rn


def system_nf_db(nf1_db, g1_db, nf2_db):
    """Friis cascade (lecture 10) for two stages: system NF in dB given the
    first stage's NF and gain and the second stage's NF. For ANSWERS.md Q5."""
    f1 = 10.0 ** (nf1_db / 10.0)
    f2 = 10.0 ** (nf2_db / 10.0)
    g1 = 10.0 ** (g1_db / 10.0)
    return 10.0 * np.log10(f1 + (f2 - 1.0) / g1)


# ----------------------------------------------------------------------------
# Toolkit — dB helpers and hw4 nouns (provided)
# ----------------------------------------------------------------------------
def db10(x_lin):
    """Linear power ratio -> dB (10 log10)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def db20(x):
    """Amplitude (e.g. |S21|) -> dB (20 log10), floored to avoid log(0)."""
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-15))


def to_network(s, f_hz):
    """Wrap an (nf,2,2) S array as a scikit-rf Network (as in hw4)."""
    import skrf
    return skrf.Network(frequency=skrf.Frequency.from_f(f_hz, unit="hz"),
                        s=s, z0=Z0_OHM)


def abcd_series(z_ohm, f_hz):
    """ABCD of a series impedance z (scalar or length-nf): [[1, z], [0, 1]]."""
    a = np.zeros((len(f_hz), 2, 2), dtype=complex)
    a[:, 0, 0] = 1.0
    a[:, 1, 1] = 1.0
    a[:, 0, 1] = z_ohm
    return a


def abcd_shunt(y_s, f_hz):
    """ABCD of a shunt admittance y (scalar or length-nf): [[1, 0], [y, 1]]."""
    a = np.zeros((len(f_hz), 2, 2), dtype=complex)
    a[:, 0, 0] = 1.0
    a[:, 1, 1] = 1.0
    a[:, 1, 0] = y_s
    return a


def unitarity_residual(s):
    """hw4's lossless test: worst-over-frequency ||S^H S - I|| (Frobenius).
    Zero for a lossless network — the matchers below must pass it."""
    gram = np.conj(np.swapaxes(s, -1, -2)) @ s - np.eye(s.shape[-1])
    return float(np.linalg.norm(gram, axis=(-2, -1)).max())


# ----------------------------------------------------------------------------
# Toolkit — L-section realization (provided; lecture 3's machinery)
#
# lsection_for(gamma, ...) returns a lossless two-element L-section, designed
# at f0, such that looking into its port 2 (port 1 terminated in Z0) you see
# exactly `gamma` at f0. Elements are ideal Ls and Cs, so the network is
# exact at f0 and honest (frequency-dependent) everywhere else — which is
# what makes the swept gain plot worth staring at.
# ----------------------------------------------------------------------------
def lsection_for(gamma, f_hz, f0_hz=F0_HZ):
    """Lossless L-section Network presenting `gamma` at f0 into port 2."""
    from skrf.network import a2s
    z_t = Z0_OHM * (1 + gamma) / (1 - gamma)         # target source impedance
    r, x = z_t.real, z_t.imag
    w0 = 2 * np.pi * f0_hz
    w = 2 * np.pi * np.asarray(f_hz)

    def z_of_x(x0):                                  # series element vs f
        return 1j * w * (x0 / w0) if x0 >= 0 else 1.0 / (1j * w * (-1 / (w0 * x0)))

    def y_of_b(b0):                                  # shunt element vs f
        return 1j * w * (b0 / w0) if b0 >= 0 else 1.0 / (1j * w * (-1 / (w0 * b0)))

    if r <= Z0_OHM:                                  # shunt at source, series at device
        b = np.sqrt((Z0_OHM - r) / r) / Z0_OHM
        xs = x + b * Z0_OHM * r
        a = abcd_shunt(y_of_b(b), f_hz) @ abcd_series(z_of_x(xs), f_hz)
    else:                                            # series at source, shunt at device
        gcond = r / (r * r + x * x)
        xs = np.sqrt(Z0_OHM / gcond - Z0_OHM ** 2)
        bd = -x / (r * r + x * x) + xs * gcond / Z0_OHM
        a = abcd_series(z_of_x(xs), f_hz) @ abcd_shunt(y_of_b(bd), f_hz)
    return to_network(a2s(a, z0=Z0_OHM), f_hz)


def build_amp(nt, gamma_s, gamma_l):
    """The finished amplifier: input match ** device ** output match, all on
    the device's own frequency grid. With 50-ohm terminations, the cascade's
    |S21|^2 at f0 IS the transducer gain your design claims — the referee."""
    m_s = lsection_for(gamma_s, nt.f)                # source side
    m_l = lsection_for(gamma_l, nt.f).flipped()      # load side (mirrored)
    return m_s ** nt ** m_l


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def k_delta_mu(s):
    """Module 1 (the audit) — Rollett K, determinant Delta, and the mu-test,
    each as a length-nf array, from an (nf, 2, 2) S stack:

        Delta = S11*S22 - S12*S21
        K  = (1 - |S11|^2 - |S22|^2 + |Delta|^2) / (2 |S12*S21|)
        mu = (1 - |S11|^2) / ( |S22 - Delta*conj(S11)| + |S12*S21| )

    Return (k, delta, mu) — delta complex, k and mu real. Unconditional
    stability at a frequency means: K > 1 AND |Delta| < 1 (two conditions),
    or equivalently the single condition mu > 1."""
    raise NotImplementedError


def unstable_bands(f_hz, mu):
    """Module 1 — the verdict per band: list of (f_lo_hz, f_hi_hz) runs of
    consecutive grid points where mu < 1 (band edges at the grid points
    themselves; empty list if unconditionally stable everywhere)."""
    raise NotImplementedError


def stability_circles(s):
    """Module 1 — SOURCE and LOAD stability circles at every frequency.

    Return (c_s, r_s, c_l, r_l): complex centers and real radii, length-nf
    each. Load circle (the set of Gamma_L making |Gamma_in| = 1):

        C_L = conj(S22 - Delta*conj(S11)) / (|S22|^2 - |Delta|^2)
        R_L = |S12*S21| / | |S22|^2 - |Delta|^2 |

    Source circle: swap ports (S11 <-> S22) in both formulas."""
    raise NotImplementedError


def max_gain_db(s):
    """Module 2 (the core) — the design ceiling, length-nf array in dB:
    MAG = |S21/S12| * (K - sqrt(K^2 - 1)) where K > 1 (maximum available
    gain), and MSG = |S21/S12| where K <= 1 (maximum *stable* gain — a
    different animal: the ceiling you could reach only after resistive
    stabilization, quoted by every datasheet in the conditional region)."""
    raise NotImplementedError


def simultaneous_match(s1):
    """Module 2 (the core) — the simultaneous conjugate match at one
    frequency (2x2 s1, only meaningful where mu > 1). Return (gamma_ms,
    gamma_ml). With B1, B2, C1, C2 as in the lecture:

        Gamma_MS = (B1 - sqrt(B1^2 - 4|C1|^2)) / (2 C1)      [|Gamma| < 1 root]
        Gamma_ML = (B2 - sqrt(B2^2 - 4|C2|^2)) / (2 C2)

    Sanity: G_T at (Gamma_MS, Gamma_ML) must equal MAG — the checker
    measures exactly that."""
    raise NotImplementedError


def gt_db(s1, gamma_s, gamma_l):
    """Module 2 (the core) — transducer gain G_T in dB at one frequency:
    the gain the amplifier actually delivers between a source of reflection
    gamma_s and a load of reflection gamma_l:

        Gamma_in = S11 + S12*S21*Gamma_L / (1 - S22*Gamma_L)
        G_T = (1-|Gamma_S|^2) |S21|^2 (1-|Gamma_L|^2)
              / ( |1 - Gamma_in*Gamma_S|^2 |1 - S22*Gamma_L|^2 )"""
    raise NotImplementedError


def design_for_gain(s1, target_db):
    """Module 2 (the core) — pick (gamma_s, gamma_l) so the amplifier's G_T
    hits target_db at this frequency. The path is yours (HOMEWORK.md sketches
    the constant-available-gain-circle route); the contract is only:
    gt_db(s1, gamma_s, gamma_l) == target_db, and both |gamma| < 1. The
    cascade referee measures the result — not the method."""
    raise NotImplementedError


def nf_db(gamma_s, f_hz):
    """Module 3 (the trade) — noise figure in dB of the device with source
    reflection gamma_s at frequency f_hz, from the two-port noise model
    (noise_params_at gives F_min linear, Gamma_opt, r_n = R_n/Z0):

        F = F_min + 4 r_n |Gamma_S - Gamma_opt|^2
                    / ( (1 - |Gamma_S|^2) |1 + Gamma_opt|^2 )"""
    raise NotImplementedError


def frontier(s1, f_hz, n=41):
    """Module 3 (the trade) — the gain-vs-noise frontier at one frequency.
    Walk gamma_s along the straight segment from the gain match (Gamma_MS)
    to the noise match (Gamma_opt); at each point re-match the output
    (gamma_l = conj(Gamma_out)) so the trade is ONLY about the input side.
    Return (gt_db_array, nf_db_array), length n each, endpoint included."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Module 1's referees: skrf's own K (Network.stability), a plain determinant,
# and — for mu — the Edwards-Sinsky theorem itself: mu equals the distance
# from the Smith-chart center to the nearest unstable point in the Gamma_L
# plane, computed here from the load stability circle's geometry, an algebra
# path that never touches the mu formula. Module 2's referee is the cascade:
# build the matchers, multiply the networks, measure |S21|^2. Read these
# after you finish — they are the lecture in twenty lines.
# ----------------------------------------------------------------------------
def _mu_geometric(s):
    """mu via stability-circle geometry: | |C_L| - R_L | (load plane)."""
    d = s[:, 0, 0] * s[:, 1, 1] - s[:, 0, 1] * s[:, 1, 0]
    den = np.abs(s[:, 1, 1]) ** 2 - np.abs(d) ** 2
    c_l = np.conj(s[:, 1, 1] - d * np.conj(s[:, 0, 0])) / den
    r_l = np.abs(s[:, 0, 1] * s[:, 1, 0] / den)
    return np.abs(np.abs(c_l) - r_l)


def _kdm_referee(nt):
    """(K from skrf, Delta from the determinant, mu from geometry)."""
    return nt.stability, np.linalg.det(nt.s), _mu_geometric(nt.s)


def _bands_referee(f_hz, mu):
    """Runs of mu < 1 — the harness's own copy, kept dumb on purpose."""
    below = np.asarray(mu) < 1.0
    bands, i = [], 0
    while i < len(below):
        if below[i]:
            j = i
            while j + 1 < len(below) and below[j + 1]:
                j += 1
            bands.append((float(f_hz[i]), float(f_hz[j])))
            i = j + 1
        else:
            i += 1
    return bands


def _fmt_band(b):
    return f"{b[0]/1e9:.3f}-{b[1]/1e9:.3f} GHz"


def _circle_check(nt, i, which, c, r):
    """Worst distance of skrf's stability_circle locus from your circle."""
    pts = nt[i].stability_circle(target_port=0 if which == "s" else 1,
                                 npoints=91)[:, 0]
    return float(np.abs(np.abs(pts - c) - r).max())


def _pick_circle_freqs(f_hz, mu):
    """Three audit frequencies: the mu minimum, the last mu < 1 point, f0."""
    fa = float(f_hz[int(np.argmin(mu))])
    below = np.asarray(mu) < 1.0
    fb = float(f_hz[np.flatnonzero(below)[-1]]) if below.any() else fa
    return [fa, fb, float(f_hz[at(f_hz, F0_HZ)])]


def run_checks(mods=None):
    m = mods or dict(k_delta_mu=k_delta_mu, unstable_bands=unstable_bands,
                     stability_circles=stability_circles,
                     max_gain_db=max_gain_db,
                     simultaneous_match=simultaneous_match, gt_db=gt_db,
                     design_for_gain=design_for_gain, nf_db=nf_db,
                     frontier=frontier)
    print("=" * 64)
    print("hw11 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    nt, label = the_device()
    print(f"\n[device] {label}")
    f_hz = nt.f
    s = nt.s
    i0 = at(f_hz, F0_HZ)
    print(f"  design grid point: {f_hz[i0]/1e9:.3f} GHz;  "
          f"|S21|^2 there = {db20(s[i0, 1, 0]):.3f} dB  (not yet a gain claim)")

    # --- module 1: the stability audit -------------------------------------
    print("\n[module 1] k_delta_mu / unstable_bands / stability_circles")
    try:
        k, d, mu = m["k_delta_mu"](s)
        k_ref, d_ref, mu_ref = _kdm_referee(nt)
        print(f"  at f0: K = {float(k[i0]):.6f}   |Delta| = "
              f"{float(np.abs(d[i0])):.6f}   mu = {float(mu[i0]):.6f}")
        print(f"  vs referees, worst over the whole file: "
              f"dK = {float(np.abs(k - k_ref).max()):.2e}  "
              f"dDelta = {float(np.abs(d - d_ref).max()):.2e}  "
              f"dmu(geometric) = {float(np.abs(mu - mu_ref).max()):.2e}"
              "   (syllabus bar 1e-8)")
        kd_verdict = (k > 1) & (np.abs(d) < 1)
        agree = int((kd_verdict == (mu > 1)).sum())
        print(f"  K-Delta verdict vs mu verdict: agree at {agree}/{len(mu)} "
              "frequencies  (the theorem says all)")
        bands = m["unstable_bands"](f_hz, mu)
        bands_ref = _bands_referee(f_hz, mu_ref)
        print(f"  mu < 1 bands: {[_fmt_band(b) for b in bands] or 'none'}"
              f"   (referee: {[_fmt_band(b) for b in bands_ref] or 'none'})")
        print(f"  worst mu = {float(mu.min()):.4f} at "
              f"{f_hz[int(np.argmin(mu))]/1e9:.3f} GHz;  mu(f0) = "
              f"{float(mu[i0]):.4f}")
        c_s, r_s, c_l, r_l = m["stability_circles"](s)
        worst = 0.0
        for fc in _pick_circle_freqs(f_hz, mu_ref):
            i = at(f_hz, fc)
            worst = max(worst,
                        _circle_check(nt, i, "s", c_s[i], r_s[i]),
                        _circle_check(nt, i, "l", c_l[i], r_l[i]))
        print(f"  circles vs skrf stability_circle loci (3 audit freqs), "
              f"worst |dist - R| = {worst:.2e}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the gain design -----------------------------------------
    print("\n[module 2] max_gain_db / simultaneous_match / gt_db / "
          "design_for_gain")
    try:
        gmax = m["max_gain_db"](s)
        d_gmax = float(np.abs(gmax - db10(nt.max_gain)).max())
        print(f"  max_gain_db vs skrf max_gain, worst over file = "
              f"{d_gmax:.2e} dB   (MSG where K<=1, MAG where K>1)")
        print(f"  at f0: MAG = {float(gmax[i0]):.4f} dB   MSG = "
              f"{db10(nt.max_stable_gain[i0]):.4f} dB   |S21|^2 = "
              f"{db20(s[i0, 1, 0]):.4f} dB")
        gms, gml = m["simultaneous_match"](s[i0])
        gt_at_match = float(m["gt_db"](s[i0], gms, gml))
        print(f"  Gamma_MS = {np.abs(gms):.4f} < {np.degrees(np.angle(gms)):.1f} deg   "
              f"Gamma_ML = {np.abs(gml):.4f} < {np.degrees(np.angle(gml)):.1f} deg")
        print(f"  G_T at the simultaneous match = {gt_at_match:.4f} dB; "
              f"G_T - MAG = {gt_at_match - float(gmax[i0]):+.2e} dB "
              "(identity: 0)")
        target_db = float(gmax[i0]) - 2.0
        gs, gl = m["design_for_gain"](s[i0], target_db)
        claimed = float(m["gt_db"](s[i0], gs, gl))
        amp = build_amp(nt, gs, gl)
        realized = float(db20(amp.s[i0, 1, 0]))
        m_s = lsection_for(gs, f_hz)
        m_l = lsection_for(gl, f_hz)
        print(f"  target G_T = MAG - 2 dB = {target_db:.4f} dB")
        print(f"  your design: Gamma_S = {np.abs(gs):.4f} < "
              f"{np.degrees(np.angle(gs)):.1f} deg,  Gamma_L = {np.abs(gl):.4f} < "
              f"{np.degrees(np.angle(gl)):.1f} deg  ->  formula G_T = {claimed:.4f} dB")
        print(f"  cascade referee: |S21|^2 of matchers**device**matchers at f0"
              f" = {realized:.4f} dB;  vs target = {realized - target_db:+.2e} dB"
              "   (syllabus bar 0.1 dB)")
        print(f"  matcher losslessness ||S^H S - I||: input {unitarity_residual(m_s.s):.1e}"
              f", output {unitarity_residual(m_l.s):.1e}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the trade -----------------------------------------------
    print("\n[module 3] nf_db / frontier")
    try:
        fmin, gopt, rn = noise_params_at(F0_HZ)
        print(f"  noise model at f0: NF_min = {db10(fmin):.4f} dB, Gamma_opt "
              f"= {np.abs(gopt):.3f} < {np.degrees(np.angle(gopt)):.1f} deg, "
              f"R_n/Z0 = {rn:.3f}   (instructor-modeled; .s2p carries no noise)")
        print(f"  NF at Gamma_S = 0      : {float(m['nf_db'](0.0, F0_HZ)):.4f} dB"
              "   (the datasheet's 50-ohm NF)")
        print(f"  NF at Gamma_S = G_opt  : {float(m['nf_db'](gopt, F0_HZ)):.4f} dB"
              "   (= NF_min by construction)")
        gms, gml = m["simultaneous_match"](s[i0])
        print(f"  NF at the gain match   : {float(m['nf_db'](gms, F0_HZ)):.4f} dB"
              "   (what max gain costs in noise)")
        gt_f, nf_f = m["frontier"](s[i0], F0_HZ)
        s1 = s[i0]
        gout = s1[1, 1] + s1[0, 1] * s1[1, 0] * gopt / (1 - s1[0, 0] * gopt)
        gt_opt = float(m["gt_db"](s1, gopt, np.conj(gout)))
        gmax0 = float(m["max_gain_db"](s)[i0])
        print(f"  G_T at the noise match (output re-matched) = {gt_opt:.4f} dB"
              f";  the Gamma_opt move costs {gmax0 - gt_opt:.4f} dB of G_T"
              "   (ANSWERS Q2's number)")
        viol_g = int(np.sum(np.diff(gt_f) > 1e-9))
        viol_n = int(np.sum(np.diff(nf_f) > 1e-9))
        print(f"  frontier ({len(gt_f)} pts, gain match -> noise match): "
              f"G_T {gt_f[0]:.3f} -> {gt_f[-1]:.3f} dB, NF {nf_f[0]:.3f} -> "
              f"{nf_f[-1]:.3f} dB")
        print(f"  monotone? G_T rises {viol_g} times, NF rises {viol_n} times "
              "along the walk  (expected: 0 and 0)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(k_delta_mu=k_delta_mu, stability_circles=stability_circles,
                     max_gain_db=max_gain_db,
                     simultaneous_match=simultaneous_match, gt_db=gt_db,
                     design_for_gain=design_for_gain, nf_db=nf_db,
                     frontier=frontier)
    nt, label = the_device()
    f_hz, s = nt.f, nt.s
    i0 = at(f_hz, F0_HZ)
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.6))

    # --- picture 1: the whole-band audit (Q1's picture) --------------------
    try:
        k, d, mu = m["k_delta_mu"](s)
        axes[0].semilogx(f_hz / 1e9, mu, label=r"$\mu$")
        axes[0].semilogx(f_hz / 1e9, np.clip(k, -1, 5), label="K (clipped)")
        axes[0].axhline(1.0, color="k", ls=":", lw=1.2)
        axes[0].axvline(F0_HZ / 1e9, color="tab:green", ls="--", alpha=0.6,
                        label=r"$f_0$ = 2.4 GHz")
        below = mu < 1
        axes[0].fill_between(f_hz / 1e9, -1, 5, where=below,
                             color="tab:red", alpha=0.15,
                             label=r"$\mu < 1$: conditional")
        axes[0].set_xlabel("frequency (GHz), log")
        axes[0].set_ylabel(r"$\mu$, K")
        axes[0].set_ylim(-0.5, 3.0)
        axes[0].set_title("the stability audit: whole file, not just $f_0$")
        axes[0].legend(fontsize=8, loc="lower right")
        axes[0].grid(True, which="both", alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 1 not implemented")

    # --- picture 2: the Gamma_S plane at f0 (design real estate) -----------
    try:
        th = np.linspace(0, 2 * np.pi, 361)
        axes[1].plot(np.cos(th), np.sin(th), "k", lw=1.0)
        c_s, r_s, c_l, r_l = m["stability_circles"](s)
        _, _, mu_ref = _kdm_referee(nt)
        for fc, col in zip(_pick_circle_freqs(f_hz, mu_ref),
                           ["tab:red", "tab:orange", "tab:blue"]):
            i = at(f_hz, fc)
            axes[1].plot(np.real(c_s[i]) + r_s[i] * np.cos(th),
                         np.imag(c_s[i]) + r_s[i] * np.sin(th),
                         color=col, lw=1.4,
                         label=f"src stab. circle {f_hz[i]/1e9:.2f} GHz")
        gms, _ = m["simultaneous_match"](s[i0])
        _, gopt, _ = noise_params_at(F0_HZ)
        gmax0 = float(m["max_gain_db"](s)[i0])
        gs, gl = m["design_for_gain"](s[i0], gmax0 - 2.0)
        axes[1].plot(gms.real, gms.imag, "s", color="tab:blue",
                     label=r"$\Gamma_{MS}$ (gain match)")
        axes[1].plot(gopt.real, gopt.imag, "*", ms=12, color="tab:green",
                     label=r"$\Gamma_{opt}$ (noise match)")
        axes[1].plot(gs.real, gs.imag, "o", color="tab:purple",
                     label=r"your $\Gamma_S$ (MAG$-$2 dB)")
        axes[1].set_aspect("equal")
        axes[1].set_xlim(-1.6, 1.6)
        axes[1].set_ylim(-1.6, 1.6)
        axes[1].set_title(r"$\Gamma_S$ plane: stability circles + the "
                          "two matches")
        axes[1].legend(fontsize=7, loc="lower left")
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("modules 1+2 not implemented")

    # --- picture 3: the frontier (Q2's picture) ----------------------------
    try:
        gt_f, nf_f = m["frontier"](s[i0], F0_HZ)
        axes[2].plot(nf_f, gt_f, "-o", ms=3)
        axes[2].plot(nf_f[0], gt_f[0], "s", color="tab:blue", ms=9,
                     label="gain match end")
        axes[2].plot(nf_f[-1], gt_f[-1], "*", color="tab:green", ms=14,
                     label="noise match end")
        axes[2].set_xlabel("noise figure (dB)")
        axes[2].set_ylabel(r"$G_T$ (dB), output re-matched")
        axes[2].set_title("the LNA frontier: what gain costs in noise")
        axes[2].legend(fontsize=8)
        axes[2].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[2].set_title("module 3 not implemented")

    fig.suptitle(label, fontsize=9)
    fig.tight_layout()
    fig.savefig("hw11_plots.png", dpi=130)
    print("wrote hw11_plots.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--plot", action="store_true",
                    help="the three pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.plot:
        make_plots()
    if not (args.check or args.plot):
        print(__doc__)


if __name__ == "__main__":
    main()
