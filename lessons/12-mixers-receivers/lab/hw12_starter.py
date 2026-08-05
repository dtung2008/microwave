"""Homework 12 starter — The frequency plan.

You implement the three modules marked TODO below. Everything else is the
toolkit: the receiver spec, the emitter table, the phase-noise synthesizer,
the closed-form referees, and the checker.

Run from this directory:

    python hw12_starter.py --check    # measured facts per module (the instrument)
    python hw12_starter.py --plot     # the two pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbm` / `*_dbc` are decibel
quantities; `*_hz`, `*_s`, `*_mps` are SI. Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
from scipy.constants import c as C_M_S          # speed of light, m/s
from scipy.signal import welch

# ----------------------------------------------------------------------------
# The receiver under design (instructor side — the spec your plan must meet)
# ----------------------------------------------------------------------------
# The course radar (lecture 1) grows its receiver this week. It tunes across
# an X-band block; the instantaneous signal fits one 10 MHz channel; a fixed
# IF (intermediate frequency) filter and a 100 MS/s ADC (analog-to-digital
# converter) close the chain. The ADC undersamples: the IF band only has to
# fit inside ONE Nyquist zone [k*fs/2, (k+1)*fs/2] and inside the ADC's
# analog input bandwidth — the carrier itself may sit above fs/2.
RX = dict(
    rf_lo_hz=10.0e9,       # bottom of the tunable RF band
    rf_hi_hz=10.4e9,       # top of the tunable RF band
    if_bw_hz=10e6,         # IF filter passband (instantaneous channel)
    adc_fs_hz=100e6,       # ADC sample rate (100 MS/s)
    adc_bw_hz=500e6,       # ADC analog input bandwidth
)

# Strong emitters near the site (a survey the instructor did for you; a real
# project starts with a spectrum analyzer on the mast — see ANSWERS Q5).
EMITTERS = [
    dict(name="marine radars",   f_lo_hz=9.300e9, f_hi_hz=9.500e9,
         note="harbor traffic, strong pulses"),
    dict(name="airfield radar",  f_lo_hz=9.595e9, f_hi_hz=9.605e9,
         note="9.6 GHz, 2 km away, very strong"),
    dict(name="police/amateur",  f_lo_hz=10.500e9, f_hi_hz=10.550e9,
         note="mobile, moderate"),
    dict(name="backhaul link",   f_lo_hz=11.200e9, f_hi_hz=11.700e9,
         note="microwave link on the same mast, strong"),
]

# The two plans the checker exercises. BUG_PLAN is hour 3's deliberate bug:
# it passes every self-consistency check and parks its image on the airfield
# radar. REF_PLAN is the instructor's chosen plan (a catalog 321.4 MHz IF).
BUG_PLAN = dict(side="low", if_hz=321.4e6)
REF_PLAN = dict(side="high", if_hz=321.4e6)

# ----------------------------------------------------------------------------
# The Doppler-corruption study (module 3's fixed test conditions)
# ----------------------------------------------------------------------------
# LO (local oscillator) phase-noise profile, SSB L(f) in dBc/Hz vs offset.
# Flat inside the 10 Hz PLL loop, then -30 dB/dec (1/f^3), then -20 dB/dec.
PN_PROFILE_DBC = [(1.0, -40.0), (10.0, -40.0), (100.0, -70.0),
                  (1e3, -90.0), (1e4, -110.0), (1e5, -120.0)]

DOPPLER = dict(
    f0_hz=10.2e9,          # radar carrier (mid-band); f_d = 2 v f0 / c
    clutter_db=60.0,       # clutter-to-drone power ratio (L14: the ground
    #                        is 60 dB bigger than the drone)
    snr_min_db=13.0,       # the Doppler line must clear the local skirt by
    #                        this much to count as visible (course standard)
    fs_hz=4096.0,          # sample rate of the baseband Doppler simulation
    t_total_s=64.0,        # total stare time (Welch-averaged 1 s frames)
    nperseg=4096,          # 1 s Hann frames -> 1 Hz bins, ENBW = 1.5 Hz
    thermal_dbc_hz=-100.0,  # thermal noise density re clutter (per Hz)
    seed=1212,             # fixed seed — the run is deterministic
)

# Test-target comb: one planted Doppler line per candidate offset (all on
# integer-Hz bins by construction, so no scalloping loss muddies module 3).
COMB_OFFSETS_HZ = np.array([40.0, 55.0, 75.0, 100.0, 130.0, 170.0, 220.0,
                            290.0, 380.0, 500.0, 650.0, 850.0, 1100.0,
                            1400.0])


# ----------------------------------------------------------------------------
# Toolkit (provided — think in these nouns; do not edit)
# ----------------------------------------------------------------------------
def db(x_lin):
    """Linear power ratio -> decibels (re-provided each lecture; course rule)."""
    return 10.0 * np.log10(np.asarray(x_lin, dtype=float))


def undb(x_db):
    """Decibels -> linear power ratio."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def lo_hz(f_rf_hz, if_hz, side):
    """LO frequency for a tuned RF: high-side f_RF + IF, low-side f_RF - IF."""
    if side == "high":
        return np.asarray(f_rf_hz, dtype=float) + if_hz
    if side == "low":
        return np.asarray(f_rf_hz, dtype=float) - if_hz
    raise ValueError("side must be 'high' or 'low'")


