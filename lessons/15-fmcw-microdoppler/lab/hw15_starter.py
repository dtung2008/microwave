"""Homework 15 starter — The drone in the parking lot.

You implement the three modules marked TODO below. Everything else is the
toolkit: the 77 GHz sensor, the delay/Doppler channel simulator with planted
ground truth, the CA-CFAR from homework 14 (re-provided as plumbing), and
the checker.

Run from this directory:

    python hw15_starter.py --check    # measured facts per module (the instrument)
    python hw15_starter.py --map      # the four pictures ANSWERS.md asks about

See HOMEWORK.md for the story and ANSWERS.md for the questions (two of them
must be answered BEFORE you run).

Unit conventions (course notation ledger, AUTHORING.md): every function name
or argument says its units. `*_db` / `*_dbm` are decibel quantities; `*_hz`,
`*_s`, `*_m`, `*_m_s` are SI. Velocity sign convention (stated once, used
everywhere): v is the RANGE RATE — positive = receding, negative = closing.
The dechirp mixer here is TX x conj(RX), which puts range at positive beat
frequency and a receding target at positive slow-time frequency +2v/lambda.
Never add two dBm numbers.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console safety

import argparse

import numpy as np
from scipy import ndimage
from scipy.constants import c as C_M_S          # speed of light, m/s

# ----------------------------------------------------------------------------
# The systems (instructor side — the specs your modules are graded against)
# ----------------------------------------------------------------------------
# The 77 GHz parking-lot sensor's chirp-sequence waveform (the reference
# design; module 1 must arrive at numbers like these from SPEC alone).
WAVEFORM = dict(
    f0_hz=77e9,        # carrier (start-of-chirp) frequency
    b_hz=300e6,        # chirp bandwidth B
    t_c_s=10e-6,       # chirp duration T_c (back-to-back, no dead time)
    n_chirps=512,      # chirps per CPI (coherent processing interval)
    fs_hz=51.2e6,      # complex (I/Q) ADC sample rate -> 512 samples/chirp
)

# The customer's waveform specification (module 1's input).
SPEC = dict(
    dr_max_m=0.5,          # range resolution, at least this fine
    r_cov_min_m=200.0,     # unaliased range coverage within the ADC rate
    v_unamb_min_m_s=75.0,  # unambiguous velocity, at least +/- this much
    dv_max_m_s=0.4,        # velocity resolution, at least this fine
)

# CA-CFAR parameters for the range-Doppler map (per-cell design P_fa; the
# map has 512 x 512 = 262,144 cells per frame — Q on false alarms per frame).
CFAR = dict(n_train=8, n_guard=2, pfa=1e-7)

# The hovering quadcopter's rotor (planted truth for module 3's referee:
# HERM-line spacing = n_blades * f_rot = 200 Hz, exact by construction).
QUAD = dict(n_blades=2, f_rot_hz=100.0, blade_len_m=0.11)

# The scene's planted targets: (name, range m, range rate m/s, map SNR dB).
# Every recovered (R, v) must land within one range and one Doppler bin.
SCENE_TRUTH = (
    ("airliner tail", 180.20,   0.00, 80.0),   # parked A330 beyond the fence
    ("car",            45.30, +11.80, 40.0),   # leaving the lot (receding)
    ("drone body",     25.10,   0.00, 22.0),   # hovering quadcopter
)


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


def chirp_slope_hz_s(waveform):
    """Chirp slope alpha_c = B / T_c."""
    return waveform["b_hz"] / waveform["t_c_s"]


def n_samples(waveform):
    """Complex samples per chirp = fs * T_c (512 for the reference design)."""
    return int(round(waveform["fs_hz"] * waveform["t_c_s"]))


def range_axis_m(waveform):
    """Range of each range-FFT bin: R = f_b * c / (2 alpha_c), f_b = k/T_c.
    Bin spacing is c/2B — bandwidth is resolution."""
    k = np.arange(n_samples(waveform))
    return k / waveform["t_c_s"] * C_M_S / (2.0 * chirp_slope_hz_s(waveform))


def velocity_axis_m_s(waveform, n_chirps=None):
    """Range rate of each (fftshifted) Doppler-FFT bin: v = f_slow*lambda/2.
    Positive = receding. Spans +/- lambda/(4 T_c)."""
    n = n_chirps or waveform["n_chirps"]
    f_slow = np.fft.fftshift(np.fft.fftfreq(n, waveform["t_c_s"]))
    return f_slow * wavelength_m(waveform["f0_hz"]) / 2.0


def dechirped_cube(waveform, scatterers, n_chirps=None, seed=1502):
    """The delay/Doppler channel + dechirp mixer, honestly.

    Simulates the dechirped (beat-domain) I/Q samples the ADC delivers:
    for each scatterer the FULL phase 2*pi*(f0*tau + alpha*tau*t - alpha*
    tau^2/2) with tau = 2*r(t)/c evaluated at every global sample instant —
    range-Doppler coupling, range migration, and blade modulation all fall
    out of the geometry, nothing is bolted on. Complex receiver noise of
    unit power (the thermal floor) is added.

    scatterers: list of dicts —
      point : dict(kind="point", r0_m=..., vr_m_s=..., amp=...)
      blade : dict(kind="blade", r0_m=..., l_m=..., f_rot_hz=...,
                   phase0=..., amp=...)   (rotating tip scatterer, Chen [R24])
    Returns complex array, shape (n_chirps, n_samples).
    """
    n_ch = n_chirps or waveform["n_chirps"]
    n_s = n_samples(waveform)
    alpha = chirp_slope_hz_s(waveform)
    f0 = waveform["f0_hz"]
    rng = np.random.default_rng(seed)
    t_f = np.arange(n_s) / waveform["fs_hz"]              # fast time in chirp
    t_g = np.arange(n_ch)[:, None] * waveform["t_c_s"] + t_f[None, :]
    cube = (rng.standard_normal((n_ch, n_s))
            + 1j * rng.standard_normal((n_ch, n_s))) * np.sqrt(0.5)
    for sc in scatterers:
        if sc["kind"] == "point":
            r = sc["r0_m"] + sc["vr_m_s"] * t_g
        elif sc["kind"] == "blade":
            r = sc["r0_m"] + sc["l_m"] * np.cos(
                2.0 * np.pi * sc["f_rot_hz"] * t_g + sc["phase0"])
        else:
            raise ValueError(f"unknown scatterer kind {sc['kind']!r}")
        tau = 2.0 * r / C_M_S
        cube += sc["amp"] * np.exp(1j * 2.0 * np.pi * (
            f0 * tau + alpha * tau * t_f[None, :] - 0.5 * alpha * tau**2))
    return cube


def _amp_for_map_snr(waveform, snr_map_db):
    """Scatterer amplitude that lands at snr_map_db in the Hann^2-windowed,
    unit-noise-normalized range-Doppler map (on-grid; off-grid scalloping
    shaves up to ~1.4 dB — quoted numbers are measured, not asserted)."""
    n_s, n_ch = n_samples(waveform), waveform["n_chirps"]
    gain = (n_s / 1.5) * (n_ch / 1.5)      # 2-D Hann SNR gain, (Sum w)^2/Sum w^2
    return float(np.sqrt(undb(snr_map_db) / gain))


def _scene_scatterers(waveform):
    """The parking lot: three point targets + one rotor (2 blade tips)."""
    sc = [dict(kind="point", r0_m=r, vr_m_s=v,
               amp=_amp_for_map_snr(waveform, snr))
          for _, r, v, snr in SCENE_TRUTH]
    drone_r = SCENE_TRUTH[2][1]
    for k in range(QUAD["n_blades"]):
        sc.append(dict(kind="blade", r0_m=drone_r, l_m=QUAD["blade_len_m"],
                       f_rot_hz=QUAD["f_rot_hz"],
                       phase0=2.0 * np.pi * k / QUAD["n_blades"], amp=0.03))
    return sc


def make_scene(waveform=WAVEFORM, seed=1502):
    """One CPI of the parking lot (512 chirps x 512 samples). Deterministic."""
    return dechirped_cube(waveform, _scene_scatterers(waveform),
                          n_chirps=waveform["n_chirps"], seed=seed)


def make_md_capture(waveform=WAVEFORM, n_chirps=8000, seed=1515):
    """The micro-Doppler dwell: 8000 chirps = 80 ms of the same scene
    (Doppler bin 12.5 Hz — fine enough to resolve the 200 Hz HERM comb)."""
    return dechirped_cube(waveform, _scene_scatterers(waveform),
                          n_chirps=n_chirps, seed=seed)


def ca_cfar(power_profile, n_train, n_guard, pfa):
    """Cell-averaging CFAR on a 1-D square-law POWER profile — this mirrors
    your homework-14 module 3 exactly (same interface, same edge policy:
    truncate the window at the array ends and recompute alpha for the actual
    training count; strict > comparison). This week it is plumbing.

      power_profile : 1-D array, square-law power samples
      n_train       : training cells per side
      n_guard       : guard cells per side
      pfa           : per-cell design false-alarm probability
      returns       : (detections, threshold) — bool and float arrays
    """
    z = np.asarray(power_profile, dtype=float)
    n = z.size
    ps = np.concatenate(([0.0], np.cumsum(z)))     # prefix sums
    i = np.arange(n)
    l_lo = np.clip(i - n_guard - n_train, 0, n)
    l_hi = np.clip(i - n_guard, 0, n)
    r_lo = np.clip(i + n_guard + 1, 0, n)
    r_hi = np.clip(i + n_guard + 1 + n_train, 0, n)
    train_sum = (ps[l_hi] - ps[l_lo]) + (ps[r_hi] - ps[r_lo])
    n_actual = (l_hi - l_lo) + (r_hi - r_lo)       # truncated at the edges
    alpha = n_actual * (pfa ** (-1.0 / n_actual) - 1.0)
    threshold = alpha * train_sum / n_actual
    return z > threshold, threshold


def cfar_alpha(n_train_total, pfa):
    """Closed-form CA-CFAR threshold multiplier (mirrors hw14's toolkit)."""
    n = float(n_train_total)
    return n * (pfa ** (-1.0 / n) - 1.0)


def group_detections(detections, power_map):
    """Merge a 2-D CFAR detection mask into distinct targets: detections
    within 3 cells of each other (a target's mainlobe + near sidelobes) are
    one group; each group reports its strongest cell. Returns a list of
    (doppler_row, range_col) peak cells, strongest first."""
    lab, n_lab = ndimage.label(
        ndimage.binary_dilation(detections, iterations=3))
    peaks = []
    for k in range(1, n_lab + 1):
        masked = np.where((lab == k) & detections, power_map, 0.0)
        i, j = np.unravel_index(int(np.argmax(masked)), power_map.shape)
        peaks.append((int(i), int(j)))
    return sorted(peaks, key=lambda ij: -power_map[ij])


# ----------------------------------------------------------------------------
# YOUR MODULES — implement below this line
# ----------------------------------------------------------------------------
def design_waveform(spec, f0_hz, fs_hz):
    """Module 1 (the design) — chirp-sequence waveform design, closed form.

    From the customer spec (a dict like SPEC), the carrier f0_hz, and the
    ADC rate fs_hz, choose and return dict(b_hz=..., t_c_s=..., n_chirps=...).

    The four constraints, from the lecture's design triangle:
      range resolution   c/2B            <= spec["dr_max_m"]
      range coverage     fs*c*T_c/(2B)   >= spec["r_cov_min_m"]
      unambiguous vel.   lambda/(4 T_c)  >= spec["v_unamb_min_m_s"]
      velocity resol.    lambda/(2N T_c) <= spec["dv_max_m_s"]
    Note T_c is squeezed from BOTH sides — work out its legal window first,
    then pick round numbers. The checker audits whatever you return against
    the closed forms; many designs pass, the reference is one of them.
    """
    raise NotImplementedError


def range_doppler_map(cube, range_window=True):
    """Module 2 (the retina) — dechirped cube -> range-Doppler POWER map.

    Hann-window the fast-time axis (unless range_window=False — that switch
    is the homework's window experiment, leave it working), range FFT along
    axis 1; Hann-window slow time, Doppler FFT along axis 0, fftshift the
    Doppler axis so velocity_axis_m_s labels the rows. Return |.|^2
    normalized by (sum wr^2)*(sum wd^2) so unit-variance receiver noise
    averages to power 1.0 — the map then reads directly in dB re thermal.
    """
    raise NotImplementedError


def extract_targets(power_map, waveform):
    """Module 2 (the verdict) — CFAR the map, return the target list.

    Run the toolkit's ca_cfar (CFAR settings) along the RANGE axis of every
    Doppler row, group the detection mask with group_detections, and return
    a list of dicts: dict(r_m=..., v_m_s=..., snr_db=...) — one per target,
    strongest first, positions read off range_axis_m / velocity_axis_m_s.
    """
    raise NotImplementedError


def micro_doppler_spectrum(cube_md, r_m, waveform):
    """Module 3 (the dwell) — slow-time spectrum of one range cell.

    Range-process the micro-Doppler capture (Hann + range FFT, as in your
    map), take the slow-time series at the range cell nearest r_m, Hann it,
    FFT it, fftshift it. Return (freq_hz, power_lin): the slow-time
    (Doppler) frequency axis and the power spectrum. The HERM comb lives
    here; scipy.signal.stft of the same series is the --map spectrogram.
    """
    raise NotImplementedError


def herm_spacing_hz(freq_hz, power_lin):
    """Module 3 (the measurement) — measured HERM-line spacing in Hz.

    Find the comb lines (peaks well above the local floor — say 10 dB over
    the median; scipy.signal.find_peaks is your friend) on the positive-
    frequency side, and return a robust estimate of their common spacing.
    The edge that bites: the weakest lines duck under any threshold, so
    adjacent DETECTED lines can be one, two, or three spacings apart — a
    bare median of the differences lands on a multiple. Estimate the
    fundamental from the smallest differences first, then fold every
    difference down by its nearest integer multiple.
    This number IS n_blades * f_rot — the referee holds it to 2%.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------------
# The instrument (provided — measured facts, not grades; do not edit)
# ----------------------------------------------------------------------------
def _audit_design(design, spec, f0_hz, fs_hz):
    """Closed-form audit of a waveform design. Returns list of fact lines."""
    lam = wavelength_m(f0_hz)
    b, t_c, n = design["b_hz"], design["t_c_s"], design["n_chirps"]
    alpha = b / t_c
    rows = [
        ("range resolution c/2B", C_M_S / (2 * b), "<=", spec["dr_max_m"], "m"),
        ("range coverage fs*c*T_c/2B", fs_hz * C_M_S * t_c / (2 * b), ">=",
         spec["r_cov_min_m"], "m"),
        ("unambiguous velocity lam/4T_c", lam / (4 * t_c), ">=",
         spec["v_unamb_min_m_s"], "m/s"),
        ("velocity resolution lam/2NT_c", lam / (2 * n * t_c), "<=",
         spec["dv_max_m_s"], "m/s"),
    ]
    lines = []
    for name, got, op, want, unit in rows:
        ok = got <= want if op == "<=" else got >= want
        lines.append(f"    {name:32s} = {got:9.4f} {unit:3s} "
                     f"(spec {op} {want:g}) {'meets' if ok else 'MISSES'}")
    lines.append(f"    slope alpha_c = {alpha:.3e} Hz/s; beat at "
                 f"{spec['r_cov_min_m']:.0f} m = "
                 f"{2 * spec['r_cov_min_m'] * alpha / C_M_S / 1e6:.2f} MHz "
                 f"(ADC {fs_hz / 1e6:.1f} MHz complex)")
    lines.append(f"    CPI = N*T_c = {n * t_c * 1e3:.2f} ms; chirps N = {n}; "
                 f"T_c legal window: "
                 f"[{spec['r_cov_min_m'] * 2 * b / (fs_hz * C_M_S) * 1e6:.2f}, "
                 f"{wavelength_m(f0_hz) / (4 * spec['v_unamb_min_m_s']) * 1e6:.2f}] us "
                 f"at this B")
    return lines


def _match_truth(targets, waveform):
    """Pair each planted target with the nearest recovered one (bin units)."""
    dr = C_M_S / (2.0 * waveform["b_hz"])
    dv = (wavelength_m(waveform["f0_hz"])
          / (2.0 * waveform["n_chirps"] * waveform["t_c_s"]))
    out = []
    for name, r_true, v_true, snr in SCENE_TRUTH:
        best, best_d = None, np.inf
        for t in targets:
            d = np.hypot((t["r_m"] - r_true) / dr, (t["v_m_s"] - v_true) / dv)
            if d < best_d:
                best, best_d = t, d
        out.append((name, r_true, v_true, best))
    return out, dr, dv


def run_checks(mods=None):
    m = mods or dict(design_waveform=design_waveform,
                     range_doppler_map=range_doppler_map,
                     extract_targets=extract_targets,
                     micro_doppler_spectrum=micro_doppler_spectrum,
                     herm_spacing_hz=herm_spacing_hz)
    lam = wavelength_m(WAVEFORM["f0_hz"])
    print("=" * 66)
    print("hw15 --check : measured facts (instrument, not grade)")
    print("=" * 66)

    # --- module 1: the waveform design -------------------------------------
    print("\n[module 1] design_waveform")
    try:
        d = m["design_waveform"](SPEC, WAVEFORM["f0_hz"], WAVEFORM["fs_hz"])
        print(f"  your design: B = {d['b_hz'] / 1e6:.1f} MHz, "
              f"T_c = {d['t_c_s'] * 1e6:.2f} us, N = {d['n_chirps']}")
        for line in _audit_design(d, SPEC, WAVEFORM["f0_hz"],
                                  WAVEFORM["fs_hz"]):
            print(line)
        print(f"  reference design: B = {WAVEFORM['b_hz'] / 1e6:.0f} MHz, "
              f"T_c = {WAVEFORM['t_c_s'] * 1e6:.0f} us, "
              f"N = {WAVEFORM['n_chirps']}  (other choices can pass the audit)")
        f_tip = 2 * 2 * np.pi * QUAD["f_rot_hz"] * QUAD["blade_len_m"] / lam
        print(f"  blade-tip check: f_tip = {f_tip / 1e3:.2f} kHz vs your "
              f"unambiguous +/-{1 / (2 * d['t_c_s']) / 1e3:.1f} kHz "
              f"({'unaliased' if f_tip < 1 / (2 * d['t_c_s']) else 'ALIASED'})")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 2: the pipeline on the parking lot -------------------------
    print("\n[module 2] range_doppler_map / extract_targets")
    try:
        cube = make_scene()
        power = m["range_doppler_map"](cube)     # probe before any output
        n_ch, n_s = cube.shape
        wr, wd = np.hanning(n_s), np.hanning(n_ch)
        w2 = np.sum(wr**2) * np.sum(wd**2)
        e_map = float(np.sum(power))
        e_win = n_ch * n_s * float(np.sum(
            np.abs(cube * wr[None, :] * wd[:, None]) ** 2)) / w2
        print(f"  Parseval through your chain: |sum(map) - N*Ns*sum|w.x|^2/W2|"
              f" / sum = {abs(e_map - e_win) / e_win:.2e}")
        noise_med = float(np.median(power))
        print(f"  map noise median = {db(noise_med):+.2f} dB re thermal "
              f"(exponential noise medians at ln 2 = -1.59 dB)")
        targets = m["extract_targets"](power, WAVEFORM)
        matched, dr, dv = _match_truth(targets, WAVEFORM)
        print(f"  {len(targets)} targets extracted "
              f"(expected false alarms per frame at pfa="
              f"{CFAR['pfa']:.0e}: {n_ch * n_s * CFAR['pfa']:.3f}):")
        print("    planted                          recovered"
              "                    error (bins)")
        for name, r_t, v_t, best in matched:
            if best is None:
                print(f"    {name:14s} ({r_t:7.2f} m, {v_t:+6.2f} m/s)  "
                      "-> NOT RECOVERED")
                continue
            er, ev = (best["r_m"] - r_t) / dr, (best["v_m_s"] - v_t) / dv
            print(f"    {name:14s} ({r_t:7.2f} m, {v_t:+6.2f} m/s)  -> "
                  f"({best['r_m']:7.2f} m, {best['v_m_s']:+6.2f} m/s) "
                  f"{best['snr_db']:5.1f} dB   ({er:+.2f}, {ev:+.2f})")
        print(f"    one bin = {dr:.4f} m in range, {dv:.4f} m/s in velocity")

        # Q1's instrument: what lives in the drone's range column?
        dc0 = int(round(SCENE_TRUTH[2][1] / dr))
        va = velocity_axis_m_s(WAVEFORM)
        col = power[:, dc0].copy()
        body = np.argsort(col)[::-1][:1]
        col[n_ch // 2 - 2:n_ch // 2 + 3] = 0.0     # mask the body's rows
        blades = np.argsort(col)[::-1][:3]
        print(f"  the drone's range column (Q1): body row v = "
              f"{va[body[0]]:+.2f} m/s at {db(power[body[0], dc0]):.1f} dB; "
              "strongest cells away from v=0: "
              + ", ".join(f"{db(power[i, dc0]):.1f} dB at {va[i]:+.1f} m/s"
                          for i in blades))

        # the window experiment (hour 3's deliberate bug, measured)
        power_nw = m["range_doppler_map"](cube, range_window=False)
        targets_nw = m["extract_targets"](power_nw, WAVEFORM)
        i0 = n_ch // 2
        dc = int(round(SCENE_TRUTH[2][1] / dr))
        near = np.r_[dc - 20:dc - 3, dc + 4:dc + 21]
        _, thr_w = ca_cfar(power[i0], CFAR["n_train"], CFAR["n_guard"],
                           CFAR["pfa"])
        _, thr_nw = ca_cfar(power_nw[i0], CFAR["n_train"], CFAR["n_guard"],
                            CFAR["pfa"])
        drone_found = any(abs(t["r_m"] - SCENE_TRUTH[2][1]) < 2 * dr
                          and abs(t["v_m_s"]) < 2 * dv for t in targets_nw)
        print("  the window experiment (v = 0 row, around the drone):")
        print(f"    leakage floor +/-20 cells: Hann "
              f"{db(np.median(power[i0, near])):+6.2f} dB re thermal | "
              f"no window {db(np.median(power_nw[i0, near])):+6.2f} dB")
        print(f"    drone cell power:          Hann "
              f"{db(power[i0, dc]):+6.2f} dB | "
              f"no window {db(power_nw[i0, dc]):+6.2f} dB")
        print(f"    CFAR threshold there:      Hann "
              f"{db(thr_w[dc]):+6.2f} dB | "
              f"no window {db(thr_nw[dc]):+6.2f} dB")
        print(f"    drone in the target list:  Hann "
              f"{any(n == 'drone body' and b is not None for n, *_, b in matched)}"
              f"  | no window {drone_found}   "
              f"({len(targets_nw)} targets without the window)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- module 3: micro-Doppler ------------------------------------------
    print("\n[module 3] micro_doppler_spectrum / herm_spacing_hz")
    try:
        cube_md = make_md_capture()
        freq, p_md = m["micro_doppler_spectrum"](cube_md, SCENE_TRUTH[2][1],
                                                 WAVEFORM)
        spacing = float(m["herm_spacing_hz"](freq, p_md))
        truth = QUAD["n_blades"] * QUAD["f_rot_hz"]
        print(f"  dwell: {cube_md.shape[0]} chirps = "
              f"{cube_md.shape[0] * WAVEFORM['t_c_s'] * 1e3:.0f} ms; "
              f"Doppler bin {1 / (cube_md.shape[0] * WAVEFORM['t_c_s']):.2f} Hz")
        print(f"  measured HERM spacing = {spacing:.3f} Hz | planted "
              f"n_blades*f_rot = {truth:.1f} Hz | error "
              f"{abs(spacing - truth) / truth * 100:.3f} % (referee: 2 %)")
        v_tip = 2 * np.pi * QUAD["f_rot_hz"] * QUAD["blade_len_m"]
        print(f"  blade tips: v_tip = {v_tip:.2f} m/s -> micro-Doppler edge "
              f"2v_tip/lam = {2 * v_tip / lam / 1e3:.2f} kHz "
              f"(slow-time Nyquist +/-{1 / (2 * WAVEFORM['t_c_s']) / 1e3:.0f} kHz"
              " — the module-1 spec kept this unaliased)")
        p_db = db(np.asarray(p_md) + 1e-300)
        floor = float(np.median(p_db))
        strong = np.asarray(freq)[p_db > floor + 15.0]
        if strong.size:
            print(f"  lines >= 15 dB over the floor span "
                  f"{strong.min() / 1e3:+.2f} .. {strong.max() / 1e3:+.2f} kHz")
        print(f"  spacing alone gives the PRODUCT n_blades*f_rot = "
              f"{spacing:.1f} Hz; with the vendor's n_blades = 2: f_rot = "
              f"{spacing / 2:.1f} Hz = {spacing / 2 * 60:.0f} rpm  (Q4)")
    except NotImplementedError:
        print("  not implemented")
    except Exception as e:                                    # noqa: BLE001
        print(f"  ERROR: {type(e).__name__}: {e}")

    print("\ndone. numbers above are material for ANSWERS.md.")


def make_plots(mods=None, show=True):
    import matplotlib.pyplot as plt
    from scipy.signal import stft

    m = mods or dict(range_doppler_map=range_doppler_map,
                     extract_targets=extract_targets,
                     micro_doppler_spectrum=micro_doppler_spectrum)
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.8))
    lam = wavelength_m(WAVEFORM["f0_hz"])
    dr = C_M_S / (2.0 * WAVEFORM["b_hz"])

    # --- picture 1: the range-Doppler map (Q1's picture) -------------------
    ax = axes[0, 0]
    try:
        cube = make_scene()
        power = m["range_doppler_map"](cube)
        ra = range_axis_m(WAVEFORM)
        va = velocity_axis_m_s(WAVEFORM)
        ax.imshow(db(power + 1e-300), aspect="auto", origin="lower",
                  extent=[ra[0], ra[-1], va[0], va[-1]],
                  vmin=-5, vmax=45, cmap="viridis")
        for name, r_t, v_t, _ in SCENE_TRUTH:
            ax.annotate(name, (r_t, v_t), color="w", fontsize=8,
                        xytext=(8, 8), textcoords="offset points")
        ax.set_xlabel("range (m)")
        ax.set_ylabel("range rate (m/s, receding +)")
        ax.set_title("the range-Doppler map (dB re thermal)")
    except NotImplementedError:
        ax.set_title("module 2 not implemented")

    # --- picture 2: the window experiment on the v=0 row (Q2) --------------
    ax = axes[0, 1]
    try:
        i0 = WAVEFORM["n_chirps"] // 2
        power_nw = m["range_doppler_map"](cube, range_window=False)
        ra = range_axis_m(WAVEFORM)
        ax.plot(ra, db(power_nw[i0] + 1e-300), lw=0.7, alpha=0.75,
                label="no range window")
        ax.plot(ra, db(power[i0] + 1e-300), lw=0.7, alpha=0.9,
                label="Hann range window")
        _, thr_nw = ca_cfar(power_nw[i0], CFAR["n_train"], CFAR["n_guard"],
                            CFAR["pfa"])
        ax.plot(ra, db(thr_nw), "r:", lw=1.0, label="CFAR threshold (no win)")
        ax.axvline(SCENE_TRUTH[2][1], color="k", ls="--", alpha=0.5)
        ax.annotate("drone", (SCENE_TRUTH[2][1], 30), ha="center", fontsize=8)
        ax.set_xlim(0, 220)
        ax.set_ylim(-15, 90)
        ax.set_xlabel("range (m)")
        ax.set_ylabel("power (dB re thermal)")
        ax.set_title("v = 0 row: the airliner's sidelobes vs the drone")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        ax.set_title("module 2 not implemented")

    # --- pictures 3+4: the micro-Doppler dwell (Q1, Q4) --------------------
    try:
        cube_md = make_md_capture()
        freq, p_md = m["micro_doppler_spectrum"](cube_md, SCENE_TRUTH[2][1],
                                                 WAVEFORM)
        # spectrogram of the same slow-time series the spectrum came from
        n_s = cube_md.shape[1]
        rp = np.fft.fft(cube_md * np.hanning(n_s)[None, :], axis=1)
        st_series = rp[:, int(round(SCENE_TRUTH[2][1] / dr))]
        f_st, t_st, z_st = stft(st_series, fs=1.0 / WAVEFORM["t_c_s"],
                                nperseg=256, noverlap=224,
                                return_onesided=False)
        order = np.argsort(f_st)                # fftfreq order -> ascending
        ax = axes[1, 0]
        s_db = db(np.abs(z_st[order]) ** 2 + 1e-300)
        med = float(np.median(s_db))
        ax.pcolormesh(t_st * 1e3, f_st[order] / 1e3,
                      s_db, vmin=med + 2, vmax=med + 22,
                      shading="auto", cmap="viridis")
        v_tip = 2 * np.pi * QUAD["f_rot_hz"] * QUAD["blade_len_m"]
        for s in (+1, -1):
            ax.axhline(s * 2 * v_tip / lam / 1e3, color="w", ls=":", lw=0.8)
        ax.set_xlabel("time (ms)")
        ax.set_ylabel("micro-Doppler (kHz)")
        ax.set_title("STFT of the drone's range cell (blade flashes; "
                     "dotted = ±2v_tip/λ)")

        ax = axes[1, 1]
        ax.plot(freq / 1e3, db(np.asarray(p_md) + 1e-300), lw=0.7)
        truth = QUAD["n_blades"] * QUAD["f_rot_hz"]
        for k in range(1, 11):
            ax.axvline(k * truth / 1e3, color="r", ls=":", lw=0.7, alpha=0.6)
        ax.set_xlim(-0.2, 2.2)
        ax.set_xlabel("slow-time frequency (kHz)")
        ax.set_ylabel("power (dB)")
        ax.set_title("the HERM comb (red: multiples of n_b·f_rot = 200 Hz)")
        ax.grid(True, alpha=0.3)
    except NotImplementedError:
        axes[1, 0].set_title("module 3 not implemented")
        axes[1, 1].set_title("module 3 not implemented")

    fig.tight_layout()
    fig.savefig("hw15_map.png", dpi=130)
    print("wrote hw15_map.png")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="measured facts per module")
    ap.add_argument("--map", action="store_true",
                    help="the four pictures ANSWERS.md asks about")
    args = ap.parse_args()
    if args.check:
        run_checks()
    if args.map:
        make_plots()
    if not (args.check or args.map):
        print(__doc__)


if __name__ == "__main__":
    main()
