# Homework 15 — The drone in the parking lot

**Follows:** Lecture 15 (FMCW, Doppler & micro-Doppler)
**Submit:** `hw15_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

A 77 GHz FMCW sensor on a light pole watches an airport's long-term parking lot.
Three things are in its field of view tonight: the tail of a parked A330 beyond the
fence at 180 m (an airliner-sized reflector, stone still, enormously strong), a car
leaving the lot at 11.8 m/s, and — the reason the sensor exists — a small quadcopter
hovering at 25 m, dead still, exactly where drones are not allowed to be.

Your job, in three moves: **design the waveform** (B, T_c, N_chirps) that meets the
customer's resolution and ambiguity spec — including the requirement, unusual for a
parking lot, that ±75 m/s of velocity stay unambiguous (the drone's blade tips do
69 m/s, and the customer wants to *see* them); **build the pipeline** — dechirped
cube → windowed range FFT → Doppler FFT → CA-CFAR (your homework-14 detector,
re-provided as plumbing) → a target list with (R, v) for everything in the lot; and
**stare at the drone's range cell** for 80 ms, take the STFT and the slow-time
spectrum, and measure the HERM-line spacing that names it a drone and not a bird.

Every target's (R, v) is planted by construction, so the referee is exact: your
recovered positions must land within one range bin and one Doppler bin; your measured
HERM spacing must land within 2% of the planted n_blades·f_rot = 200 Hz; and energy
must survive your FFT chain (Parseval — the checker measures the residual). The
airliner is 58 dB stronger than the drone and 155 m away — whether the drone
survives *your* range FFT depends on one line of code, and the checker runs your
pipeline both ways to show you.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `design_waveform` | the design triangle, closed form | ~35 min | 20% |
| 2 | `range_doppler_map`, `extract_targets` | **the core** — the map and the verdict | ~65 min | 40% |
| 3 | `micro_doppler_spectrum`, `herm_spacing_hz` | the long stare; drone named | ~40 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs
(module 3 gets the drone's *planted* range, not your module-2 output), so a broken
module 1 never hides module 3.

**Signs, stated once** (they bite everyone once): v is the **range rate** — positive
= receding. The toolkit's dechirp convention puts range at positive beat frequency
and a receding target at positive slow-time frequency +2v/λ; `velocity_axis_m_s`
carries the convention so your map reads correctly if you fftshift the Doppler axis
and label rows with the toolkit's axis. The planted car *recedes* at +11.8 m/s.

**Module-2 contract details** (the parts that save you an hour): normalize the map
by (Σw_r²)·(Σw_d²) so unit-variance noise averages to power 1.0 — the map then reads
in dB re thermal and the checker's numbers will match yours. Keep the
`range_window=False` switch working — the checker uses it for the window experiment.
CFAR runs along the **range axis of each Doppler row** (the toolkit's `ca_cfar` is
your hw14 module 3, verbatim — same interface, same edge policy); `group_detections`
merges each target's mainlobe-plus-sidelobe cluster and hands you peak cells.

**Module-3 edge that bites:** the weakest comb lines duck under any peak threshold,
so adjacent *detected* lines can sit two or three spacings apart — a bare median of
the differences lands on a multiple of the truth (400 or 600 Hz, not 200). Estimate
the fundamental from the smallest differences first, then fold every difference down
by its nearest integer multiple. (`scipy.signal.find_peaks` finds the lines; the
folding is three lines of numpy and the actual thinking.)

## Running it — the two commands

```
python hw15_starter.py --check    # measured facts per module (the instrument)
python hw15_starter.py --map      # the four pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues. Everything is seeded — reruns reproduce exactly.

## The toolkit (provided — think in these nouns)

- `WAVEFORM`, `SPEC`, `CFAR`, `QUAD`, `SCENE_TRUTH` — the sensor, the customer's
  spec, the detector settings, and the planted truth (yes, you can read the answers;
  the referee measures whether your *pipeline* recovers them).
- `db` / `undb`, `wavelength_m`, `chirp_slope_hz_s`, `n_samples` — the vocabulary.
- `range_axis_m`, `velocity_axis_m_s` — the map's physical axes (the sign convention
  lives here so it can only be wrong in one place).
- `dechirped_cube(waveform, scatterers, n_chirps, seed)` — the delay/Doppler channel
  + dechirp mixer: full phase 2π(f₀τ + α_cτt − ½α_cτ²) at every sample instant, unit
  receiver noise. `make_scene()` is one 512-chirp CPI of the parking lot;
  `make_md_capture()` is the 8000-chirp (80 ms) micro-Doppler dwell of the same lot.
- `ca_cfar(power_profile, n_train, n_guard, pfa)` — **your homework-14 CA-CFAR**,
  re-provided verbatim as plumbing (n_train/n_guard per side, edge-truncating,
  strict `>`). `cfar_alpha` too.
- `group_detections(detections, power_map)` — detection mask → peak cells, one per
  target (merges everything within 3 cells; the strong targets' near-sidelobe
  detections fold into their own group).

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("Hann both axes, normalize by
window energy, fftshift Doppler only, CFAR per Doppler row along range, strict
bins-to-meters via the toolkit axes"), the AI types; you verify against the planted
truth, the Parseval residual, and the 2% HERM referee. If your AI hands you a
spacing estimator, feed it a comb with every third line deleted and see what it does
— that is exactly what the noise will do.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Reference design: **B = 300 MHz, T_c = 10 µs, N = 512** (ΔR = 0.4997 m, coverage
  255.8 m, v_unamb ±97.34 m/s, Δv = 0.3802 m/s; T_c's legal window at this B is
  **[7.82, 12.98] µs**). Other choices can pass the audit.
- Map noise median **−1.58 dB** re thermal (exponential noise medians at ln 2);
  Parseval residual through the chain **0.0e+00**.
- Recovered: airliner tail (180.38 m, +0.00 m/s, 79.3 dB), car (45.47 m,
  +11.79 m/s, 39.7 dB), drone (24.98 m, +0.00 m/s, 21.2 dB) — worst error
  **0.35 range bins**, 0.04 Doppler bins. Expected false alarms per frame at
  P_fa = 10⁻⁷: 0.026.
- The window experiment, v = 0 row at the drone: leakage floor **−1.98 dB**
  (Hann) vs **+27.07 dB** (no window); CFAR threshold at the drone's cell
  **12.74 dB** vs **41.56 dB**; drone in the target list **True** vs **False**.
- HERM spacing measured **200.000 Hz** vs planted 200.0 (error 0.000%); lines
  ≥15 dB over the floor span ±35.8 kHz (tips at 35.50 kHz); with the vendor's
  n_blades = 2: f_rot = 100.0 Hz = 6000 rpm.

## References

- TI SPYY005, "The Fundamentals of Millimeter Wave Radar Sensors" (free) — [R34]
- Chen et al. 2006, "Micro-Doppler Effect in Radar" (course pack, §II) — [R24]
- Cai et al. 2019, "Simulation of Radar Micro-Doppler Patterns for Multi-Propeller
  Drones" (free author copy) — [R30]
- MIT OCW RES.LL-003, the coffee-can FMCW radar (free) — [R33]
