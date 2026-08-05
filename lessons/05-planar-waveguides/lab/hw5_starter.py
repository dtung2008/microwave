"""Homework 5 starter — Design the board, spec the pipe.

You implement the three modules marked TODO below. Everything else is the
toolkit: the stackup, the waveguide catalog, the loss formulas, the referees,
and the checker.

Run from this directory:

    python hw5_starter.py --check    # measured facts per module (the instrument)
    python hw5_starter.py --sweep    # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and the formula card; ANSWERS.md has the
questions (two of them must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_m` is meters, `*_hz` hertz, `*_ohm` ohms,
`*_db` decibels, `*_np_m` nepers per meter. eps_eff is dimensionless.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
from scipy.constants import c as C_M_S            # speed of light, m/s
from scipy.constants import mu_0 as MU0           # H/m

ETA0_OHM = 376.730313668                          # impedance of free space
NP_TO_DB = 8.685889638                            # 1 Np in dB (= 20*log10(e))

# ----------------------------------------------------------------------------
# The hardware (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
# The board: Rogers RO4350B, the course's X-band stackup. ep_r and tand are
# the datasheet's 10 GHz "design" values; h is the standard 20-mil core.
RO4350B = dict(name="RO4350B", ep_r=3.48, h_m=0.508e-3, tand=0.0037,
               t_m=35e-6)                          # 35 um = 1 oz copper
# The board you are NOT using this time (but priced in lecture 1's spirit).
FR4 = dict(name="FR-4", ep_r=4.4, h_m=0.508e-3, tand=0.02, t_m=35e-6)

RHO_CU_OHM_M = 1.68e-8                             # copper resistivity

# The pipes: EIA rectangular waveguides a student can actually buy.
# a_m x b_m inner dimensions; band = the vendor's recommended operating band.
WAVEGUIDES = {
    "WR-90": dict(a_m=22.86e-3, b_m=10.16e-3, band="8.2-12.4 GHz"),
    "WR-75": dict(a_m=19.05e-3, b_m=9.525e-3, band="10.0-15.0 GHz"),
    "WR-62": dict(a_m=15.7988e-3, b_m=7.8994e-3, band="12.4-18.0 GHz"),
}

F0_HZ = 10e9                # the front-end's center frequency (X-band)
WINDOW_HZ = (9.9e9, 10.1e9)  # the 200 MHz signal window around f0
RUN_M = 0.30                # the run from front-end to antenna: 30 cm
Z_ANT_OHM = 100.0           # the antenna feed impedance the lambda/4 must reach

# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def w_eff_m(w_m, sub):
    """Wheeler's thickness correction: the strip the fields actually see.

    A strip of thickness t behaves like a slightly wider zero-thickness
    strip: w_eff = w + (t/pi)*(1 + ln(2h/t)). Feed THIS width to the
    zero-thickness Hammerstad formulas."""
    return w_m + sub["t_m"] / np.pi * (1.0 + np.log(2.0 * sub["h_m"]
                                                    / sub["t_m"]))


def skrf_mline(w_m, sub, f_start_ghz=1.0, f_stop_ghz=20.0, npoints=191):
    """The microstrip referee: scikit-rf MLine (Hammerstad-Jensen quasi-static
    + Kirschning-Jansen dispersion + finite thickness + conductor/dielectric
    loss). An independent implementation with MORE physics than your hand
    model — where you two disagree is the lecture's dispersion story.

    Read z0_characteristic (ohms), ep_reff_f (effective permittivity vs f),
    alpha_conductor / alpha_dielectric (Np/m) off the returned object."""
    import skrf
    from skrf.media import MLine
    freq = skrf.Frequency(f_start_ghz, f_stop_ghz, npoints, "ghz")
    return MLine(frequency=freq, w=w_m, h=sub["h_m"], t=sub["t_m"],
                 ep_r=sub["ep_r"], tand=sub["tand"], rho=RHO_CU_OHM_M,
                 model="hammerstadjensen", disp="kirschningjansen",
                 f_epr_tand=F0_HZ)


def skrf_waveguide(name, f_start_ghz, f_stop_ghz, npoints=201):
    """The waveguide referee: scikit-rf RectangularWaveguide (TE10).

    Read f_cutoff (Hz), beta (rad/m), v_g (m/s), alpha (Np/m) off it."""
    import skrf
    from skrf.media import RectangularWaveguide
    g = WAVEGUIDES[name]
    freq = skrf.Frequency(f_start_ghz, f_stop_ghz, npoints, "ghz")
    return RectangularWaveguide(frequency=freq, a=g["a_m"], b=g["b_m"],
                                rho=RHO_CU_OHM_M)


# --- loss formulas (provided: module 3 assembles, it does not derive) --------
def rs_ohm(f_hz):
    """Surface resistance of copper: Rs = sqrt(pi*f*mu0*rho)."""
    return np.sqrt(np.pi * np.asarray(f_hz, dtype=float) * MU0 * RHO_CU_OHM_M)


def ms_alpha_c_np_m(f_hz, w_m, z0_ohm):
    """Microstrip conductor loss (Pozar 3.199, the classroom estimate):
    alpha_c = Rs / (Z0 * w), in Np/m."""
    return rs_ohm(f_hz) / (z0_ohm * w_m)


def ms_alpha_d_np_m(f_hz, eps_eff, sub):
    """Microstrip dielectric loss (Pozar 3.198): the substrate's tand,
    weighted by the filling factor, in Np/m."""
    k0 = 2.0 * np.pi * np.asarray(f_hz, dtype=float) / C_M_S
    er = sub["ep_r"]
    return (k0 * er * (eps_eff - 1.0) * sub["tand"]
            / (2.0 * np.sqrt(eps_eff) * (er - 1.0)))


def wg_alpha_c_np_m(f_hz, a_m, b_m):
    """TE10 rectangular-waveguide wall loss (Pozar 3.96), copper, in Np/m."""
    f = np.asarray(f_hz, dtype=float)
    k = 2.0 * np.pi * f / C_M_S
    beta = np.sqrt(k**2 - (np.pi / a_m) ** 2)
    return (rs_ohm(f) / (a_m**3 * b_m * beta * k * ETA0_OHM)
            * (2.0 * b_m * np.pi**2 + a_m**3 * k**2))


# --- reference inputs (instructor-measured, so a broken module 1 never -------
# --- hides module 3; your own module-1 numbers should land within ~1%) -------
REF_W50_M = 1.1131e-3       # 50-ohm width on RO4350B from the reference solution
REF_EPS_EFF_50 = 2.7361     # its quasi-static eps_eff
REF_FR4_W50_M = 0.9302e-3   # same two numbers on FR-4 (the shootout's foil)
REF_FR4_EPS_EFF_50 = 3.3323


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def ms_eps_eff(w_m, sub):
    """Module 1 — quasi-static effective permittivity of a microstrip of
    width w_m on substrate `sub` (a dict like RO4350B).

    Hammerstad's formula (the formula card in HOMEWORK.md), applied to the
    thickness-corrected width `w_eff_m(w_m, sub)`. Must land between
    (ep_r+1)/2 and ep_r — half the field is in air, and the formula is the
    bookkeeping for exactly how much."""
    raise NotImplementedError


def ms_z0(w_m, sub):
    """Module 1 — characteristic impedance (ohms) of the same microstrip,
    quasi-static Hammerstad (both w/h regimes), thickness-corrected width.
    The referee is skrf MLine: the syllabus bar is 2% across 1-20 GHz."""
    raise NotImplementedError


def ms_width_for(z0_ohm, sub):
    """Module 1 — synthesis: the width (m) at which YOUR ms_z0 reports
    z0_ohm. Closed-form Hammerstad synthesis (formula card) or a numeric
    root on your own analysis — your choice; the checker only measures the
    result. Used for 50 ohm and for the transformer's 70.71 ohm."""
    raise NotImplementedError


