"""Homework 4 starter — Trust, but verify the two-port.

Three "measured" two-port datasets (NETWORKS["A"], ["B"], ["C"]) arrived with
claims attached. You implement the three modules marked TODO below: the
conversion library, the invariant suite, and the verdicts. Everything else is
the toolkit: the frequency grid, the planted datasets, ABCD element builders,
the skrf referee, plotting, and the checker.

Run from this directory:

    python hw4_starter.py --check    # measured facts per module (the instrument)
    python hw4_starter.py --plot     # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Array conventions: every S / Z / ABCD matrix is a numpy array of shape
(nf, 2, 2), frequency-major, complex. `@` matrix-multiplies such stacks
frequency-by-frequency for free. Reference impedance is real 50 ohm at both
ports unless stated. Sᵀ (plain transpose) tests reciprocity; Sᴴ (conjugate
transpose) builds the unitarity/passivity tests — mixing the two is THE
classic bug of this homework.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np

Z0_OHM = 50.0                                  # course reference impedance
F_HZ = np.linspace(0.05e9, 3.0e9, 201)         # the "VNA sweep" all files share
W_RAD_S = 2.0 * np.pi * F_HZ

# Course tolerances for the invariant suite. Rationale: the planted "VNA"
# adds ~1e-4 of noise per S entry, which floors the residuals near 1e-3
# (reciprocity) and 1e-3 (unitarity). Tolerances sit ~5x above the floor.
# Lectures 7 and 11 reuse these names and values.
RECIP_TOL = 2e-3
UNIT_TOL = 5e-3
PASSIV_TOL = 5e-3


# ----------------------------------------------------------------------------
# Toolkit — ABCD element builders (provided; think in these nouns)
# ----------------------------------------------------------------------------
def abcd_series(z_ohm):
    """ABCD of a series impedance z (scalar or length-nf array): [[1, z],[0, 1]]."""
    a = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    a[:, 0, 0] = 1.0
    a[:, 1, 1] = 1.0
    a[:, 0, 1] = z_ohm
    return a


def abcd_shunt(y_s):
    """ABCD of a shunt admittance y (scalar or length-nf array): [[1, 0],[y, 1]]."""
    a = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    a[:, 0, 0] = 1.0
    a[:, 1, 1] = 1.0
    a[:, 1, 0] = y_s
    return a


def abcd_line(z_line_ohm, f0_hz, quarter_waves):
    """ABCD of a lossless line, length = quarter_waves x (lambda/4 at f0_hz)."""
    bl = (np.pi / 2.0) * quarter_waves * (F_HZ / f0_hz)
    a = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    a[:, 0, 0] = np.cos(bl)
    a[:, 1, 1] = np.cos(bl)
    a[:, 0, 1] = 1j * z_line_ohm * np.sin(bl)
    a[:, 1, 0] = 1j * np.sin(bl) / z_line_ohm
    return a


def to_network(s):
    """Wrap an (nf,2,2) S array as a scikit-rf Network on the course grid."""
    import skrf
    return skrf.Network(frequency=skrf.Frequency.from_f(F_HZ, unit="hz"),
                        s=s, z0=Z0_OHM)


# ----------------------------------------------------------------------------
# The evidence — three planted "measurements" (instructor side)
#
# SEALED ENVELOPE. The generator below is the ground truth for the three
# datasets. Commit your verdicts in ANSWERS.md BEFORE reading it — the whole
# exercise is whether your invariant suite can convict without the envelope.
# Ground truth, for after: A is a 5th-order 0.5 dB Chebyshev lowpass
# (fc = 1 GHz) with finite-Q elements (Q_L = 40, Q_C = 400) — reciprocal,
# passive, lossy, exactly as its label says. B is a 3rd-order Butterworth
# lowpass (fc = 1.2 GHz) whose file claims ideal lossless elements, but
# Q_L = 150 / Q_C = 1500 of dissipation was left in — reciprocal and passive,
# NOT unitary: the claim is false. C is no filter at all: a behavioral
# amplifier (+8 dB forward gain, one-pole rolloff at 2 GHz, ~30 dB reverse
# isolation) wearing a passive device's file label — non-reciprocal and
# non-passive into 50 ohm. All three carry ~1e-4 of "VNA noise", seeded, so
# every run of --check sees identical data.
# ----------------------------------------------------------------------------
def _a2s_ref(a):
    """Generator-side ABCD -> S. Uses the skrf referee on purpose: the
    evidence is minted by the same authority your module 1 is checked
    against, so nothing here depends on your TODO functions."""
    from skrf.network import a2s
    return a2s(a, z0=Z0_OHM)


def _lowpass_ladder(g_values, fc_hz, q_l, q_c):
    """Shunt-C-first lumped lowpass ladder from prototype g-values, with
    finite element Q (series r = wL/Q_L, shunt g = wC/Q_C)."""
    wc = 2.0 * np.pi * fc_hz
    a = None
    for k, gk in enumerate(g_values):
        if k % 2 == 0:                                   # shunt C
            c_f = gk / (Z0_OHM * wc)
            sec = abcd_shunt(1j * W_RAD_S * c_f + W_RAD_S * c_f / q_c)
        else:                                            # series L
            l_h = gk * Z0_OHM / wc
            sec = abcd_series(1j * W_RAD_S * l_h + W_RAD_S * l_h / q_l)
        a = sec if a is None else a @ sec
    return _a2s_ref(a)


def _make_planted():
    rng = np.random.default_rng(20260804)                # fixed: --check is
                                                         # deterministic
    def vna(s):                                          # ~1e-4 measurement noise
        return s + (rng.normal(scale=1e-4, size=s.shape)
                    + 1j * rng.normal(scale=1e-4, size=s.shape))

    s_a = _lowpass_ladder([1.7058, 1.2296, 2.5408, 1.2296, 1.7058],
                          fc_hz=1.0e9, q_l=40.0, q_c=400.0)

    s_b = _lowpass_ladder([1.0, 2.0, 1.0], fc_hz=1.2e9, q_l=150.0, q_c=1500.0)

    s_c = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    s_c[:, 1, 0] = 10.0 ** (8.0 / 20.0) / (1.0 + 1j * F_HZ / 2.0e9)
    s_c[:, 0, 1] = 0.03 * np.exp(-1j * 2.0 * np.pi * F_HZ / 6.0e9)
    s_c[:, 0, 0] = 0.12 * np.exp(-1j * 2.0 * np.pi * F_HZ / 3.0e9)
    s_c[:, 1, 1] = 0.18 * np.exp(-1j * 2.0 * np.pi * F_HZ / 4.0e9)

    return {
        "A": dict(s=vna(s_a),
                  claim="passive lowpass filter; some dissipation expected"),
        "B": dict(s=vna(s_b),
                  claim="LOSSLESS lowpass filter (ideal elements, says the file)"),
        "C": dict(s=vna(s_c),
                  claim="passive two-port, per the shipping label"),
    }


NETWORKS = _make_planted()


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def s_to_abcd(s, z0=Z0_OHM):
    """Module 1 — S -> ABCD for a two-port, (nf,2,2) in and out, real equal
    reference z0 at both ports. Watch the 2*S21 in every denominator: deep
    in a stopband S21 is tiny and this division is legal but delicate."""
    raise NotImplementedError


def abcd_to_s(a, z0=Z0_OHM):
    """Module 1 — ABCD -> S, (nf,2,2) in and out, real equal z0."""
    raise NotImplementedError


def s_to_z(s, z0=Z0_OHM):
    """Module 1 — S -> Z (impedance matrix), (nf,2,2) in and out.
    Z = z0 (I - S)^(-1) (I + S) for real equal z0."""
    raise NotImplementedError


def z_to_s(z, z0=Z0_OHM):
    """Module 1 — Z -> S, (nf,2,2) in and out, real equal z0."""
    raise NotImplementedError


def cascade(*s_list, z0=Z0_OHM):
    """Module 1 — cascade any number of two-ports given as S arrays; return
    the S array of the chain. Route through ABCD (S-matrices do NOT cascade
    by matrix multiplication — hour 3 demonstrated the wreck)."""
    raise NotImplementedError


def is_reciprocal(s, tol=RECIP_TOL):
    """Module 2 (the core) — True if S = S-transpose at every frequency to
    within tol (largest |S12 - S21| over the sweep). Plain transpose — no
    conjugate anywhere in this one."""
    raise NotImplementedError


def unitarity_residual(s):
    """Module 2 (the core) — how far from lossless: the worst-over-frequency
    Frobenius norm of (S-conjugate-transpose @ S - I). Exactly 0 for a
    lossless network; the course writes it as the number ||S^H S - I||."""
    raise NotImplementedError


def passivity_residual(s):
    """Module 2 (the core) — how far outside passivity: worst-over-frequency
    max(sigma_max(S)^2 - 1, 0), where sigma_max is the largest singular
    value. A passive network scatters no more power than it accepts, at any
    excitation, so every singular value obeys sigma <= 1; the residual is 0
    for passive, positive for active (or broken) data."""
    raise NotImplementedError


def verdict(s, claim):
    """Module 3 — the classification, built on YOUR module 2. Return a short
    one-line string that states: reciprocal or not; lossless / lossy-passive /
    non-passive (use the course tolerances); and whether `claim` survives the
    evidence. Exact wording is yours — ANSWERS.md carries the defense."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Module 1's referee is scikit-rf (s2a / a2s / s2z / z2s and the ** cascade
