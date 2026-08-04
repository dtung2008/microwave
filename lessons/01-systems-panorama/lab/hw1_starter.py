"""Homework 1 starter — Can this radar see the drone?

You implement the three modules marked TODO below. Everything else is the
toolkit: system specs, the linear-watts referee, plotting, and the checker.

Run from this directory:

    python hw1_starter.py --check    # measured facts per module (the instrument)
    python hw1_starter.py --plot     # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbm` / `*_dbi` are decibel quantities;
`*_w` is watts; `*_hz`, `*_m`, `*_m2` are SI. Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s
from scipy.constants import k as K_BOLTZ        # Boltzmann constant, J/K

T0_K = 290.0                                    # IEEE noise reference temperature

# ----------------------------------------------------------------------------
# The systems (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
# A WiFi-class point-to-point link (module 1's test article).
WIFI_LINK = dict(
    f_hz=2.4e9,        # carrier frequency
    p_t_dbm=20.0,      # transmit power (100 mW)
    g_t_dbi=6.0,       # transmit antenna gain
    g_r_dbi=2.0,       # receive antenna gain
    b_hz=20e6,         # receiver noise bandwidth
    nf_db=7.0,         # receiver noise figure
)

# The course radar — a compact X-band perimeter-surveillance set. It returns
# in lectures 10 (its receive chain), 13 (its antenna), 14-16 (its mission).
COURSE_RADAR = dict(
    f_hz=10e9,         # X-band
    p_t_w=10e3,        # transmit power, watts (10 kW)
    g_dbi=33.0,        # antenna gain, same dish for TX and RX (monostatic)
    b_hz=1e6,          # receiver noise bandwidth
    nf_db=3.0,         # receiver noise figure
    loss_db=6.0,       # total system losses (plumbing, processing, weather)
    snr_req_db=13.0,   # SNR required to call a detection (honest version: L14)
)

# The three customers of lecture 1's story (radar cross sections).
TARGETS = {
    "airliner": 40.0,      # m^2  -- a 747-class body, broadside-ish
    "fighter":   1.0,      # m^2  -- clean supersonic airframe
    "drone":     0.01,     # m^2  -- small quadcopter, plastic + battery
}


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def wavelength_m(f_hz):
    """Free-space wavelength lambda = c / f."""
    return C_M_S / np.asarray(f_hz, dtype=float)


def noise_floor_w(b_hz, nf_db):
    """Receiver noise power k*T0*B*F in WATTS (linear F = 10^(NF/10))."""
    return K_BOLTZ * T0_K * np.asarray(b_hz, dtype=float) * 10.0 ** (nf_db / 10.0)


def ratio(x_db):
    """dB -> linear power ratio (toolkit's own; your undb is module 1)."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def db(x_lin):
    """Module 1 (warm-up) — linear power ratio -> decibels. Vectorized."""
    raise NotImplementedError


def undb(x_db):
    """Module 1 (warm-up) — decibels -> linear power ratio. Vectorized."""
    raise NotImplementedError


def fspl_db(f_hz, r_m):
    """Module 1 — free-space path loss (dB, positive number) between two
    isotropic antennas at frequency f_hz separated by r_m. Vectorized in
    r_m. Hour 1 derived it; hour 3 printed 92.45 dB at (1 GHz, 1 km)."""
    raise NotImplementedError


def link_budget(link, r_m):
    """Module 1 — one-way link budget, entirely in dB.

    `link` is a dict like WIFI_LINK. Return (p_r_dbm, snr_db) at range r_m:
    received power at the antenna terminals, and SNR against the receiver's
    noise floor k*T0*B raised by its noise figure. Vectorized in r_m.
    """
    raise NotImplementedError


def radar_snr_db(radar, sigma_m2, r_m):
    """Module 2 (the core) — monostatic radar equation, forward direction.

    `radar` is a dict like COURSE_RADAR. Return the single-pulse SNR (dB) on
    a target of RCS sigma_m2 at range r_m, including the radar's system
    losses. Vectorized in r_m. Work in dB; the checker's referee works in
    watts — if you ever mix the two, the disagreement will be loud.
    """
    raise NotImplementedError


def radar_max_range_m(radar, sigma_m2):
    """Module 2 (the core) — the inverse question: the maximum range (m) at
    which the radar still achieves its required SNR (radar['snr_req_db'])
    on a target of RCS sigma_m2. Closed form, not a numeric search: invert
    the radar equation by hand first."""
    raise NotImplementedError


def target_study(radar, targets):
    """Module 3 — the three-customer study. For each name in `targets`
    (dict: name -> RCS in m^2), compute the maximum detection range with
    YOUR radar_max_range_m. Return a dict name -> range in meters."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# The referee below never touches a decibel: it walks the physics in watts
# and square meters (spreading -> intercept -> re-radiation -> aperture).
# Your dB-domain modules and this linear chain are two independent
# implementations; if they disagree, one of you mixed units.
# ----------------------------------------------------------------------------
def _friis_watts_referee(link, r_m):
    """One-way received power (W) and SNR (linear), no dB anywhere."""
    r = np.asarray(r_m, dtype=float)
    lam = wavelength_m(link["f_hz"])
    p_t_w = 1e-3 * ratio(link["p_t_dbm"])            # dBm -> W (the one gate)
    g_t = ratio(link["g_t_dbi"])
    g_r = ratio(link["g_r_dbi"])
    density_w_m2 = p_t_w * g_t / (4.0 * np.pi * r**2)     # spreading
    a_eff_m2 = g_r * lam**2 / (4.0 * np.pi)               # receive aperture
    p_r_w = density_w_m2 * a_eff_m2
    snr = p_r_w / noise_floor_w(link["b_hz"], link["nf_db"])
    return p_r_w, snr


def _radar_watts_referee(radar, sigma_m2, r_m):
    """Monostatic single-pulse SNR (linear), no dB anywhere."""
    r = np.asarray(r_m, dtype=float)
    lam = wavelength_m(radar["f_hz"])
    g = ratio(radar["g_dbi"])
    density_w_m2 = radar["p_t_w"] * g / (4.0 * np.pi * r**2)   # at the target
    p_scat_w = density_w_m2 * sigma_m2                         # RCS intercept
    density_back_w_m2 = p_scat_w / (4.0 * np.pi * r**2)        # return trip
    a_eff_m2 = g * lam**2 / (4.0 * np.pi)                      # same dish
    p_r_w = density_back_w_m2 * a_eff_m2
    p_r_w = p_r_w / ratio(radar["loss_db"])                    # system losses
    return p_r_w / noise_floor_w(radar["b_hz"], radar["nf_db"])


def _fmt_m(r_m):
    return f"{r_m/1e3:8.2f} km"


def run_checks(mods=None):
    m = mods or dict(db=db, undb=undb, fspl_db=fspl_db, link_budget=link_budget,
                     radar_snr_db=radar_snr_db,
                     radar_max_range_m=radar_max_range_m,
                     target_study=target_study)
    print("=" * 64)
    print("hw1 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: dB machinery and the one-way budget ---------------------
    print("\n[module 1] db / undb / fspl_db / link_budget")
    try:
        x = np.array([1e-9, 0.5, 1.0, 2.0, 4e6])
        rt = np.abs(m["undb"](m["db"](x)) - x) / x
        print(f"  undb(db(x)) round trip, max relative error = {rt.max():.2e}")
        print(f"  db(2) = {float(m['db'](2.0)):.4f}   (3 dB is a doubling)")
        print(f"  fspl(1 GHz, 1 km) = {float(m['fspl_db'](1e9, 1e3)):.2f} dB"
              "   (the classic 92.45)")
        for r in (50.0, 200.0, 1000.0):
            p_dbm, snr_db_ = m["link_budget"](WIFI_LINK, r)
            p_ref_w, snr_ref = _friis_watts_referee(WIFI_LINK, r)
            d_p = float(p_dbm) - (10*np.log10(p_ref_w) + 30.0)
            d_s = float(snr_db_) - 10*np.log10(snr_ref)
            print(f"  r={r:6.0f} m: P_r = {float(p_dbm):8.2f} dBm, "
                  f"SNR = {float(snr_db_):6.2f} dB   "
                  f"| vs watts referee: dP = {d_p:+.2e} dB, dSNR = {d_s:+.2e} dB")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the radar equation, forward and inverse -----------------
    print("\n[module 2] radar_snr_db / radar_max_range_m")
    try:
        for r_km in (5.0, 15.0, 40.0):
            s = float(m["radar_snr_db"](COURSE_RADAR, 1.0, r_km * 1e3))
            s_ref = 10*np.log10(_radar_watts_referee(COURSE_RADAR, 1.0, r_km*1e3))
            print(f"  sigma=1 m2, r={r_km:5.1f} km: SNR = {s:7.2f} dB"
                  f"   | vs watts referee: d = {s - s_ref:+.2e} dB")
        r1 = float(m["radar_snr_db"](COURSE_RADAR, 1.0, 10e3))
        r2 = float(m["radar_snr_db"](COURSE_RADAR, 1.0, 20e3))
        print(f"  range doubled 10 -> 20 km: SNR fell {r1 - r2:.2f} dB"
              "   (one-way link would fall 6.02)")
        rmax = float(m["radar_max_range_m"](COURSE_RADAR, 1.0))
        back = float(m["radar_snr_db"](COURSE_RADAR, 1.0, rmax))
        print(f"  round trip: R_max(sigma=1) = {_fmt_m(rmax)}; "
              f"SNR there = {back:.4f} dB (required {COURSE_RADAR['snr_req_db']})")
        rmax2 = float(m["radar_max_range_m"](COURSE_RADAR, 2.0))
        print(f"  sigma x2 -> range x{rmax2/rmax:.4f}   (2^(1/4) = {2**0.25:.4f})")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the three customers -------------------------------------
    print("\n[module 3] target_study")
    try:
        study = m["target_study"](COURSE_RADAR, TARGETS)
        for name, sig in TARGETS.items():
            print(f"  {name:8s} (sigma = {sig:6.2f} m2): "
                  f"detectable to {_fmt_m(study[name])}")
        ratio_meas = study["airliner"] / study["drone"]
        ratio_theory = (TARGETS["airliner"] / TARGETS["drone"]) ** 0.25
        print(f"  airliner/drone range ratio = {ratio_meas:.3f}"
              f"   ((sigma ratio)^(1/4) = {ratio_theory:.3f})")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(radar_snr_db=radar_snr_db,
                     radar_max_range_m=radar_max_range_m,
                     target_study=target_study)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))

    # --- picture 1: SNR vs range for the three customers (Q2's picture) ----
    try:
        r = np.linspace(1e3, 60e3, 600)
        for name, sig in TARGETS.items():
            axes[0].plot(r / 1e3, m["radar_snr_db"](COURSE_RADAR, sig, r),
                         label=f"{name} ({sig} m$^2$)")
        axes[0].axhline(COURSE_RADAR["snr_req_db"], color="k", ls=":",
                        alpha=0.7, label="required SNR")
        study = m["target_study"](COURSE_RADAR, TARGETS)
        for name in TARGETS:
            axes[0].axvline(study[name] / 1e3, color="gray", ls="--",
                            alpha=0.4)
        axes[0].set_xlabel("range (km)")
        axes[0].set_ylabel("single-pulse SNR (dB)")
        axes[0].set_title("the radar equation's verdict")
        axes[0].set_ylim(-10, 60)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 2 not implemented")

    # --- picture 2: detection range vs RCS, and the 1/4 law (Q3's picture) -
    try:
        sig = np.logspace(-3, 2, 60)
        rmax = np.array([m["radar_max_range_m"](COURSE_RADAR, s) for s in sig])
        axes[1].loglog(sig, rmax / 1e3, label="max detection range")
        guide = rmax[0] * (sig / sig[0]) ** 0.25
        axes[1].loglog(sig, guide / 1e3, "k--", alpha=0.5,
                       label=r"slope $+1/4$ guide")
        study = m["target_study"](COURSE_RADAR, TARGETS)
        for name, s in TARGETS.items():
            axes[1].plot(s, study[name] / 1e3, "o")
            axes[1].annotate(name, (s, study[name] / 1e3),
                             textcoords="offset points", xytext=(6, 4))
        axes[1].set_xlabel(r"radar cross section $\sigma$ (m$^2$)")
        axes[1].set_ylabel("max detection range (km)")
        axes[1].set_title("what stealth buys: the $\\sigma^{1/4}$ law")
        axes[1].legend()
        axes[1].grid(True, which="both", alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 2 not implemented")

    fig.tight_layout()
    fig.savefig("hw1_plots.png", dpi=130)
    print("wrote hw1_plots.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--plot", action="store_true",
                    help="the two pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.plot:
        make_plots()
    if not (args.check or args.plot):
        print(__doc__)


if __name__ == "__main__":
    main()