def quarter_wave(z_line_ohm, f_hz, sub):
    """Module 1 — the physical quarter-wave section: return (w_m, length_m)
    of a lambda_g/4 line of impedance z_line_ohm at f_hz on `sub`.

    The length is a quarter of the GUIDED wavelength — the wavelength the
    wave actually has on this line, not in vacuum and not in bulk dielectric.
    (Hour 3's deliberate bug lives exactly here; get the epsilon right.)"""
    raise NotImplementedError


def wg_cutoffs(a_m, b_m):
    """Module 2 — return (fc10_hz, fc_next_hz): the TE10 cutoff and the
    cutoff of the NEXT mode up (the ceiling of the single-mode band).
    General TE_mn cutoff: f_c = (c/2)*sqrt((m/a)^2 + (n/b)^2); which mode
    is next for a standard a ~ 2b guide is yours to reason out."""
    raise NotImplementedError


def wg_beta(f_hz, a_m):
    """Module 2 — TE10 phase constant beta(f) in rad/m, vectorized in f_hz.
    Only called above cutoff. The omega-beta diagram in --sweep is this
    function; so is the dispersion the group delay pays for."""
    raise NotImplementedError


def wg_group_delay_s(f_hz, a_m, length_m):
    """Module 2 — group delay (seconds) of a length_m run at each frequency
    in the array f_hz: tau = length * d(beta)/d(omega), taken NUMERICALLY
    from YOUR wg_beta (np.gradient is fine). The checker referees against
    the closed-form d(beta)/d(omega) — an independent path; syllabus bar 1%."""
    raise NotImplementedError