def nyquist_zone(f_hz, fs_hz):
    """Which Nyquist zone a frequency sits in: k = floor(f / (fs/2)).
    Zone 0 is DC..fs/2 (baseband); an undersampled band must fit one zone."""
    return int(np.floor(f_hz / (fs_hz / 2.0)))


def chebyshev_min_order(f_pass_lo_hz, f_pass_hi_hz, f_stop_hz,
                        rej_db, ripple_db=0.5):
    """Lecture 8's order estimate for a Chebyshev bandpass filter.

    Returns (n, n_exact, omega_s): minimum integer order, the exact real
    order, and the mapped stopband frequency omega_s of the lowpass
    prototype. f0 = sqrt(f1*f2); omega(f) = |f/f0 - f0/f| / (f2/f0 - f0/f2).
    """
    f0 = np.sqrt(f_pass_lo_hz * f_pass_hi_hz)
    bw = f_pass_hi_hz / f0 - f0 / f_pass_hi_hz
    omega_s = abs(f_stop_hz / f0 - f0 / f_stop_hz) / bw
    n_exact = (np.arccosh(np.sqrt((undb(rej_db) - 1.0)
                                  / (undb(ripple_db) - 1.0)))
               / np.arccosh(omega_s))
    return int(np.ceil(n_exact)), float(n_exact), float(omega_s)


def pn_dbc_hz(f_offset_hz):
    """SSB phase noise L(f) in dBc/Hz from PN_PROFILE_DBC, log-log
    interpolated, clamped flat outside the profile ends. Vectorized."""
    f = np.maximum(np.asarray(f_offset_hz, dtype=float), 1e-6)
    fp = np.log10([p[0] for p in PN_PROFILE_DBC])
    lp = [p[1] for p in PN_PROFILE_DBC]
    return np.interp(np.log10(f), fp, lp)


def synth_phase_rad(fs_hz, n, seed):
    """Synthesize a phase-noise time series phi(t) (radians, length n) whose
    one-sided PSD is S_phi(f) = 2*10^(L(f)/10) rad^2/Hz — the small-angle
    identity L(f) = S_phi(f)/2. Frequency-domain shaping, fixed seed."""
    rng = np.random.default_rng(seed)
    f = np.fft.rfftfreq(n, 1.0 / fs_hz)
    s_phi = np.zeros_like(f)
    s_phi[1:] = 2.0 * undb(pn_dbc_hz(f[1:]))
    z = (rng.standard_normal(len(f)) + 1j * rng.standard_normal(len(f)))
    a = z * np.sqrt(s_phi * fs_hz * n) / 2.0     # E|a|^2 = S*fs*n/2
    a[0] = 0.0
    a[-1] = a[-1].real
    return np.fft.irfft(a, n)


def doppler_scene():
    """The module-3 scene: clutter (0 Hz, +clutter_db) carrying the LO's
    phase noise, a comb of drone test lines (0 dB each) at COMB_OFFSETS_HZ,
    and thermal noise. Returns (t_s, x) with x complex baseband."""
    d = DOPPLER
    n = int(round(d["fs_hz"] * d["t_total_s"]))
    phi = synth_phase_rad(d["fs_hz"], n, d["seed"])
    t = np.arange(n) / d["fs_hz"]
    a_c = np.sqrt(undb(d["clutter_db"]))
    x = a_c * np.exp(1j * phi)
    for f_k in COMB_OFFSETS_HZ:
        x = x + np.exp(1j * (2.0 * np.pi * f_k * t + phi))
    rng = np.random.default_rng(d["seed"] + 1)
    sigma = np.sqrt(undb(d["clutter_db"] + d["thermal_dbc_hz"])
                    * d["fs_hz"] / 2.0)
    x = x + sigma * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return t, x