# operator). Module 2's referee is planted analytic truth: a matched line is
# unitary BY CONSTRUCTION, a x1/2 pad has ||S^H S - I|| = 3/(2*sqrt(2)) on
# paper, an ideal isolator is the textbook non-reciprocal device. The tiny
# _invariants_referee below exists so a module-2 bug cannot hide inside the
# module-3 table; read it after you finish — it is the suite in ten lines.
# ----------------------------------------------------------------------------
def _invariants_referee(s):
    """(reciprocity residual, unitarity residual, passivity residual)."""
    recip = float(np.abs(s - np.swapaxes(s, -1, -2)).max())
    gram = np.conj(np.swapaxes(s, -1, -2)) @ s - np.eye(s.shape[-1])
    unit = float(np.linalg.norm(gram, axis=(-2, -1)).max())
    sv_max = np.linalg.svd(s, compute_uv=False)[:, 0]
    passiv = float(max(0.0, (sv_max**2 - 1.0).max()))
    return recip, unit, passiv


def _reference_sections():
    """Six known-good passive sections (S arrays minted by the skrf referee)
    for the cascade check — mismatched on purpose so a wrong cascade cannot
    luck into the right answer."""
    mats = [abcd_line(75.0, 1.0e9, 1.0),
            abcd_series(1j * W_RAD_S * 4e-9 + 2.0),
            abcd_shunt(1j * W_RAD_S * 1.5e-12),
            abcd_line(30.0, 1.0e9, 0.6),
            abcd_shunt(1.0 / (1j * W_RAD_S * 8e-9)),
            abcd_line(60.0, 1.0e9, 1.7)]
    return [_a2s_ref(a) for a in mats]


