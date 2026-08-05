"""Homework 7 starter — Feed four antennas.

A four-element array needs an equal-amplitude feed: a corporate tree of three
Wilkinson dividers, plus a branch-line hybrid for a monopulse experiment. You
implement the three modules marked TODO below: the even/odd closed form, the
corporate feed assembled in skrf Circuit, and the monopulse teaser. Everything
else is the toolkit: the frequency grid, the ideal-TEM media, the assembled
Wilkinson and branch-line building blocks, lecture 4's invariant suite, the
closed-form referees, plotting, and the checker.

Run from this directory:

    python hw7_starter.py --check    # measured facts per module (the instrument)
    python hw7_starter.py --plot     # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Conventions: f0 = 10 GHz sits exactly on the sweep grid (index I_F0). All
S-matrices are 50-ohm referenced at the external ports. Wilkinson port order:
1 = input, 2/3 = outputs. Branch-line port order (Pozar fig. 7.21): 1 = input,
2 = through, 3 = coupled, 4 = isolated; the monopulse experiment hangs the two
antenna elements on ports 2 and 3 and reads Sigma at port 1, Delta at port 4.
skrf Circuit facts, verified against the installed 1.13.0 wheel: external
ports appear in the reduced network IN THE ORDER their Port objects first
appear in the connections list (not alphabetically); every network in a
Circuit needs a unique, non-empty .name.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
import skrf
from scipy.constants import c as C_M_S
from skrf.circuit import Circuit
from skrf.media import DefinedGammaZ0

Z0_OHM = 50.0                                  # course reference impedance
F0_HZ = 10.0e9                                 # design frequency (X-band)
FREQ = skrf.Frequency(5, 15, 201, "ghz")       # the sweep; step 50 MHz
I_F0 = int(np.argmin(np.abs(FREQ.f - F0_HZ)))  # = 100; FREQ.f[I_F0] == F0_HZ
Z_QW_OHM = Z0_OHM * np.sqrt(2.0)               # 70.711 — the Wilkinson arm
R_ISO_OHM = 2.0 * Z0_OHM                       # 100 — the isolation resistor

# Ideal dispersionless TEM medium: gamma = j*omega/c, so a line cut for 90
# degrees at f0 is 45 degrees at f0/2 — real electrical length, real sweeps.
MEDIA = DefinedGammaZ0(frequency=FREQ, z0=Z0_OHM, gamma=1j * FREQ.w / C_M_S)

# Invariant-suite tolerance (lecture 4's RECIP_TOL; this lab has no planted
# measurement noise, so residuals sit at float precision, ~1e-15).
RECIP_TOL = 2e-3


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db20(x):
    """|x| in dB (20 log10), floored at 1e-16 (-320 dB) so ideal nulls print."""
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-16))


def tem_line(z_ohm, deg_at_f0, name):
    """Lossless TEM line as a 2-port Network: characteristic impedance z_ohm,
    electrical length deg_at_f0 degrees AT F0 (scales linearly with f). The
    length is passed to skrf in meters on purpose — media.line's 'deg' unit
    is referenced to the band center, and being explicit costs nothing."""
    d_m = (deg_at_f0 / 360.0) * (C_M_S / F0_HZ)
    return MEDIA.line(d_m, unit="m", z0=z_ohm, name=name)


def resistor2(r_ohm, name):
    """Series resistor as a 2-port Network (skrf media.resistor)."""
    return MEDIA.resistor(r_ohm, name=name)


def circuit_port(name):
    """External 50-ohm port for skrf Circuit. Remember: port order in the
    reduced network = order of first appearance in the connections list."""
    return Circuit.Port(FREQ, name=name, z0=Z0_OHM)


def wilkinson_network(z_line_ohm=Z_QW_OHM, r_iso_ohm=R_ISO_OHM,
                      name="wilkinson"):
    """The equal-split Wilkinson assembled in skrf Circuit (hour 3 built this
    live): two quarter-wave arms of z_line_ohm from the input junction, the
    isolation resistor r_iso_ohm across the outputs. Ports: 1 in, 2/3 out.
    This is module 1's referee and module 2's building block."""
    p1 = circuit_port(f"port1_{name}")
    p2 = circuit_port(f"port2_{name}")
    p3 = circuit_port(f"port3_{name}")
    arm_a = tem_line(z_line_ohm, 90.0, name=f"arm_a_{name}")
    arm_b = tem_line(z_line_ohm, 90.0, name=f"arm_b_{name}")
    r_iso = resistor2(r_iso_ohm, name=f"r_iso_{name}")
    cnx = [
        [(p1, 0), (arm_a, 0), (arm_b, 0)],       # input tee
        [(p2, 0), (arm_a, 1), (r_iso, 0)],       # output a + resistor end
        [(p3, 0), (arm_b, 1), (r_iso, 1)],       # output b + resistor end
    ]
    ntwk = Circuit(cnx).network
    ntwk.name = name
    return ntwk


def branchline_network(name="branchline"):
    """The 3-dB branch-line (90 deg) hybrid assembled in skrf Circuit: series
    arms Z0/sqrt(2) between ports 1-2 and 4-3, shunt arms Z0 between 1-4 and
    2-3, all quarter-wave at f0. Ports: 1 in, 2 through, 3 coupled, 4
    isolated. At f0: S21 = -j/sqrt(2), S31 = -1/sqrt(2), S41 = 0."""
    p1 = circuit_port(f"port1_{name}")
    p2 = circuit_port(f"port2_{name}")
    p3 = circuit_port(f"port3_{name}")
    p4 = circuit_port(f"port4_{name}")
    ser_12 = tem_line(Z0_OHM / np.sqrt(2.0), 90.0, name=f"ser12_{name}")
    ser_43 = tem_line(Z0_OHM / np.sqrt(2.0), 90.0, name=f"ser43_{name}")
    shn_14 = tem_line(Z0_OHM, 90.0, name=f"shn14_{name}")
    shn_23 = tem_line(Z0_OHM, 90.0, name=f"shn23_{name}")
    cnx = [
        [(p1, 0), (ser_12, 0), (shn_14, 0)],
        [(p2, 0), (ser_12, 1), (shn_23, 0)],
        [(p3, 0), (ser_43, 1), (shn_23, 1)],
        [(p4, 0), (ser_43, 0), (shn_14, 1)],
    ]
    ntwk = Circuit(cnx).network
    ntwk.name = name
    return ntwk


def s_at_f0(ntwk):
    """The S-matrix of a Network at exactly f0 (one (n,n) complex array)."""
    return ntwk.s[I_F0]


# Lecture 4's invariant suite, re-provided as toolkit (you built these in
# hw4; same names, same semantics — here they referee, they don't teach).
def is_reciprocal(s, tol=RECIP_TOL):
    """True if S = S-transpose everywhere to within tol (plain transpose)."""
    return bool(np.abs(s - np.swapaxes(s, -1, -2)).max() <= tol)


def unitarity_residual(s):
    """Worst-over-frequency Frobenius norm of (S^H S - I): 0 iff lossless.
    Accepts (nf, n, n) or a single (n, n) matrix."""
    s = np.asarray(s)
    if s.ndim == 2:
        s = s[None]
    gram = np.conj(np.swapaxes(s, -1, -2)) @ s - np.eye(s.shape[-1])
    return float(np.linalg.norm(gram, axis=(-2, -1)).max())


def passivity_residual(s):
    """Worst-over-frequency max(sigma_max(S)^2 - 1, 0): 0 iff passive."""
    s = np.asarray(s)
    if s.ndim == 2:
        s = s[None]
    sv_max = np.linalg.svd(s, compute_uv=False)[..., 0]
    return float(max(0.0, float((sv_max**2 - 1.0).max())))


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def wilkinson_s0(z_line_ohm, r_iso_ohm, z0_ohm=Z0_OHM):
    """Module 1 (the core) — the Wilkinson's 3x3 S-matrix AT f0, closed form,
    from the even/odd-mode analysis, for ARBITRARY arm impedance z_line_ohm
    and isolation resistor r_iso_ohm (not just the ideal values — the
    formulas must carry the design's failure modes too).

    Port order: 1 in, 2/3 out. Work the analysis on paper first: even mode
    (outputs driven ++) sees an open where the resistor was cut; odd mode
    (+-) sees a short at the input junction and half the resistor to ground.
    At f0 every quarter-wave tangent has gone to infinity — take the limits
    by hand, do not evaluate tan(pi/2) numerically. The checker compares
    this against the skrf-assembled circuit for four (z_line, r_iso) cases;
    the syllabus bar is 1e-6."""
    raise NotImplementedError


def corporate_feed():
    """Module 2 — the four-antenna feed: three toolkit wilkinson_network()
    instances (give each a distinct name) assembled into one 5-port with
    skrf Circuit. Port order must be: 1 = transmitter in, 2..5 = the four
    antenna outputs, left to right — remember the appearance-order rule.
    Return the reduced skrf Network."""
    raise NotImplementedError


def feed_facts(ntwk):
    """Module 2 — measure the feed at f0. Return a dict with:
      balance_db   : max spread among the four |S_k1| in dB (ideal: 0)
      split_db     : worst-case |S_k1| in dB (nominal: -6.02)
      match_db     : |S_11| in dB
      isolation_db : worst (largest) |S_jk| in dB over the six output pairs
    The checker prints its own referee values next to yours."""
    raise NotImplementedError


def monopulse_response(hybrid, psi_rad):
    """Module 3 — the two-element monopulse experiment at f0. The antenna
    elements feed ports 2 and 3 with equal amplitudes and relative phase
    psi (port 3 leads port 2 by psi_rad; total incident power = 1):
    a2 = 1/sqrt(2), a3 = exp(j*psi)/sqrt(2), a1 = a4 = 0. Push them through
    the hybrid's S at f0 and return (p_sigma_db, p_delta_db): the power
    emerging from port 1 (Sigma) and port 4 (Delta), in dB re the incident
    total, vectorized over psi_rad."""
    raise NotImplementedError


def delta_null(hybrid):
    """Module 3 — locate the Delta-port null: sweep psi over [0, 360) deg
    (0.25 deg steps are fine), find the psi that minimizes the Delta power,
    and return (psi_null_deg, null_depth_db) where null_depth_db is Delta
    minus Sigma AT THAT psi (how far the null sits below the beam)."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Module 1's referee is the skrf-assembled circuit (an independent authority:
# it never saw your algebra, only lines and a resistor). Module 2's referee
# is the closed-form ideal S(f0) of the tree — every path is two quarter-wave
# hops, (-j/sqrt2)^2 = -1/2 — plus lecture 4's invariant suite. Module 3's
# referee is the hybrid's own S-matrix read at the null: the two paths into
# Delta must arrive exactly 180 degrees apart. Read these after you finish.
# ----------------------------------------------------------------------------
def _ideal_feed_s0():
    """Closed-form S(f0) of the ideal corporate tree: S_k1 = S_1k = -1/2
    (two quarter-wave hops from input to every output), all other entries 0."""
    s = np.zeros((5, 5), dtype=complex)
    s[1:, 0] = -0.5
    s[0, 1:] = -0.5
    return s


def _imbalance_vs_depth(err_db=0.1, max_depth=3):
    """Worst-case output imbalance of a corporate tree whose every Wilkinson
    carries err_db of arm-to-arm amplitude spread (each arm +/- err_db/2 of
    nominal), computed by walking path amplitudes leaf by leaf. This is Q1's
    referee: commit to a prediction before reading its output."""
    rows = []
    for depth in range(1, max_depth + 1):
        n_leaves = 2**depth
        amps_db = []
        for leaf in range(n_leaves):
            # worst case: arms signed so the leftmost path collects every
            # +err/2 and the rightmost every -err/2
            a_db = 0.0
            for level in range(depth):
                arm = (leaf >> (depth - 1 - level)) & 1     # 0 = high arm
                a_db += -3.0103 + (err_db / 2.0) * (1.0 if arm == 0 else -1.0)
            amps_db.append(a_db)
        rows.append((depth, n_leaves, max(amps_db) - min(amps_db)))
    return rows


def run_checks(mods=None):
    m = mods or dict(wilkinson_s0=wilkinson_s0, corporate_feed=corporate_feed,
                     feed_facts=feed_facts,
                     monopulse_response=monopulse_response,
                     delta_null=delta_null)
    print("=" * 64)
    print("hw7 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: even/odd closed form vs the assembled circuit -----------
    print("\n[module 1] wilkinson_s0 — hand even/odd vs skrf Circuit at f0")
    try:
        cases = [("ideal      z_line=70.71, R=100", Z_QW_OHM, 100.0),
                 ("thin arms  z_line=60.00, R=100", 60.0, 100.0),
                 ("hour-3 bug z_line=70.71, R=200", Z_QW_OHM, 200.0),
                 ("both wrong z_line=85.00, R=60 ", 85.0, 60.0)]
        for label, z_line, r_iso in cases:
            s_hand = np.asarray(m["wilkinson_s0"](z_line, r_iso))
            s_ref = s_at_f0(wilkinson_network(z_line, r_iso, name="ref"))
            print(f"  {label}: max|dS| = {np.abs(s_hand - s_ref).max():.2e}")
        print("  (syllabus bar for all four: 1e-6)")
        s_id = np.asarray(m["wilkinson_s0"](Z_QW_OHM, 100.0))
        print(f"  ideal S21 = {db20(s_id[1, 0]):.4f} dB at "
              f"{np.degrees(np.angle(s_id[1, 0])):.1f} deg"
              "   (-3.0103 dB, -90 deg)")
        print(f"  ideal |S11| = {np.abs(s_id[0, 0]):.1e}, "
              f"|S23| = {np.abs(s_id[1, 2]):.1e}   (analytic 0, 0)")
        s_bug = np.asarray(m["wilkinson_s0"](Z_QW_OHM, 200.0))
        print(f"  R doubled : |S11| = {np.abs(s_bug[0, 0]):.1e}  but "
              f"|S22| = {np.abs(s_bug[1, 1]):.4f} = 1/6, "
              f"isolation = {db20(s_bug[1, 2]):.2f} dB"
              "   (match survives, isolation collapses)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the corporate feed --------------------------------------
    print("\n[module 2] corporate_feed / feed_facts — the four-antenna tree")
    try:
        feed = m["corporate_feed"]()
        s0 = s_at_f0(feed)
        print(f"  ports: {feed.nports}   "
              f"vs closed-form ideal S(f0): max|dS| = "
              f"{np.abs(s0 - _ideal_feed_s0()).max():.2e}")
        outs_db = db20(s0[1:, 0])
        iso_ref = max(db20(s0[j, k]) for j in range(1, 5)
                      for k in range(j + 1, 5))
        print(f"  referee: outputs |S_k1| = "
              + " ".join(f"{v:8.4f}" for v in outs_db) + " dB")
        print(f"  referee: balance spread = {outs_db.max() - outs_db.min():.2e} dB"
              f"   (syllabus: <= 0.01 dB ideal)")
        print(f"  referee: match |S11| = {db20(s0[0, 0]):7.1f} dB, "
              f"worst output-output isolation = {iso_ref:7.1f} dB"
              "   (syllabus: > 30 dB)")
        facts = m["feed_facts"](feed)
        print("  yours  : " + "  ".join(
            f"{k} = {facts[k]:.4f}" for k in
            ("balance_db", "split_db", "match_db", "isolation_db")))
        print(f"  invariants (lecture 4's suite): reciprocal = "
              f"{is_reciprocal(feed.s)}, passivity residual = "
              f"{passivity_residual(feed.s):.1e}")
        print(f"  unitarity residual at f0 = {unitarity_residual(s0):.6f}"
              f"   (sqrt(3) = {np.sqrt(3.0):.6f} — NOT lossless; Q3 asks why)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # the Q1 referee runs on the toolkit alone — predictions first
    print("\n[instrument] worst-case imbalance vs tree depth "
          "(0.1 dB per-Wilkinson arm spread)")
    for depth, n_leaves, imb in _imbalance_vs_depth():
        print(f"  depth {depth} ({n_leaves} outputs): {imb:.3f} dB")
    print("  (grows with depth = log2(N) — Q1 asks you to predict this "
          "before looking)")

    # --- module 3: the monopulse teaser ------------------------------------
    print("\n[module 3] monopulse_response / delta_null — Sigma and Delta")
    try:
        hyb = branchline_network()
        s0 = s_at_f0(hyb)
        print(f"  hybrid pedigree: |S21| = {db20(s0[1, 0]):.4f} dB, "
              f"|S31| = {db20(s0[2, 0]):.4f} dB, "
              f"phase(S21)-phase(S31) = "
              f"{np.degrees(np.angle(s0[1, 0]) - np.angle(s0[2, 0])):.1f} deg")
        print(f"  hybrid isolation |S41| at f0 = {db20(s0[3, 0]):.1f} dB "
              "(float floor -320)")
        p_sig, p_del = m["monopulse_response"](hyb, 0.0)
        print(f"  boresight (psi = 0): Sigma = {float(np.squeeze(p_sig)):.4f} dB, "
              f"Delta = {float(np.squeeze(p_del)):.4f} dB   (Q2 predicted this)")
        psi_null, depth_db = m["delta_null"](hyb)
        print(f"  Delta null: psi = {psi_null:.2f} deg, "
              f"depth = {depth_db:.1f} dB below Sigma"
              "   (syllabus: deeper than 60 dB)")
        a2, a3 = 1.0 / np.sqrt(2.0), np.exp(1j * np.radians(psi_null)) / np.sqrt(2.0)
        path_a, path_b = s0[3, 1] * a2, s0[3, 2] * a3
        dphi = np.degrees(np.angle(path_a) - np.angle(path_b)) % 360.0
        print(f"  the 180-degree check: the two paths into Delta arrive "
              f"{np.abs(path_a):.4f} and {np.abs(path_b):.4f} in amplitude, "
              f"{dphi:.6f} deg apart")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    m = mods or dict(corporate_feed=corporate_feed,
                     monopulse_response=monopulse_response)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    f_ghz = FREQ.f / 1e9

    # --- picture 1: the corporate feed swept (Q1/Q3's picture) -------------
    try:
        feed = m["corporate_feed"]()
        s = feed.s
        for k in range(1, 5):
            axes[0].plot(f_ghz, db20(s[:, k, 0]), lw=1.2,
                         label=f"|S{k + 1}1| (output {k})" if k == 1 else None)
        axes[0].plot(f_ghz, db20(s[:, 0, 0]), "k", lw=1.2, label="|S11| match")
        iso = np.max(np.stack([db20(s[:, j, k]) for j in range(1, 5)
                               for k in range(1, 5) if j < k]), axis=0)
        axes[0].plot(f_ghz, iso, "r--", lw=1.2, label="worst out-out isolation")
        axes[0].axvline(F0_HZ / 1e9, color="gray", ls=":", alpha=0.6)
        axes[0].axhline(-6.02, color="gray", lw=0.7, alpha=0.6)
        axes[0].set_xlabel("frequency (GHz)")
        axes[0].set_ylabel("dB")
        axes[0].set_ylim(-60, 0)
        axes[0].set_title("the corporate feed, swept")
        axes[0].legend(fontsize=8, loc="lower right")
        axes[0].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[0].set_title("module 2 not implemented")

    # --- picture 2: Sigma and Delta vs psi (Q2's picture) ------------------
    try:
        hyb = branchline_network()
        psi_deg = np.arange(0.0, 360.0, 0.25)
        p_sig, p_del = m["monopulse_response"](hyb, np.radians(psi_deg))
        axes[1].plot(psi_deg, p_sig, label=r"$\Sigma$ (port 1)")
        axes[1].plot(psi_deg, p_del, label=r"$\Delta$ (port 4)")
        axes[1].axvline(90.0, color="gray", ls=":", alpha=0.6)
        axes[1].axvline(0.0, color="gray", ls="--", alpha=0.4)
        axes[1].annotate("boresight", (0.0, -40), fontsize=8, rotation=90,
                         textcoords="offset points", xytext=(4, 0))
        axes[1].set_xlabel(r"relative phase $\psi$ (deg), port 3 vs port 2")
        axes[1].set_ylabel("output power (dB re incident)")
        axes[1].set_ylim(-80, 3)
        axes[1].set_title("the monopulse curves at f$_0$")
        axes[1].legend(fontsize=9, loc="lower right")
        axes[1].grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1].set_title("module 3 not implemented")

    fig.tight_layout()
    fig.savefig("hw7_plots.png", dpi=130)
    print("wrote hw7_plots.png")
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
