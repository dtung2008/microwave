"""Homework 10 starter — The receiver budget.

You implement the three modules marked TODO below. Everything else is the
toolkit: the element catalog, the ordering generator, the lecture-1 radar
engine (carried here so your hw1 needn't be finished), the two-tone
behavioral referee, and the checker.

Run from this directory:

    python hw10_starter.py --check    # measured facts per module (the instrument)
    python hw10_starter.py --plot     # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbm` / `*_dbi` are decibel
quantities; `*_hz`, `*_m`, `*_m2`, `*_w` are SI. Noise factor F and gain G
are LINEAR inside cascade formulas — Friis 1944 does not speak dB. Never add
two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse
import itertools

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s
from scipy.constants import k as K_BOLTZ        # Boltzmann constant, J/K

T0_K = 290.0                                    # IEEE noise reference temperature

# ----------------------------------------------------------------------------
# The five blocks (instructor side — the catalog your chain is built from)
# ----------------------------------------------------------------------------
# Each element: gain (dB), noise figure (dB), input-referred IP3 (dBm).
# iip3_dbm = inf means "passive and ideally linear" (cable, filter): it adds
# loss and noise but no third-order spurs worth modeling.
# For a passive lossy element, NF = its loss (hour 1 proves this).
RX_ELEMENTS = {
    "cable": dict(name="cable", gain_db=-2.0, nf_db=2.0, iip3_dbm=np.inf),
    "lna":   dict(name="lna",   gain_db=20.0, nf_db=1.5, iip3_dbm=-5.0),
    "bpf":   dict(name="bpf",   gain_db=-1.5, nf_db=1.5, iip3_dbm=np.inf),
    "mixer": dict(name="mixer", gain_db=-7.0, nf_db=8.0, iip3_dbm=15.0),
    "ifamp": dict(name="ifamp", gain_db=30.0, nf_db=4.0, iip3_dbm=10.0),
}

# The course radar — MIRRORED VERBATIM from lecture 1's hw1_starter.py so the
# payoff module runs even if your hw1 was never finished. Same names, same
# contract. Its nf_db=3.0 is the SPEC lecture 1 assumed; this week you find
# out what the chain actually delivers.
COURSE_RADAR = dict(
    f_hz=10e9,         # X-band
    p_t_w=10e3,        # transmit power, watts (10 kW)
    g_dbi=33.0,        # antenna gain, same dish for TX and RX (monostatic)
    b_hz=1e6,          # receiver noise bandwidth
    nf_db=3.0,         # receiver noise figure (lecture 1's assumption)
    loss_db=6.0,       # total system losses (plumbing, processing, weather)
    snr_req_db=13.0,   # SNR required to call a detection (honest version: L14)
)

# The three customers of lecture 1 (radar cross sections, m^2).
TARGETS = {"airliner": 40.0, "fighter": 1.0, "drone": 0.01}

# Reference chains the checker exercises (element names, antenna first):
REF_WARMUP = ("cable", "lna")                     # two blocks, hand-workable
REF_MAST = ("lna", "cable", "bpf", "mixer", "ifamp")   # LNA on the mast
REF_OBVIOUS = ("cable", "bpf", "lna", "mixer", "ifamp")  # "filter first!" — Q4

# Instructor's hand-worked values for those chains (worked in ANSWERS-key.md;
# the two-block warm-up is EXACT: lossy-first NF = loss + next NF, and a
# lossless attenuator in front lifts IIP3 by exactly its loss).
HAND_WORKED = {
    REF_WARMUP:  dict(gain_db=18.0, nf_db=3.5000, iip3_dbm=-3.0000),
    REF_MAST:    dict(gain_db=39.5, nf_db=2.3387, iip3_dbm=-7.3767),
    REF_OBVIOUS: dict(gain_db=39.5, nf_db=5.3792, iip3_dbm=-5.7011),
}

# Module 3's design question: the customer wants the drone at this range.
SPEC_RANGE_M = 4300.0


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
    """Free-space wavelength lambda = c / f."""
    return C_M_S / np.asarray(f_hz, dtype=float)


def chain(*names):
    """Element names -> list of element dicts (what your modules consume)."""
    return [RX_ELEMENTS[n] for n in names]


def sensible_orderings():
    """All orderings of the five blocks that respect the frequency plan:
    the BPF is an RF (radio frequency) filter, so it must sit before the
    mixer; the IF (intermediate frequency) amplifier only works after the
    mixer. Cable and LNA may go anywhere — that is the design freedom this
    homework prices. Returns 20 tuples of names, antenna first."""
    out = []
    for p in itertools.permutations(RX_ELEMENTS):
        if p.index("bpf") < p.index("mixer") < p.index("ifamp"):
            out.append(p)
    return out


def radar_max_range_m(radar, sigma_m2):
    """Lecture 1's radar engine — the closed-form maximum detection range (m)
    at the radar's required SNR. Verbatim-equivalent of hw1's solution
    (same name, same contract), carried by the toolkit so module 3 works
    whether or not your hw1 is finished."""
    lam = wavelength_m(radar["f_hz"])
    num = radar["p_t_w"] * undb(2.0 * radar["g_dbi"]) * lam**2 * sigma_m2
    den = ((4.0 * np.pi) ** 3 * K_BOLTZ * T0_K * radar["b_hz"]
           * undb(radar["nf_db"]) * undb(radar["loss_db"])
           * undb(radar["snr_req_db"]))
    return float((num / den) ** 0.25)


def two_tone_iip3_dbm(iip3_dbm, p_in_dbm=(-45.0, -40.0, -35.0)):
    """The behavioral referee: build an actual y = x + a3*x^3 nonlinearity
    whose analytic IIP3 is `iip3_dbm`, drive it with two equal tones at each
    input level, FFT, read the IM3 (third-order intermodulation) spurs at
    2f1-f2, and return (spur_slope, iip3_extrapolated_dbm).

    If your cascade IIP3 is a real physical number, feeding it here and
    extrapolating the measured spurs must hand it back. Deterministic —
    pure signals, no noise, tones on exact FFT bins.
    Convention: dBm across 50 ohms; amplitude A has power A^2/100 W.
    """
    fs_hz, n = 40.96e6, 4096                    # 10 kHz bins, exact
    f1_hz, f2_hz = 5.00e6, 5.10e6               # bins 500 and 510
    t = np.arange(n) / fs_hz
    a_ip3_sq = 0.1 * undb(iip3_dbm)             # V^2: A^2 = 2*50*P  (P in W)
    a3 = -4.0 / (3.0 * a_ip3_sq)                # compressive cubic
    p_fund, p_im3 = [], []
    for p_dbm in p_in_dbm:
        a = np.sqrt(0.1 * undb(p_dbm))          # per-tone amplitude, volts
        x = a * np.cos(2 * np.pi * f1_hz * t) + a * np.cos(2 * np.pi * f2_hz * t)
        y = x + a3 * x**3
        spec = np.abs(np.fft.rfft(y)) * 2.0 / n     # bin -> amplitude
        p_fund.append(float(db(spec[500] ** 2 / 0.1)))
        p_im3.append(float(db(spec[490] ** 2 / 0.1)))   # 2f1 - f2 = 4.9 MHz
    slope = np.polyfit(p_in_dbm, p_im3, 1)[0]
    iip3_meas = p_in_dbm[0] + (p_fund[0] - p_im3[0]) / 2.0
    return float(slope), float(iip3_meas)


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def cascade_gain_db(elements):
    """Module 1 (warm-up) — total gain (dB) of a chain of element dicts
    (each has 'gain_db'), antenna first. The one cascade that IS legal in
    dB — and the checker shows it doesn't care about order."""
    raise NotImplementedError