def _pad_s(k=0.5):
    """Matched attenuator: S11 = S22 = 0, S12 = S21 = k (k=1/2 is 6.02 dB)."""
    s = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    s[:, 0, 1] = k
    s[:, 1, 0] = k
    return s


def _isolator_s():
    """Ideal isolator: S21 = 1, S12 = 0 — the textbook non-reciprocal device."""
    s = np.zeros((len(F_HZ), 2, 2), dtype=complex)
    s[:, 1, 0] = 1.0
    return s


def run_checks(mods=None):
    m = mods or dict(s_to_abcd=s_to_abcd, abcd_to_s=abcd_to_s, s_to_z=s_to_z,
                     z_to_s=z_to_s, cascade=cascade, is_reciprocal=is_reciprocal,
                     unitarity_residual=unitarity_residual,
                     passivity_residual=passivity_residual, verdict=verdict)
    print("=" * 64)
    print("hw4 --check : measured facts (instrument, not grade)")
    print("=" * 64)

    # --- module 1: conversions + cascade, refereed by scikit-rf ------------
    print("\n[module 1] s_to_abcd / abcd_to_s / s_to_z / z_to_s / cascade")
    try:
        from skrf.network import a2s, s2a, s2z, z2s
        worst = dict(a=0.0, art=0.0, z=0.0, zrt=0.0)
        for name, net in NETWORKS.items():
            s = net["s"]
            worst["a"] = max(worst["a"],
                             float(np.abs(m["s_to_abcd"](s) - s2a(s, z0=Z0_OHM)).max()))
            worst["art"] = max(worst["art"],
                               float(np.abs(m["abcd_to_s"](m["s_to_abcd"](s)) - s).max()))
            worst["z"] = max(worst["z"],
                             float(np.abs(m["s_to_z"](s) - s2z(s, z0=Z0_OHM)).max()))
            worst["zrt"] = max(worst["zrt"],
                               float(np.abs(m["z_to_s"](m["s_to_z"](s)) - s).max()))
        print(f"  s_to_abcd vs skrf s2a, worst over A/B/C : {worst['a']:.2e}")
        print(f"  abcd_to_s(s_to_abcd(S)) - S round trip  : {worst['art']:.2e}")
        print(f"  s_to_z    vs skrf s2z, worst over A/B/C : {worst['z']:.2e}")
        print(f"  z_to_s(s_to_z(S)) - S round trip        : {worst['zrt']:.2e}")
        secs = _reference_sections()
        ref = to_network(secs[0])
        for s_k in secs[1:]:
            ref = ref ** to_network(s_k)
        d_casc = float(np.abs(m["cascade"](*secs) - ref.s).max())
        print(f"  cascade of 6 mismatched sections vs skrf ** : {d_casc:.2e}")
        print("  (syllabus bar for all five lines: 1e-10)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the invariant suite on planted analytic references ------
    print("\n[module 2] is_reciprocal / unitarity_residual / passivity_residual")
    try:
        line = _a2s_ref(abcd_line(50.0, 1.0e9, 1.0))
        pad = _pad_s(0.5)
        iso = _isolator_s()
        print(f"  matched 50-ohm line : unitarity = {m['unitarity_residual'](line):.2e}"
              "   (lossless by construction: analytic 0)")
        print(f"  x1/2 pad (6.02 dB)  : unitarity = {m['unitarity_residual'](pad):.5f}"
              f"   (analytic 3/(2*sqrt(2)) = {3/(2*np.sqrt(2)):.5f})")
        print(f"                        passivity = {m['passivity_residual'](pad):.2e}"
              "   (passive: analytic 0)")
        print(f"  ideal isolator      : is_reciprocal = {m['is_reciprocal'](iso)}"
              "   (S21 = 1, S12 = 0: analytic False)")
        print(f"  matched line        : is_reciprocal = {m['is_reciprocal'](line)}"
              "   (analytic True)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the verdicts on the three planted datasets --------------
    print("\n[module 3] verdict — the three files, cross-read against the "
          "harness referee")
    for name, net in NETWORKS.items():
        r_ref, u_ref, p_ref = _invariants_referee(net["s"])
        print(f"  network {name} (claim: {net['claim']})")
        print(f"    referee residuals: recip = {r_ref:.2e}  "
              f"unitarity = {u_ref:.4f}  passivity = {p_ref:.4f}")
        try:
            print(f"    your verdict     : {m['verdict'](net['s'], net['claim'])}")
        except NotImplementedError:
            print("    your verdict     : not implemented")
        except Exception as e:                                # noqa: BLE001
            print(f"    your verdict     : ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    db20 = lambda x: 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))  # noqa: E731

    # --- picture 1: what the eye sees — |S21| in dB (Q2's picture) ---------
    for name, net in NETWORKS.items():
        axes[0].plot(F_HZ / 1e9, db20(net["s"][:, 1, 0]),
                     label=f"{name}: {net['claim'].split(';')[0].split(' (')[0]}")
    axes[0].axhline(0.0, color="k", lw=0.8, alpha=0.6)
    axes[0].set_xlabel("frequency (GHz)")
    axes[0].set_ylabel(r"$|S_{21}|$ (dB)")
    axes[0].set_ylim(-60, 12)
    axes[0].set_title("what the datasheet plot shows")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    # --- picture 2: what the invariant sees — sigma_max vs the ceiling -----
    # (plotting plumbing: per-frequency largest singular value, the quantity
    # whose worst excess your passivity_residual reports as one number)
    for name, net in NETWORKS.items():
        sv_max = np.linalg.svd(net["s"], compute_uv=False)[:, 0]
        axes[1].plot(F_HZ / 1e9, sv_max, label=f"{name}")
    axes[1].axhline(1.0, color="k", ls=":", lw=1.5,
                    label="passivity ceiling $\\sigma_{max} = 1$")
    axes[1].set_xlabel("frequency (GHz)")
    axes[1].set_ylabel(r"$\sigma_{max}(S)$")
    axes[1].set_title("what the passivity invariant sees")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("hw4_plots.png", dpi=130)
    print("wrote hw4_plots.png")
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