def doppler_psd():
    """Welch PSD of the scene with the course's Doppler-processing settings:
    1 s Hann frames (1 Hz bins, ENBW = 1.5 Hz), 50% overlap, 64 s stare.
    Returns (f_hz, pxx) for positive offsets only."""
    d = DOPPLER
    _, x = doppler_scene()
    f, pxx = welch(x, fs=d["fs_hz"], window="hann", nperseg=d["nperseg"],
                   noverlap=d["nperseg"] // 2, detrend=False,
                   return_onesided=False)
    keep = f > 0
    return f[keep], pxx[keep]


ENBW_HZ = 1.5   # of the 1 s Hann Doppler frame (exact for periodic Hann)


def doppler_hz_per_mps():
    """Doppler per unit radial speed at the carrier: 2 f0 / c (Hz per m/s)."""
    return 2.0 * DOPPLER["f0_hz"] / C_M_S


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def mixer_products(f_lo_hz, f_in_hz, order=3):
    """Module 1 — every mixer product |m*f_LO ± n*f_in| for 0 <= m, n <=
    order, (m, n) != (0, 0). Return a list of tuples (m, n, f_hz); when both
    m >= 1 and n >= 1 there are two products (difference and sum) — include
    both. m = 0 rows are the input's own harmonics, n = 0 rows the LO's.
    The checker compares your list against an independent closed form AND
    against FFT peaks measured from a behavioral diode mixer."""
    raise NotImplementedError


def image_band_hz(if_hz, side):
    """Module 1 — the image band swept across the RX tuning range: for every
    tuned f_RF in [RX['rf_lo_hz'], RX['rf_hi_hz']], the image sits at
    f_LO ± IF on the far side of the LO. Return (f_lo_hz, f_hi_hz) of the
    band the images cover. (Closed form — no loop needed.)"""
    raise NotImplementedError


def audit_plan(if_hz, side):
    """Module 2 (the core) — the interference audit for one candidate plan.

    Checks, against RX and EMITTERS:
      * own_band_clear: the image band does not overlap the RF tuning band
        (the preselector must pass the whole band, so it cannot help there);
      * zone_ok: the IF passband (if_hz ± if_bw/2) fits inside ONE Nyquist
        zone of the ADC and inside its analog input bandwidth;
      * collisions: for tuned f_RF across the band (a 1 MHz tune grid is
        fine), every product m*f_LO ± n*f_E (m, n <= 3) of the LO with each
        emitter that lands inside the IF passband. A product of an emitter
        BAND covers an interval — endpoints are enough (it is monotonic in
        f_E). Severity: 'fatal' for (m, n) == (1, 1) — that is the image,
        full conversion gain, no rejection available — else 'order-(m+n)'
        (real mixers suppress those by balance; see ANSWERS Q3).

    Return dict(image_band_hz=(lo, hi), own_band_clear=bool, zone_ok=bool,
                collisions=[dict(emitter=str, m=int, n=int, f_tune_hz=float,
                                 severity=str), ...],
                feasible=bool)   # everything true and no fatal collisions
    """
    raise NotImplementedError


def filter_specs(if_hz, side):
    """Module 2 — the filter specs your plan implies, in lecture 8's
    language (Chebyshev, 0.5 dB ripple, 60 dB rejection via the toolkit's
    chebyshev_min_order):
      * preselector: passband = the RF tuning band; stopband point = the
        image-band edge nearest the passband;
      * IF filter: passband = if_hz ± if_bw/2; stopband points = both edges
        of the Nyquist zone the IF sits in (anti-alias for undersampling);
        report the worse (higher-order) of the two.
    Return dict(presel_n=int, presel_n_exact=float, presel_stop_hz=float,
                if_n=int, if_n_exact=float, if_stop_hz=float)."""
    raise NotImplementedError