def cascade_nf_db(elements):
    """Module 1 (the core) — system noise figure (dB) of the chain, via
    Friis's 1944 cascade formula. Hand-roll it; convert to LINEAR noise
    factors and gains first — Friis does not speak dB (hour 3's deliberate
    bug is what happens if you forget)."""
    raise NotImplementedError


def cascade_iip3_dbm(elements):
    """Module 1 (the core) — system input-referred IP3 (third-order
    intercept, dBm) of the chain, via hour 2's cascade formula. Linear
    inside, like Friis: reciprocals of watts (or mW), never dB. Elements
    with iip3_dbm = inf contribute nothing (1/inf = 0)."""
    raise NotImplementedError


def mds_dbm(nf_db, b_hz):
    """Module 2 — minimum detectable signal: the input power (dBm) at which
    the signal just equals the receiver's noise floor k*T0*b_hz raised by
    nf_db (SNR = 0 dB convention). Vectorized in b_hz."""
    raise NotImplementedError


def sfdr_db(iip3_dbm, nf_db, b_hz):
    """Module 2 — spur-free dynamic range (dB) in bandwidth b_hz, from the
    system's input-referred IP3 and noise figure. Hour 2 derived it: the
    2/3 is not folklore, it falls out of the 3:1 spur slope."""
    raise NotImplementedError


