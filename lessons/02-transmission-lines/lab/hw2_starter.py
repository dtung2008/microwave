"""Homework 2 starter — The feed line that lies.

You implement the three modules marked TODO below. Everything else is the
toolkit: the cable and antenna specs, ideal-line builders, the scikit-rf
referee, plotting, and the checker.

Run from this directory:

    python hw2_starter.py --check    # measured facts per module (the instrument)
    python hw2_starter.py --sweep    # the pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_ohm` is ohms, `*_m` meters, `*_hz` hertz,
`*_db` decibels. Two different gammas live in this file and they are never
the same thing: `gamma_per_m` is the propagation constant (complex, 1/m);
a bare reflection coefficient is always called `refl` (complex,
dimensionless). Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np

# ----------------------------------------------------------------------------
# The systems (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
F0_HZ = 2.4e9          # the station's operating frequency

# An RG-58-like coax, described the way lecture 2 describes every line: by its
# per-meter RLGC cell. R and G are FROZEN at their 2.4 GHz values (a real
# cable's R grows as sqrt(f) with skin effect — lecture 5's fine print), so
# alpha is nearly flat across our 2.0-2.8 GHz sweep. That is a modeling
# choice, stated out loud.
RG58 = dict(
    r_ohm_m=10.0,      # series resistance per meter (at 2.4 GHz)
    l_h_m=250e-9,      # series inductance per meter
    g_s_m=4.5e-4,      # shunt conductance per meter (dielectric, at 2.4 GHz)
    c_f_m=100e-12,     # shunt capacitance per meter
)

FEED_M = 10.0                  # the feed run: 10 m of RG58 to the mast
Z_ANT_OHM = 36.0 - 21.0j       # the antenna at 2.4 GHz (frozen across the
                               # sweep to isolate LINE behavior; it returns,
                               # frequency-dependence and all, in lecture 3)
Z0_SYS_OHM = 50.0              # system / generator reference impedance
BAND_HZ = np.linspace(2.0e9, 2.8e9, 401)      # the course sweep
WIDE_HZ = np.linspace(0.1e9, 4.8e9, 47001)    # module 3's bandwidth scan


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> dB (lecture 1's module, now toolkit)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """dB -> linear power ratio (lecture 1's module, now toolkit)."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def rl_db(refl):
    """Return loss (dB, positive) of a reflection coefficient: -db(|refl|^2)."""
    return -db(np.abs(refl) ** 2)


def vp_m_s(line):
    """Phase velocity 1/sqrt(L'C') of a line's lossless skeleton."""
    return 1.0 / np.sqrt(line["l_h_m"] * line["c_f_m"])


def ideal_line(z0_ohm, v_m_s):
    """Build a LOSSLESS line (RLGC dict, R=G=0) with characteristic impedance
    z0_ohm and phase velocity v_m_s. Use it for matching sections."""
    return dict(r_ohm_m=0.0, l_h_m=z0_ohm / v_m_s,
                g_s_m=0.0, c_f_m=1.0 / (z0_ohm * v_m_s))


def lossless(line):
    """The same line with its loss switched off (R=G=0). The energy-
    conservation invariant is exact only here."""
    return dict(line, r_ohm_m=0.0, g_s_m=0.0)


def band_edges_hz(f_hz, refl, rl_level_db, f0_hz):
    """Contiguous band around f0_hz where return loss >= rl_level_db.
    Returns (f_lo, f_hi) with linearly interpolated edges; an edge that
    never crosses inside the scan comes back as the scan end."""
    f = np.asarray(f_hz, dtype=float)
    mag = np.abs(refl)
    thr = 10.0 ** (-rl_level_db / 20.0)
    inside = mag <= thr
    i0 = int(np.argmin(np.abs(f - f0_hz)))
    lo, hi = i0, i0
    while lo > 0 and inside[lo - 1]:
        lo -= 1
    while hi < len(f) - 1 and inside[hi + 1]:
        hi += 1

    def _edge(a, b):
        return f[a] + (thr - mag[a]) * (f[b] - f[a]) / (mag[b] - mag[a])

    f_lo = _edge(lo, lo - 1) if lo > 0 else f[0]
    f_hi = _edge(hi, hi + 1) if hi < len(f) - 1 else f[-1]
    return f_lo, f_hi


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def propagation(line, f_hz):
    """Module 1 (the core) — the telegrapher's verdict on one RLGC cell.

    `line` is an RLGC dict like RG58. Return (gamma_per_m, z0_ohm) at
    frequency f_hz: the complex propagation constant gamma = alpha + j*beta
    (1/m) and the complex characteristic impedance (ohms). Vectorized in
    f_hz. Hour 1 derived both from (R' + jwL') and (G' + jwC')."""
    raise NotImplementedError


def reflection(z_ohm, z0_ohm):
    """Module 1 — reflection coefficient of impedance z_ohm against
    reference z0_ohm. Complex in, complex out, vectorized."""
    raise NotImplementedError


def swr(refl):
    """Module 1 — standing wave ratio of a reflection coefficient.
    Vectorized. SWR = 1 for a match; -> infinity as |refl| -> 1."""
    raise NotImplementedError


def z_in(line, z_l_ohm, ell_m, f_hz):
    """Module 1 (the core) — input impedance of a length ell_m of `line`
    terminated in z_l_ohm, at frequency f_hz. Must broadcast over ell_m OR
    f_hz given as arrays. Hour 2 derived this (the tangent transformation);
    your version must survive loss (use the lossy form, not the lossless
    tangent) and must not blow up at the quarter-wave point."""
    raise NotImplementedError


def power_ledger(line, z_l_ohm, ell_m, f_hz):
    """Module 2 — where every watt goes.

    One watt of wave power is incident on the line's input (the generator
    is matched: nothing re-reflects at the source). Return a dict with:

      reflected_frac   -- fraction that comes back OUT of the input
      delivered_frac   -- fraction that ends up in the load
      dissipated_frac  -- fraction turned to heat in the line
      line_loss_db     -- the line's one-way loss, dB (positive)
      mismatch_loss_db -- the load's mismatch loss, dB (positive)

    The three fractions must sum to 1 (lossless case: to 1 within 1e-12 —
    the checker measures the residual). Scalar f_hz is enough."""
    raise NotImplementedError


def quarter_wave_fix(line, z_l_ohm, f0_hz):
    """Module 3 — design the lambda/4 fix at the antenna end.

    A quarter-wave transformer only matches REAL impedances, and the
    antenna's is not. Find the SHORTEST spacer of ideal 50-ohm line (same
    phase velocity as `line`) that rotates the antenna to a purely real
    impedance (Q1 in ANSWERS.md predicts where), then size the transformer
    that matches that plane to 50 ohms. Return a dict with:

      spacer_m      -- spacer length, m
      r_plane_ohm   -- the (real) impedance at the spacer's input, ohms
      zt_ohm        -- transformer characteristic impedance, ohms
      ell_t_m       -- transformer length (a quarter wave at f0_hz), m

    Design with the IDEAL line's phase constant (beta = 2*pi*f/vp), not the
    lossy cable's — they differ in the 6th digit and the |Gamma(f0)| < 1e-10
    criterion notices."""
    raise NotImplementedError


def fix_gamma(fix, z_l_ohm, f_hz):
    """Module 3 — the fix, measured. Return the complex reflection
    coefficient seen at the transformer's input (reference Z0_SYS_OHM) for
    the assembly [transformer][spacer][antenna], both sections built as
    ideal lossless lines (toolkit `ideal_line`) at the cable's phase
    velocity. Vectorized in f_hz — the checker sweeps it for bandwidth."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# The referee: scikit-rf's DistributedCircuit computes gamma and z0 from the
# same RLGC cell by its own code path, and DefinedGammaZ0 rebuilds module
# 3's assembly from nothing but gamma and z0. Two independent
# implementations; when they disagree, someone's algebra is wrong.
# ----------------------------------------------------------------------------
def _skrf_medium(line, f_hz):
    import skrf
    from skrf.media import DistributedCircuit

    fr = skrf.Frequency.from_f(np.atleast_1d(np.asarray(f_hz, float)),
                               unit="hz")
    return DistributedCircuit(frequency=fr, R=line["r_ohm_m"],
                              L=line["l_h_m"], G=line["g_s_m"],
                              C=line["c_f_m"])


def _skrf_zin_referee(line, z_l_ohm, ell_m, f_hz):
    """Z_in of the terminated line from skrf's gamma/z0 (its own RLGC
    solution) plus the reflection-propagation identity — a code path with
    no tanh in it."""
    med = _skrf_medium(line, f_hz)
    refl_l = (z_l_ohm - med.z0) / (z_l_ohm + med.z0)
    refl_in = refl_l * np.exp(-2.0 * med.gamma * ell_m)
    return med.z0 * (1.0 + refl_in) / (1.0 - refl_in)


def _skrf_fix_referee(fix, z_l_ohm, f_hz):
    """Module 3's assembly rebuilt in skrf: two DefinedGammaZ0 media
    (spacer at 50 ohms, transformer at zt), ports renormalized to 50, then
    cascaded onto the antenna. Returns the assembly's reflection
    coefficient."""
    import skrf
    from skrf.media import DefinedGammaZ0

    f = np.atleast_1d(np.asarray(f_hz, float))
    fr = skrf.Frequency.from_f(f, unit="hz")
    v = vp_m_s(RG58)
    beta = 2.0 * np.pi * f / v
    med_sp = DefinedGammaZ0(frequency=fr, z0=Z0_SYS_OHM, gamma=1j * beta,
                            z0_port=Z0_SYS_OHM)
    med_t = DefinedGammaZ0(frequency=fr, z0=fix["zt_ohm"], gamma=1j * beta,
                           z0_port=Z0_SYS_OHM)
    refl_l = np.full(len(f), (z_l_ohm - Z0_SYS_OHM) / (z_l_ohm + Z0_SYS_OHM))
    asm = (med_t.line(fix["ell_t_m"], unit="m")
           ** med_sp.line(fix["spacer_m"], unit="m")
           ** med_sp.load(refl_l))
    return asm.s[:, 0, 0]


def run_checks(mods=None):
    m = mods or dict(propagation=propagation, reflection=reflection, swr=swr,
                     z_in=z_in, power_ledger=power_ledger,
                     quarter_wave_fix=quarter_wave_fix, fix_gamma=fix_gamma)
    print("=" * 64)
    print("hw2 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: the line engine vs the skrf referee ---------------------
    print("\n[module 1] propagation / reflection / swr / z_in")
    try:
        gam, z0 = m["propagation"](RG58, F0_HZ)
        gam, z0 = complex(gam), complex(z0)
        print(f"  z0(2.4 GHz)  = {z0.real:.4f} {z0.imag:+.4f}j ohm")
        print(f"  alpha        = {gam.real:.6f} Np/m = "
              f"{gam.real * 20 / np.log(10):.4f} dB/m "
              f"-> {FEED_M:.0f} m one-way = "
              f"{gam.real * 20 / np.log(10) * FEED_M:.2f} dB")
        v = 2 * np.pi * F0_HZ / gam.imag
        print(f"  beta         = {gam.imag:.4f} rad/m -> vp = {v:.4g} m/s"
              f" ({v / 299792458.0:.3f} c), lambda = "
              f"{v / F0_HZ * 1e3:.2f} mm")
        print(f"  the 10 m feed is {FEED_M * F0_HZ / v:.1f} wavelengths"
              " long at f0 (electrically long is an understatement)")
        med = _skrf_medium(RG58, BAND_HZ)
        gams, z0s = m["propagation"](RG58, BAND_HZ)
        e_g = np.max(np.abs(gams - med.gamma) / np.abs(med.gamma))
        e_z = np.max(np.abs(z0s - med.z0) / np.abs(med.z0))
        print(f"  vs skrf DistributedCircuit over 2.0-2.8 GHz: "
              f"gamma rel err = {e_g:.2e}, z0 rel err = {e_z:.2e}")
        refl_l = complex(m["reflection"](Z_ANT_OHM, Z0_SYS_OHM))
        print(f"  antenna: Gamma_L = {abs(refl_l):.4f} at "
              f"{np.degrees(np.angle(refl_l)):.2f} deg, "
              f"SWR = {float(m['swr'](refl_l)):.4f}, "
              f"RL = {float(rl_db(refl_l)):.2f} dB")
        zin_me = m["z_in"](RG58, Z_ANT_OHM, FEED_M, BAND_HZ)
        zin_ref = _skrf_zin_referee(RG58, Z_ANT_OHM, FEED_M, BAND_HZ)
        e_zin = np.max(np.abs(zin_me - zin_ref) / np.abs(zin_ref))
        print(f"  z_in(10 m) vs skrf referee across the sweep: "
              f"max rel err = {e_zin:.2e}   (criterion: 1e-6)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the power ledger ----------------------------------------
    print("\n[module 2] power_ledger")
    try:
        led = m["power_ledger"](RG58, Z_ANT_OHM, FEED_M, F0_HZ)
        tot = (led["reflected_frac"] + led["delivered_frac"]
               + led["dissipated_frac"])
        print(f"  at f0, of 1 W incident on the feed: "
              f"delivered {led['delivered_frac']*1e3:.1f} mW, "
              f"reflected {led['reflected_frac']*1e3:.2f} mW, "
              f"heat {led['dissipated_frac']*1e3:.1f} mW  "
              f"(sum = {tot:.12f})")
        print(f"  line loss (one way) = {led['line_loss_db']:.2f} dB, "
              f"mismatch loss = {led['mismatch_loss_db']:.2f} dB   "
              f"(delivered sits {-db(led['delivered_frac']):.2f} dB below"
              " incident — the two taxes add)")
        ll = m["power_ledger"](lossless(RG58), Z_ANT_OHM, FEED_M, F0_HZ)
        resid = abs(ll["reflected_frac"] + ll["delivered_frac"] - 1.0)
        print(f"  lossless line: |Gamma|^2 + delivered - 1 = {resid:.2e}"
              "   (criterion: 1e-12)")
        zin0 = complex(m["z_in"](RG58, Z_ANT_OHM, FEED_M, F0_HZ))
        refl_in = complex(m["reflection"](zin0, Z0_SYS_OHM))
        refl_l = complex(m["reflection"](Z_ANT_OHM, Z0_SYS_OHM))
        print(f"  THE LIE: return loss at the antenna = "
              f"{float(rl_db(refl_l)):.2f} dB; at the transmitter end of"
              f" 10 m = {float(rl_db(refl_in)):.2f} dB"
              "   (RL_in = RL_L + 2 x line loss)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the lambda/4 fix ----------------------------------------
    print("\n[module 3] quarter_wave_fix / fix_gamma")
    try:
        fix = m["quarter_wave_fix"](RG58, Z_ANT_OHM, F0_HZ)
        lam = vp_m_s(RG58) / F0_HZ
        print(f"  spacer = {fix['spacer_m']*1e3:.4f} mm = "
              f"{fix['spacer_m']/lam:.4f} lambda; plane impedance = "
              f"{fix['r_plane_ohm']:.4f} ohm (compare Z0/SWR)")
        print(f"  transformer: Z_T = {fix['zt_ohm']:.4f} ohm, "
              f"ell_T = {fix['ell_t_m']*1e3:.4f} mm")
        r0 = complex(m["fix_gamma"](fix, Z_ANT_OHM, F0_HZ))
        r0_ref = complex(_skrf_fix_referee(fix, Z_ANT_OHM, F0_HZ))
        print(f"  |Gamma(f0)| = {abs(r0):.2e}   (criterion: 1e-10);"
              f" skrf rebuild says {abs(r0_ref):.2e}")
        sw = m["fix_gamma"](fix, Z_ANT_OHM, WIDE_HZ)
        sw_ref = _skrf_fix_referee(fix, Z_ANT_OHM, BAND_HZ)
        sw_me = m["fix_gamma"](fix, Z_ANT_OHM, BAND_HZ)
        e_fx = np.max(np.abs(sw_me - sw_ref))
        print(f"  vs skrf rebuild across 2.0-2.8 GHz: max |diff| = {e_fx:.2e}")
        lo10, hi10 = band_edges_hz(WIDE_HZ, sw, 10.0, F0_HZ)
        lo20, hi20 = band_edges_hz(WIDE_HZ, sw, 20.0, F0_HZ)
        print(f"  10-dB-RL band: {lo10/1e9:.4f}-{hi10/1e9:.4f} GHz = "
              f"{(hi10-lo10)/1e6:.1f} MHz ({(hi10-lo10)/F0_HZ*100:.1f}% of"
              " f0)")
        print(f"  20-dB-RL band: {lo20/1e9:.4f}-{hi20/1e9:.4f} GHz = "
              f"{(hi20-lo20)/1e6:.1f} MHz ({(hi20-lo20)/F0_HZ*100:.1f}%)"
              "   (the price of the deep null: it is narrow)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_sweep(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(propagation=propagation, reflection=reflection,
                     z_in=z_in, power_ledger=power_ledger,
                     quarter_wave_fix=quarter_wave_fix, fix_gamma=fix_gamma)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    f_ghz = BAND_HZ / 1e9

    # --- picture 1: return loss at three planes (Q2's picture) -------------
    try:
        refl_l = m["reflection"](Z_ANT_OHM, Z0_SYS_OHM)
        zin_f = m["z_in"](RG58, Z_ANT_OHM, FEED_M, BAND_HZ)
        refl_in = m["reflection"](zin_f, Z0_SYS_OHM)
        axes[0].plot(f_ghz, np.full_like(BAND_HZ, rl_db(refl_l)),
                     label="at the antenna (the truth)")
        axes[0].plot(f_ghz, rl_db(refl_in),
                     label="at the transmitter (the lie)")
        try:
            fix = m["quarter_wave_fix"](RG58, Z_ANT_OHM, F0_HZ)
            rfx = m["fix_gamma"](fix, Z_ANT_OHM, BAND_HZ)
            axes[0].plot(f_ghz, rl_db(rfx),
                         label="antenna + lambda/4 fix")
        except NotImplementedError:
            pass
        axes[0].axhline(10.0, color="k", ls=":", alpha=0.7,
                        label="10-dB RL")
        axes[0].set_xlabel("frequency (GHz)")
        axes[0].set_ylabel("return loss (dB)")
        axes[0].set_title("the same antenna, three measurement planes")
        axes[0].set_ylim(0, 60)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 1 not implemented")

    # --- picture 2: where the watts go, vs frequency (Q3's picture) --------
    try:
        bare = np.array([m["power_ledger"](RG58, Z_ANT_OHM, FEED_M, f)
                         ["delivered_frac"] for f in BAND_HZ[::10]])
        axes[1].plot(f_ghz[::10], db(bare), label="delivered, bare antenna")
        try:
            fix = m["quarter_wave_fix"](RG58, Z_ANT_OHM, F0_HZ)
            rfx = m["fix_gamma"](fix, Z_ANT_OHM, BAND_HZ[::10])
            gam, _ = m["propagation"](RG58, BAND_HZ[::10])
            thru = np.exp(-2.0 * gam.real * FEED_M)
            axes[1].plot(f_ghz[::10], db(thru * (1 - np.abs(rfx) ** 2)),
                         label="delivered, with the fix")
        except NotImplementedError:
            pass
        axes[1].axhline(db(np.exp(-2.0 * complex(
            m["propagation"](RG58, F0_HZ)[0]).real * FEED_M)),
            color="k", ls=":", alpha=0.7, label="line-loss ceiling")
        axes[1].set_xlabel("frequency (GHz)")
        axes[1].set_ylabel("delivered / incident (dB)")
        axes[1].set_title("what 10 m of RG-58 does to your watts")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 2 not implemented")

    fig.tight_layout()
    fig.savefig("hw2_sweep.png", dpi=130)
    print("wrote hw2_sweep.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--sweep", action="store_true",
                    help="the pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.sweep:
        make_sweep()
    if not (args.check or args.sweep):
        print(__doc__)


if __name__ == "__main__":
    main()