def doppler_study():
    """Module 3 — how slow a drone can this radar still see?

    Use the toolkit: doppler_psd() gives the Welch PSD of the scene (clutter
    + drone comb + thermal). For each offset in COMB_OFFSETS_HZ, measure the
    line's SNR against the LOCAL phase-noise skirt: the line lives in its
    exact bin (integer-Hz offsets, 1 Hz bins); estimate the skirt from bins
    a few Hz to either side (say 4–12 Hz away, excluding the line's own ±2
    bins), then SNR = (line bin − skirt) / skirt, in dB. A line is visible
    when SNR >= DOPPLER['snr_min_db']. The skirt falls 20 dB/decade through
    the crossing, so fit SNR against log10(f) near the threshold and solve
    for the crossing offset; convert to speed with doppler_hz_per_mps().

    Return dict(offsets_hz=array, snr_db=array, v_min_mps=float)."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
#
# Three referees, per the course's referee principle:
#   * a closed-form m,n grid (independent of your mixer_products),
#   * an FFT of a behavioral diode mixer — physics by construction,
#   * the analytic integrated-phase-noise bound for module 3.
# Read them AFTER you finish; they are the cleanest statements in the file.
# ----------------------------------------------------------------------------
def _closed_form_products(f_lo_hz, f_in_hz, order=3):
    """Independent m,n grid via array ops (the trig identities, vectorized)."""
    m, n = np.meshgrid(np.arange(order + 1), np.arange(order + 1),
                       indexing="ij")
    diff = np.abs(m * f_lo_hz - n * f_in_hz)
    summ = m * f_lo_hz + n * f_in_hz
    out = []
    for mi in range(order + 1):
        for ni in range(order + 1):
            if mi == 0 and ni == 0:
                continue
            out.append((mi, ni, float(diff[mi, ni])))
            if mi >= 1 and ni >= 1:
                out.append((mi, ni, float(summ[mi, ni])))
    return out


_DIODE = dict(f_lo_hz=800.0, f_rf_hz=530.0, fs_hz=8192.0, n=8192,
              a_lo=1.2, a_rf=0.9)


def _diode_spectrum():
    """Behavioral single-diode mixer at audio rate: i = exp(v) with
    v = a_lo*cos(w_lo t) + a_rf*cos(w_rf t). Every m*f_LO ± n*f_RF product
    exists by construction. Returns (f_hz, p_dbc) — power re strongest line.
    Deterministic (no noise); 1 Hz bins."""
    d = _DIODE
    t = np.arange(d["n"]) / d["fs_hz"]
    v = (d["a_lo"] * np.cos(2 * np.pi * d["f_lo_hz"] * t)
         + d["a_rf"] * np.cos(2 * np.pi * d["f_rf_hz"] * t))
    i = np.exp(v)
    spec = np.abs(np.fft.rfft(i - i.mean())) / d["n"]
    p = spec ** 2
    f = np.fft.rfftfreq(d["n"], 1.0 / d["fs_hz"])
    return f, db(np.maximum(p / p.max(), 1e-30))


def _match_products_to_peaks(products, f_hz, p_dbc, floor_dbc=-80.0):
    """How many predicted products have a measured spectral peak in their
    exact 1 Hz bin (local max within ±2 bins, above floor_dbc)."""
    hits, misses = 0, []
    for (m, n, fp) in products:
        k = int(round(fp))
        if k < 2 or k > len(p_dbc) - 3:
            continue
        window = p_dbc[k - 2:k + 3]
        if p_dbc[k] >= floor_dbc and p_dbc[k] == window.max():
            hits += 1
        else:
            misses.append((m, n, fp))
    return hits, misses


def _analytic_vmin_mps():
    """The analytic bound: the drone line is visible while
    P_drone >= SNR_min * P_clutter * L(f_d) * ENBW, i.e. while
    L(f_d) <= -clutter_db - snr_min_db - 10log10(ENBW). Invert the piecewise
    log-log profile for the crossing offset, convert to m/s."""
    d = DOPPLER
    l_star = -d["clutter_db"] - d["snr_min_db"] - db(ENBW_HZ)
    fp = np.array([p[0] for p in PN_PROFILE_DBC])
    lp = np.array([p[1] for p in PN_PROFILE_DBC])
    for i in range(len(fp) - 1):
        l1, l2 = lp[i], lp[i + 1]
        if (l1 - l_star) * (l2 - l_star) <= 0 and l1 != l2:
            frac = (l_star - l1) / (l2 - l1)
            f_star = 10 ** (np.log10(fp[i])
                            + frac * (np.log10(fp[i + 1]) - np.log10(fp[i])))
            return float(f_star / doppler_hz_per_mps()), float(f_star)
    raise RuntimeError("threshold outside profile")


def _fmt_ghz(f_hz):
    return f"{f_hz/1e9:.4f} GHz"


def run_checks(mods=None):
    m = mods or dict(mixer_products=mixer_products, image_band_hz=image_band_hz,
                     audit_plan=audit_plan, filter_specs=filter_specs,
                     doppler_study=doppler_study)
    print("=" * 66)
    print("hw12 --check : measured facts (instrument, not grade)")
    print("=" * 66)

    # --- module 1: the m,n grid and the image bands ------------------------
    print("\n[module 1] mixer_products / image_band_hz")
    try:
        d = _DIODE
        mine = m["mixer_products"](d["f_lo_hz"], d["f_rf_hz"], 3)
        ref = _closed_form_products(d["f_lo_hz"], d["f_rf_hz"], 3)
        a = np.sort([round(p[2], 6) for p in mine])
        b = np.sort([round(p[2], 6) for p in ref])
        if len(a) == len(b):
            print(f"  products to order 3: {len(a)} "
                  f"(closed form {len(b)}); max |df| = "
                  f"{np.max(np.abs(a - b)):.3e} Hz")
        else:
            print(f"  products to order 3: {len(a)} — closed form has "
                  f"{len(b)}; check your (m,n) enumeration")
        f_hz, p_dbc = _diode_spectrum()
        hits, misses = _match_products_to_peaks(mine, f_hz, p_dbc)
        print(f"  FFT referee (behavioral diode): {hits}/{len(mine)} "
              "predicted products have a measured peak in their exact bin")
        if misses:
            print(f"    missing: {misses[:4]} ...")
        for side in ("low", "high"):
            lo, hi = m["image_band_hz"](REF_PLAN["if_hz"], side)
            print(f"  image band, {side:4s}-side LO, IF = 321.4 MHz: "
                  f"{_fmt_ghz(lo)} – {_fmt_ghz(hi)}")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the plan, audited ---------------------------------------
    print("\n[module 2] audit_plan / filter_specs")
    try:
        for tag, plan in (("BUG (hour 3's)", BUG_PLAN), ("REF", REF_PLAN)):
            rep = m["audit_plan"](plan["if_hz"], plan["side"])
            fatal = [c for c in rep["collisions"] if c["severity"] == "fatal"]
            other = [c for c in rep["collisions"] if c["severity"] != "fatal"]
            print(f"  {tag}: {plan['side']}-side, IF = "
                  f"{plan['if_hz']/1e6:.1f} MHz -> own-band clear: "
                  f"{rep['own_band_clear']}, ADC zone ok: {rep['zone_ok']}, "
                  f"fatal collisions: {len(fatal)}, higher-order: "
                  f"{len(set((c['emitter'], c['m'], c['n']) for c in other))}"
                  f", feasible: {rep['feasible']}")
            for c in fatal[:3]:
                print(f"      FATAL image collision: {c['emitter']} at tune "
                      f"{_fmt_ghz(c['f_tune_hz'])} (m,n = {c['m']},{c['n']})")
            for key in sorted(set((c["emitter"], c["m"], c["n"])
                                  for c in other)):
                print(f"      note: ({key[1]},{key[2]}) product of "
                      f"{key[0]} reaches the IF (mixer balance's job)")
        # feasibility scan: where could a plan live at all?
        for side in ("low", "high"):
            grid = np.arange(205e6, 497.6e6, 2.5e6)
            ok = [f for f in grid if m["audit_plan"](f, side)["feasible"]]
            if ok:
                print(f"  feasible IF windows, {side:4s}-side: "
                      f"{min(ok)/1e6:.1f} – {max(ok)/1e6:.1f} MHz "
                      f"({len(ok)} of {len(grid)} grid points)")
            else:
                print(f"  feasible IF windows, {side:4s}-side: none "
                      f"(0 of {len(grid)} grid points)")
        spec = m["filter_specs"](REF_PLAN["if_hz"], REF_PLAN["side"])
        print(f"  REF preselector: n = {spec['presel_n']} "
              f"(n_exact {spec['presel_n_exact']:.2f}) for 60 dB at "
              f"{_fmt_ghz(spec['presel_stop_hz'])}")
        print(f"  REF IF filter:   n = {spec['if_n']} "
              f"(n_exact {spec['if_n_exact']:.2f}) for 60 dB at "
              f"{spec['if_stop_hz']/1e6:.0f} MHz (zone edge)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: the slow drone ------------------------------------------
    print("\n[module 3] doppler_study")
    try:
        study = m["doppler_study"]()
        hzmps = doppler_hz_per_mps()
        print("  offset (Hz) | speed (m/s) | line SNR over skirt (dB)")
        for f_k, s in zip(study["offsets_hz"], study["snr_db"]):
            mark = " <- visible" if s >= DOPPLER["snr_min_db"] else ""
            print(f"    {f_k:7.0f}   |   {f_k/hzmps:6.2f}    |  "
                  f"{s:7.2f}{mark}")
        v_ana, f_star = _analytic_vmin_mps()
        v_meas = study["v_min_mps"]
        print(f"  minimum visible speed: measured {v_meas:.3f} m/s | "
              f"analytic bound {v_ana:.3f} m/s (skirt crossing at "
              f"{f_star:.1f} Hz)")
        print(f"  relative error vs analytic bound: "
              f"{abs(v_meas - v_ana)/v_ana*100:.2f} %   (criterion: <= 5 %)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    m = mods or dict(audit_plan=audit_plan, doppler_study=doppler_study)
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))

    # --- picture 1: the frequency-planning chart (Q1's picture) ------------
    try:
        grid = np.arange(205e6, 497.6e6, 2.5e6)
        for row, side in enumerate(("low", "high")):
            feas = np.array([m["audit_plan"](f, side)["feasible"]
                             for f in grid])
            axes[0].fill_between(grid / 1e6, row + 0.1, row + 0.9,
                                 where=~feas, color="#f3c2bf", step="mid")
            axes[0].fill_between(grid / 1e6, row + 0.1, row + 0.9,
                                 where=feas, color="#bcd8b8", step="mid")
        axes[0].axvline(321.4, color="k", ls="--", lw=1)
        axes[0].annotate("321.4 MHz\n(catalog IF)", (321.4, 1.92),
                         ha="center", va="top", fontsize=8)
        axes[0].set_yticks([0.5, 1.5])
        axes[0].set_yticklabels(["low-side LO", "high-side LO"])
        axes[0].set_xlabel("IF (MHz)")
        axes[0].set_title("where a plan can live (green = passes the audit)")
        axes[0].set_ylim(0, 2)
    except NotImplementedError:
        axes[0].set_title("module 2 not implemented")

    # --- picture 2: the skirt and the drone comb (Q2's picture) ------------
    try:
        f_hz, pxx = doppler_psd()
        d = DOPPLER
        p_drone_bin = 1.0 / ENBW_HZ          # a 0 dB line's PSD in its bin
        axes[1].semilogx(f_hz, db(pxx / p_drone_bin), lw=0.6,
                         label="measured PSD (re drone line)")
        fg = np.logspace(np.log10(5), np.log10(2000), 200)
        skirt = d["clutter_db"] + pn_dbc_hz(fg)
        axes[1].semilogx(fg, skirt, "k--", lw=1.2,
                         label="clutter x L(f) skirt (design)")
        axes[1].axhline(-d["snr_min_db"], color="#b3261e", ls=":",
                        label=f"visibility bar (line - {d['snr_min_db']:.0f} dB)")
        study = m["doppler_study"]()
        vmin = study["v_min_mps"]
        f_min = vmin * doppler_hz_per_mps()
        axes[1].axvline(f_min, color="#0f62fe", ls="--", lw=1)
        axes[1].annotate(f"v_min = {vmin:.2f} m/s", (f_min * 1.06, 12),
                         color="#0f62fe", fontsize=9)
        axes[1].set_xlabel("Doppler offset (Hz)")
        axes[1].set_ylabel("PSD re drone line (dB)")
        axes[1].set_title("the skirt that buries the slow drone")
        axes[1].set_xlim(5, 2000)
        axes[1].set_ylim(-45, 65)
        axes[1].legend(fontsize=8, loc="upper right")
        axes[1].grid(True, which="both", alpha=0.25)
    except NotImplementedError:
        axes[1].set_title("module 3 not implemented")

    fig.tight_layout()
    fig.savefig("hw12_plots.png", dpi=130)
    print("wrote hw12_plots.png")
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