def shootout(orderings):
    """Module 2 — evaluate every ordering (list of name-tuples) with your
    module-1 engine at the course radar's bandwidth. Return a list of dicts,
    one per ordering, each carrying at least:
        names, gain_db, nf_db, iip3_dbm, mds_dbm, sfdr_db
    The harness sorts and prints; your job is honest numbers per chain."""
    raise NotImplementedError


def range_payoff(nf_best_db, nf_worst_db):
    """Module 3 — the lecture-1 payoff. Feed each noise figure into the
    course radar (toolkit: radar_max_range_m + COURSE_RADAR — swap only
    nf_db) and return a dict:
        r_best_m, r_worst_m, ratio     (drone target, sigma = 0.01 m^2)
    for the best and worst chains' NF."""
    raise NotImplementedError


def nf_required_db(radar, sigma_m2, r_m):
    """Module 3 (the design question) — invert the radar equation for the
    noise figure: the LARGEST nf_db for which radar_max_range_m still
    reaches r_m on a target of sigma_m2. Closed form, not a search — start
    from lecture 1's R_max expression and solve for F by hand."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Referees: hand-worked reference chains (0.01 dB NF / 0.1 dB IIP3 is the
# course criterion); Friis limit cases — a single stage IS the system, a
# lossy first element adds EXACTLY its loss in dB, a huge first gain makes
# later stages vanish; the two-tone FFT, which hands your cascade IIP3 back
# through actual measured spurs; and the closed-form 10^(dNF/40) range law.
# ----------------------------------------------------------------------------
def _fmt_chain(names):
    return ">".join(names)


def run_checks(mods=None):
    m = mods or dict(cascade_gain_db=cascade_gain_db,
                     cascade_nf_db=cascade_nf_db,
                     cascade_iip3_dbm=cascade_iip3_dbm,
                     mds_dbm=mds_dbm, sfdr_db=sfdr_db, shootout=shootout,
                     range_payoff=range_payoff, nf_required_db=nf_required_db)
    print("=" * 72)
    print("hw10 --check : measured facts (instrument, not grade)")
    print("=" * 72)

    b_hz = COURSE_RADAR["b_hz"]
    records = None   # module 2's output, reused by module 3 if it exists

    # --- module 1: the cascade engine --------------------------------------
    print("\n[module 1] cascade_gain_db / cascade_nf_db / cascade_iip3_dbm")
    try:
        # single stage: the chain IS the element
        nf1 = float(m["cascade_nf_db"](chain("lna")))
        ip1 = float(m["cascade_iip3_dbm"](chain("lna")))
        print(f"  single LNA: NF = {nf1:.4f} dB (element says 1.5000), "
              f"IIP3 = {ip1:.4f} dBm (element says -5.0000)")
        # hand-worked chains
        for names in (REF_WARMUP, REF_MAST, REF_OBVIOUS):
            hw = HAND_WORKED[names]
            g = float(m["cascade_gain_db"](chain(*names)))
            nf = float(m["cascade_nf_db"](chain(*names)))
            ip = float(m["cascade_iip3_dbm"](chain(*names)))
            print(f"  {_fmt_chain(names):28s} G = {g:5.2f} dB | "
                  f"NF = {nf:7.4f} (hand {hw['nf_db']:7.4f}, "
                  f"d = {nf - hw['nf_db']:+.4f}) | "
                  f"IIP3 = {ip:8.4f} (hand {hw['iip3_dbm']:8.4f}, "
                  f"d = {ip - hw['iip3_dbm']:+.4f})")
        # Friis limit cases
        rest = ("lna", "bpf", "mixer", "ifamp")
        d_att = (float(m["cascade_nf_db"](chain("cable", *rest)))
                 - float(m["cascade_nf_db"](chain(*rest))))
        print(f"  lossy-first invariant: cable in front adds {d_att:.4f} dB "
              f"of NF (its loss is exactly 2.0000)")
        big = dict(name="big", gain_db=40.0, nf_db=1.5, iip3_dbm=np.inf)
        d_dom = float(m["cascade_nf_db"]([big, RX_ELEMENTS["mixer"],
                                          RX_ELEMENTS["ifamp"]])) - 1.5
        print(f"  first-stage dominance: 40 dB first stage -> later stages "
              f"add only {d_dom:.4f} dB")
        # the two-tone referee hands the cascade IIP3 back through real spurs
        ip_mast = float(m["cascade_iip3_dbm"](chain(*REF_MAST)))
        slope, ip_meas = two_tone_iip3_dbm(ip_mast)
        print(f"  two-tone referee on your mast-chain IIP3 ({ip_mast:.4f} dBm):"
              f"\n    spur slope = {slope:.4f} (algebra says 3), extrapolated "
              f"IIP3 = {ip_meas:.4f} dBm (d = {ip_meas - ip_mast:+.4f})")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the shootout --------------------------------------------
    print(f"\n[module 2] mds_dbm / sfdr_db / shootout   (B = {b_hz:.0e} Hz)")
    try:
        # reference inputs first, so a broken module 1 can't hide module 2
        md = float(m["mds_dbm"](3.0, 1e6))
        sf = float(m["sfdr_db"](-7.3767, 2.3387, 1e6))
        print(f"  mds(NF=3, B=1 MHz) = {md:.4f} dBm   (hand: -110.9752)")
        print(f"  sfdr(IIP3=-7.3767, NF=2.3387, 1 MHz) = {sf:.4f} dB   "
              f"(hand: 69.5065)")
        records = m["shootout"](sensible_orderings())
        gains = [r["gain_db"] for r in records]
        print(f"  {len(records)} sensible orderings; gain spread "
              f"max-min = {max(gains) - min(gains):.2e} dB (gain commutes)")
        by_sens = sorted(records, key=lambda r: r["mds_dbm"])
        by_sfdr = sorted(records, key=lambda r: -r["sfdr_db"])
        print("  ranked by sensitivity (best MDS first):")
        for i, r in enumerate(by_sens):
            tag = ""
            if r["names"] == REF_OBVIOUS:
                tag = "   <- the 'obvious' one (Q4)"
            if i < 4 or i >= len(by_sens) - 2 or tag:
                print(f"   {i+1:2d}. {_fmt_chain(r['names']):28s} "
                      f"NF {r['nf_db']:7.4f}  IIP3 {r['iip3_dbm']:8.4f}  "
                      f"MDS {r['mds_dbm']:9.4f}  SFDR {r['sfdr_db']:7.4f}{tag}")
            elif i == 4:
                print("     ...")
        print(f"  best by SFDR: {_fmt_chain(by_sfdr[0]['names'])} "
              f"({by_sfdr[0]['sfdr_db']:.4f} dB) — same chain as best MDS? "
              f"{by_sfdr[0]['names'] == by_sens[0]['names']}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: sensitivity and the payoff ------------------------------
    print("\n[module 3] range_payoff / nf_required_db")
    try:
        # reference NFs (instructor's best/worst) so module 2 can't hide it
        pay = m["range_payoff"](2.0378, 14.9267)
        closed = 10.0 ** ((14.9267 - 2.0378) / 40.0)
        print(f"  drone with best chain (NF 2.0378):  "
              f"{pay['r_best_m']/1e3:7.3f} km")
        print(f"  drone with worst chain (NF 14.9267): "
              f"{pay['r_worst_m']/1e3:7.3f} km")
        print(f"  ratio = {pay['ratio']:.4f}   "
              f"(closed form 10^(dNF/40) = {closed:.4f}; "
              f"lecture-1 spec NF 3.0 gave 4.106 km)")
        if records is not None:
            by_sens = sorted(records, key=lambda r: r["mds_dbm"])
            own = m["range_payoff"](by_sens[0]["nf_db"], by_sens[-1]["nf_db"])
            print(f"  with YOUR shootout's best/worst NF: "
                  f"{own['r_best_m']/1e3:.3f} km vs {own['r_worst_m']/1e3:.3f}"
                  f" km  (x{own['ratio']:.4f})")
        nf_req = float(m["nf_required_db"](COURSE_RADAR, TARGETS["drone"],
                                           SPEC_RANGE_M))
        rt = radar_max_range_m(dict(COURSE_RADAR, nf_db=nf_req),
                               TARGETS["drone"])
        print(f"  customer spec: drone at {SPEC_RANGE_M/1e3:.1f} km needs "
              f"NF <= {nf_req:.4f} dB (round trip through the radar engine: "
              f"{rt/1e3:.4f} km)")
        if records is not None:
            n_ok = sum(1 for r in records if r["nf_db"] <= nf_req)
            print(f"  chains that clear that spec: {n_ok} of {len(records)}")
        # MDS vs bandwidth, the resolution-vs-sensitivity ledger (Q5)
        bs = np.array([1e3, 1e4, 1e5, 1e6, 1e7, 1e8])
        mm = np.atleast_1d(m["mds_dbm"](2.0378, bs))
        row = "  MDS(best chain) vs B: " + "  ".join(
            f"{b:8.0e}Hz {v:8.2f}" for b, v in zip(bs, mm))
        print(row + "  dBm")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(cascade_nf_db=cascade_nf_db,
                     cascade_iip3_dbm=cascade_iip3_dbm,
                     mds_dbm=mds_dbm, sfdr_db=sfdr_db, shootout=shootout)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # --- picture 1: the shootout map (Q3's picture) ------------------------
    try:
        records = m["shootout"](sensible_orderings())
        for r in records:
            axes[0].plot(r["mds_dbm"], r["sfdr_db"], "o", color="#0f62fe",
                         alpha=0.55)
        by_sens = sorted(records, key=lambda r: r["mds_dbm"])
        for r, label, dy in ((by_sens[0], "best MDS", 8),
                             (by_sens[-1], "worst MDS", -12)):
            axes[0].annotate(f"{label}\n{_fmt_chain(r['names'])}",
                             (r["mds_dbm"], r["sfdr_db"]), fontsize=7,
                             textcoords="offset points", xytext=(6, dy))
        obv = next(r for r in records if r["names"] == REF_OBVIOUS)
        axes[0].plot(obv["mds_dbm"], obv["sfdr_db"], "s", color="#b3261e")
        axes[0].annotate("the 'obvious' chain", (obv["mds_dbm"],
                         obv["sfdr_db"]), fontsize=7, color="#b3261e",
                         textcoords="offset points", xytext=(6, -14))
        axes[0].set_xlabel("MDS (dBm) — sensitivity, left is better")
        axes[0].set_ylabel("SFDR (dB) — up is better")
        axes[0].set_title("20 orderings, two verdicts")
        axes[0].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 2 not implemented")

    # --- picture 2: the SFDR picture for the mast chain (Q2's picture) -----
    try:
        nf = float(m["cascade_nf_db"](chain(*REF_MAST)))
        ip3 = float(m["cascade_iip3_dbm"](chain(*REF_MAST)))
        md = float(m["mds_dbm"](nf, COURSE_RADAR["b_hz"]))
        sf = float(m["sfdr_db"](ip3, nf, COURSE_RADAR["b_hz"]))
        p_in = np.linspace(-120, 10, 300)
        axes[1].plot(p_in, p_in, label="fundamental (slope 1)")
        axes[1].plot(p_in, 3 * p_in - 2 * ip3, label="IM3 spurs (slope 3)")
        axes[1].axhline(md, color="k", ls=":", alpha=0.7,
                        label=f"noise floor (MDS = {md:.1f} dBm)")
        axes[1].plot(ip3, ip3, "k*", ms=12,
                     label=f"IIP3 = {ip3:.1f} dBm (fiction)")
        p_top = (2 * ip3 + md) / 3.0
        axes[1].annotate(f"SFDR = {sf:.1f} dB", xy=(p_top, (md + p_top) / 2),
                         fontsize=9, rotation=90, ha="right", va="center")
        axes[1].vlines(p_top, md, p_top, color="#b3261e", lw=2)
        axes[1].set_xlim(-120, 15)
        axes[1].set_ylim(-130, 25)
        axes[1].set_xlabel("input power (dBm), each of two tones")
        axes[1].set_ylabel("input-referred level (dBm)")
        axes[1].set_title(f"the SFDR picture — {_fmt_chain(REF_MAST)}")
        axes[1].legend(fontsize=7, loc="upper left")
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("modules 1+2 not implemented")

    fig.tight_layout()
    fig.savefig("hw10_plots.png", dpi=130)
    print("wrote hw10_plots.png")
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