def loss_shootout(sub, w50_m, eps_eff50, f_hz, length_m):
    """Module 3 — the verdict table. For a `length_m` run at `f_hz`, return a
    dict of dB losses (positive numbers):

        {"ms_conductor_db": ..., "ms_dielectric_db": ..., "ms_total_db": ...,
         "wg_db": ...,           # WR-90, wall loss
         "winner": "microstrip" or "waveguide"}

    The alpha formulas are provided in the toolkit (they return Np/m — the
    Np->dB gate is NP_TO_DB, and walking through it consciously is the
    point of this module). The checker feeds instructor-measured reference
    inputs, so this module stands even if module 1 is broken."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
def _wg_tau_referee_s(f_hz, a_m, length_m):
    """Closed-form TE10 group delay: tau = L / (c*sqrt(1-(fc/f)^2)).
    This is d(beta)/d(omega) done on paper — the analytic referee your
    numerical gradient is measured against."""
    f = np.asarray(f_hz, dtype=float)
    fc = C_M_S / (2.0 * a_m)
    return length_m / (C_M_S * np.sqrt(1.0 - (fc / f) ** 2))


def _mods_default():
    return dict(ms_eps_eff=ms_eps_eff, ms_z0=ms_z0, ms_width_for=ms_width_for,
                quarter_wave=quarter_wave, wg_cutoffs=wg_cutoffs,
                wg_beta=wg_beta, wg_group_delay_s=wg_group_delay_s,
                loss_shootout=loss_shootout)


def run_checks(mods=None):
    m = mods or _mods_default()
    print("=" * 64)
    print("hw5 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: Hammerstad synthesis --------------------------------------
    print("\n[module 1] ms_eps_eff / ms_z0 / ms_width_for / quarter_wave")
    try:
        w50 = float(m["ms_width_for"](50.0, RO4350B))
        z_own = float(m["ms_z0"](w50, RO4350B))
        ee = float(m["ms_eps_eff"](w50, RO4350B))
        print(f"  50-ohm width on RO4350B: w = {w50*1e3:.4f} mm "
              f"(your ms_z0 there: {z_own:.4f} ohm)")
        ml = skrf_mline(w50, RO4350B)
        z_sk = ml.z0_characteristic.real
        e_sk = ml.ep_reff_f.real
        i10 = np.argmin(np.abs(ml.frequency.f - F0_HZ))
        dz = np.abs(z_own - z_sk) / z_sk * 100.0
        de = np.abs(ee - e_sk) / e_sk * 100.0
        print(f"  vs skrf MLine at 10 GHz: z0 = {z_sk[i10]:.4f} ohm "
              f"(d = {dz[i10]:.2f}%), eps_eff = {e_sk[i10]:.4f} "
              f"(d = {de[i10]:.2f}%)")
        print(f"  across 1-20 GHz: worst z0 d = {dz.max():.2f}% "
              f"(bar 2%), worst eps_eff d = {de.max():.2f}% (bar 3%)")
        print(f"  your quasi-static eps_eff = {ee:.4f} "
              f"(floor (er+1)/2 = {(RO4350B['ep_r']+1)/2:.3f}, "
              f"ceiling er = {RO4350B['ep_r']:.2f})")
        lam_g = C_M_S / (F0_HZ * np.sqrt(ee))
        print(f"  guided wavelength at 10 GHz: lam_g = {lam_g*1e3:.4f} mm "
              f"(free space 29.9792, in bulk er {C_M_S/(F0_HZ*np.sqrt(RO4350B['ep_r']))*1e3:.4f})")
        zt = np.sqrt(50.0 * Z_ANT_OHM)
        wt, lt = m["quarter_wave"](zt, F0_HZ, RO4350B)
        wtf, ltf = m["quarter_wave"](zt, F0_HZ, FR4)
        print(f"  lambda/4 transformer to {Z_ANT_OHM:.0f} ohm "
              f"(Z_T = {zt:.2f} ohm):")
        print(f"    RO4350B: w = {float(wt)*1e3:.4f} mm, "
              f"L = {float(lt)*1e3:.4f} mm")
        print(f"    FR-4   : w = {float(wtf)*1e3:.4f} mm, "
              f"L = {float(ltf)*1e3:.4f} mm   "
              f"(RO4350B/FR-4 length ratio = {float(lt)/float(ltf):.4f})")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the waveguide picker --------------------------------------
    print("\n[module 2] wg_cutoffs / wg_beta / wg_group_delay_s")
    try:
        fwin = np.linspace(WINDOW_HZ[0], WINDOW_HZ[1], 201)
        for name, g in WAVEGUIDES.items():
            fc10, fc_next = m["wg_cutoffs"](g["a_m"], g["b_m"])
            fc_ref = C_M_S / (2.0 * g["a_m"])
            single = fc10 < F0_HZ < fc_next
            tag = (f"single-mode at 10 GHz, f0/fc = {F0_HZ/fc10:.3f}"
                   if single else "10 GHz is BELOW cutoff")
            print(f"  {name}: fc(TE10) = {fc10/1e9:.6f} GHz "
                  f"(c/2a = {fc_ref/1e9:.6f}, d = {abs(fc10-fc_ref):.3e} Hz), "
                  f"next mode {fc_next/1e9:.6f} GHz")
            print(f"        vendor band {g['band']}; {tag}")
            if fc10 < WINDOW_HZ[0]:
                tau = np.asarray(m["wg_group_delay_s"](fwin, g["a_m"], RUN_M),
                                 dtype=float)
                tau_ref = _wg_tau_referee_s(fwin, g["a_m"], RUN_M)
                i0 = np.argmin(np.abs(fwin - F0_HZ))
                derr = np.abs(tau - tau_ref) / tau_ref * 100.0
                spread = (tau.max() - tau.min()) * 1e12
                print(f"        30 cm group delay at 10 GHz = "
                      f"{tau[i0]*1e9:.4f} ns (free space "
                      f"{RUN_M/C_M_S*1e9:.4f} ns); vs analytic d(beta)/d(omega): "
                      f"worst d = {derr.max():.3f}% (bar 1%)")
                print(f"        delay spread across the 200 MHz window = "
                      f"{spread:.1f} ps")
        # skrf cross-check on the picker's winner. API note: skrf's v_g is
        # d(omega)/d(gamma) and gamma = alpha + j*beta, so the physical group
        # SPEED is |v_g| (the number lands in the imaginary part).
        wg = skrf_waveguide("WR-90", 9.9, 10.1, 201)
        vg = np.abs(wg.v_g)
        tau_sk = RUN_M / vg
        tau_own = np.asarray(m["wg_group_delay_s"](wg.frequency.f, 22.86e-3,
                                                   RUN_M), dtype=float)
        print(f"  WR-90 vs skrf |v_g| referee: worst d = "
              f"{(np.abs(tau_own-tau_sk)/tau_sk).max()*100:.3f}%")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the loss shootout -----------------------------------------
    print("\n[module 3] loss_shootout (reference inputs: instructor-measured)")
    try:
        r = m["loss_shootout"](RO4350B, REF_W50_M, REF_EPS_EFF_50, F0_HZ,
                               RUN_M)
        print(f"  30 cm at 10 GHz, RO4350B microstrip: conductor "
              f"{r['ms_conductor_db']:.3f} dB + dielectric "
              f"{r['ms_dielectric_db']:.3f} dB = {r['ms_total_db']:.3f} dB")
        print(f"  30 cm at 10 GHz, WR-90 waveguide:    {r['wg_db']:.4f} dB")
        print(f"  winner: {r['winner']} "
              f"(ratio {r['ms_total_db']/max(r['wg_db'],1e-12):.1f}x in dB terms)")
        ml = skrf_mline(REF_W50_M, RO4350B, 10.0, 10.0, 1)
        ac = float(ml.alpha_conductor[0]) * NP_TO_DB
        ad = float(ml.alpha_dielectric[0]) * NP_TO_DB
        wg = skrf_waveguide("WR-90", 10.0, 10.0, 1)
        aw = float(wg.alpha[0].real) * NP_TO_DB
        print(f"  skrf referee (dB/m): MLine conductor {ac:.3f} + dielectric "
              f"{ad:.3f}; RectangularWaveguide {aw:.4f}")
        rf4 = m["loss_shootout"](FR4, REF_FR4_W50_M, REF_FR4_EPS_EFF_50,
                                 F0_HZ, RUN_M)
        print(f"  same run on FR-4: {rf4['ms_total_db']:.2f} dB "
              f"(dielectric alone {rf4['ms_dielectric_db']:.2f} dB) — "
              f"the lecture's 40%-in-the-substrate war story, priced")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_sweep(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or _mods_default()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    # --- picture 1: the quasi-static lie, measured (Q5's picture) -----------
    try:
        w50 = float(m["ms_width_for"](50.0, RO4350B))
        ml = skrf_mline(w50, RO4350B)
        f_ghz = ml.frequency.f / 1e9
        ax = axes[0]
        ax.plot(f_ghz, ml.ep_reff_f.real, label="skrf MLine (dispersive)")
        ee = float(m["ms_eps_eff"](w50, RO4350B))
        ax.axhline(ee, color="C1", ls="--",
                   label=f"hand quasi-static ({ee:.3f})")
        ax.set_xlabel("frequency (GHz)")
        ax.set_ylabel(r"$\epsilon_{\rm eff}$")
        ax.set_title("microstrip dispersion: where the\nquasi-static story bends")
        ax2 = ax.twinx()
        ax2.plot(f_ghz, ml.z0_characteristic.real, color="C2", alpha=0.6)
        ax2.axhline(float(m["ms_z0"](w50, RO4350B)), color="C3", ls=":",
                    alpha=0.8)
        ax2.set_ylabel(r"$Z_0$ ($\Omega$)  (green: skrf, dotted: hand)")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 1 not implemented")

    # --- picture 2: the omega-beta diagram (Q2's picture) -------------------
    try:
        ax = axes[1]
        f = np.linspace(5e9, 20e9, 800)
        for name, g in WAVEGUIDES.items():
            fc10, _ = m["wg_cutoffs"](g["a_m"], g["b_m"])
            fs = f[f > fc10 * 1.001]
            beta = np.asarray(m["wg_beta"](fs, g["a_m"]), dtype=float)
            ax.plot(beta, fs / 1e9, label=f"{name} (fc {fc10/1e9:.2f} GHz)")
        blight = 2.0 * np.pi * f / C_M_S
        ax.plot(blight, f / 1e9, "k--", alpha=0.5, label="light line (TEM)")
        ax.axhline(10.0, color="gray", ls=":", alpha=0.7)
        ax.annotate("10 GHz", (30, 10.15), fontsize=9, color="gray")
        ax.set_xlabel(r"$\beta$ (rad/m)")
        ax.set_ylabel("frequency (GHz)")
        ax.set_title("the omega-beta diagram:\nflat slope near cutoff = slow energy")
        ax.set_xlim(0, blight.max())
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 2 not implemented")

    fig.tight_layout()
    fig.savefig("hw5_sweep.png", dpi=130)
    print("wrote hw5_sweep.png")
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
        make_sweep()
    if not (args.check or args.sweep):
        print(__doc__)


if __name__ == "__main__":
    main()
