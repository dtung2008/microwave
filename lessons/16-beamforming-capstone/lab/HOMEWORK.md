# Homework 16 — Detect, locate, avoid (the capstone)

**Follows:** Lecture 16 (Beamforming, DOA & collision avoidance)
**Submit:** `hw16_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Homework 15's 77 GHz sensor grew up: a 16-element receive array (d = λ/2, 29 mm of
silicon-adjacent copper) now guards a corridor where drones are not allowed to fly.
The FMCW pipeline you built last week is on the job — it hands you, every quarter
second, a list of detections with range and range rate. What it cannot tell you is
*where* each echo came from, and therefore whether anything is actually on a path
that matters.

Three afternoons of traffic, all trajectories planted and known: two **crossing
drones** (one will pass 24 m from the sensor, one 60 m — only one of those is your
problem); a **fast fixed-wing intruder** boring in at 39 m/s alongside a drone that
is politely leaving; and, on the third afternoon, the same corridor with a **jammer**
parked at +25° — 40 dB stronger than the drone you must keep tracking through it.

Your job, in three moves: **DOA** — turn array snapshots into angles, with beamscan
(lecture 13's pattern used backwards) and MVDR (adaptivity in one Lagrange
multiplier), and measure when each one resolves two drones and what the jammer does
to each; **the chain** — plug your DOA into the provided (R, v) detections for full
(R, v, θ) target lists per frame; **avoid** — track each target through the
toolkit's α-β filter, compute the closest point of approach and time-to-go in
closed form, and issue alert / no-alert against the given contract (alert iff
0 < t_CPA ≤ 20 s and d_CPA < 30 m).

The referees are merciless because everything is planted: **pyargus** (an
independent DOA library) runs on your *identical* snapshots and must agree with
your spectra's peaks to 0.5°; every trajectory is a straight line, so CPA has a
**closed form** your tracked estimate must hit within 5 m; and the instructor's
**truth table** (in the file — you can read it) must be reproduced from noisy
measurements on all five targets, *including the two correct non-alerts*. A guard
sensor that alerts on everything is as useless as one that alerts on nothing —
lecture 14's false-alarm economics, now with a cockpit attached.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `sample_covariance`, `beamscan_spectrum`, `mvdr_spectrum`, `resolution_study` | **the core** — spatial spectra + the resolution question | ~70 min | 40% |
| 2 | `chain_frames` | (R, v) meets your θ | ~30 min | 20% |
| 3 | `cpa_ttc`, `alert_decision`, `avoid_study` | the geometry and the verdict | ~45 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs
(module 3's `cpa_ttc` is probed on the intruder's *true* state before your chain
ever runs), so a broken module 1 never hides module 3.

**Conventions, stated once** (they bite everyone once): θ is measured **from
broadside** (the corridor axis), element n sits at x = n·d with geometric phase
+k·d·n·sin θ — hw13's convention, and the toolkit's `steering_vector` carries it so
it can only be wrong in one place. v is the **range rate, receding positive** —
hw15's sign, unchanged. The spectra have stated normalizations (in the docstrings):
beamscan `a^H R a / N²` reads a lone source at its per-element SNR; MVDR
`N / (a^H R⁻¹ a)` reads 0 dB in noise-only directions and 1 + N·p at a lone source
— the array gain N rides in front. Use them, or the checker's dB numbers will not
match yours (the *peak angles* will still be right — which is its own lesson about
normalization conventions).

**Module-1 contract details** (the parts that save you an hour): build the spectra
on the course grid `THETA_DEG` (0.02° steps — grid quantization is invisible
against the 0.5° criterion). For MVDR use `np.linalg.solve(R, A)` on the whole
steering matrix — an explicit inverse in a loop over 9001 angles is the slow, less
accurate way to the same answer. `resolution_study` uses the classic three-point
dip test (spectrum at each true angle vs at the midpoint) — no peak-finding needed,
and it is deliberately cheap so you can afford the SNR sweep.

**Module-2 edge that bites:** in the jammed scene the jammer is a *legitimate
spectrum peak* — 40 dB stronger than the drone. `top_peaks_deg` will hand it to you
first. The contract: when `mask_deg` is given, get the jammer's bearing from the
toolkit's `jammer_bearing_deg(frames)` (it beamscans a target-free reference cell)
and refuse any peak within `mask_deg` of it. Then ask yourself Q3: why does this
mask rescue MVDR but *not* beamscan?

**Module-3 bookkeeping:** decide at the **last frame**. `cpa_ttc` on the final
track state returns time-to-go from that moment; the alert rule uses the
time-to-go; but report `t_cpa_s` from the scene's first frame (add the decision
time) so your table lines up with the closed-form referee. Handle |v| = 0
(a hovering target's CPA is *now*, at its current range).

## Running it — the two commands

```
python hw16_starter.py --check    # measured facts per module (the instrument)
python hw16_starter.py --plot     # the four pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and
the run continues. Everything is seeded — reruns reproduce exactly.

## The toolkit (provided — think in these nouns)

- `ARRAY`, `DOA_SCENES`, `TRACK_SCENES`, `ALERT`, `TRUTH_TABLE` — the array, the
  snapshot scenes, the three corridor afternoons, the alert contract, and the
  instructor's verdicts (yes, you can read them; the referee measures whether your
  *pipeline* reproduces them from noise).
- `db` / `undb`, `wavelength_m`, `hpbw_deg` — the vocabulary (HPBW = 6.35° for
  this array; the whole homework is priced in beamwidths).
- `steering_vector(arr, theta_deg)` — a(θ), hw13's phases as a column vector.
- `make_snapshots(arr, sources, n_snap, seed)` — the snapshot model x = A s + n:
  fluctuating complex-Gaussian sources (Swerling-style, lecture 14), unit noise.
- `top_peaks_deg(theta_deg, p_lin, n_peaks, min_sep_deg)` — peak picking
  (plumbing, not physics).
- `make_frames(scene_name)` — the hw15 pipeline's output: per frame, detections
  with `track_id` (association is GIVEN — real trackers spend half their code
  earning it), `r_m`, `v_m_s` (hw15 conventions), and `x_snap` for your DOA;
  jammed scenes also carry `jammer_ref` snapshots of a target-free cell.
- `jammer_bearing_deg(frames)` — the reference cell beamscanned for you.
- `alpha_beta_track(t_s, pos_xy_m)` — the α-β filter, course gains α = 0.5,
  β = 0.2 (Q4 asks you to reason about them, not tune them).
- `cpa_truth(scene, track_id)` — the closed-form CPA referee.
- The **instrument**: `_pyargus_spectra` maps pyargus onto our angle convention
  (θ_pyargus = 90° − θ; their steering uses cos from the array axis) and compares
  peak angles on identical snapshots. Read it after you finish — convention
  mapping between two libraries is half of real array work.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("R̂ = XX^H/K; beamscan
a^H R a/N²; MVDR N/(a^H R⁻¹a) with optional loading added to R̂ before the solve;
three-point dip test; mask peaks near the jammer bearing; CPA by minimizing
|p + vt|²"), the AI types; you verify against pyargus, the closed-form CPA, and the
truth table. If your AI writes the MVDR with an explicit `np.linalg.inv`, ask it
why `solve` is better — and if it cannot say, lecture 4's numerics warning applies
to it too.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Array: N = 16 at 77 GHz, d = 1.9467 mm = λ/2, **HPBW = 6.3480°**; 1.5
  beamwidths = 9.522°.
- One drone at −12°, 10 dB: beamscan peak **−12.00°** reads +9.91 dB; MVDR peak
  −12.02° reads +20.85 dB (convention 1 + N·p = 22.07 dB).
- pyargus referee: max peak delta **0.000°** on all three scenes, both methods
  (criterion 0.5°) — identical mathematics, independently coded.
- Resolution (SNR −15…18 dB, step 3): at **1.5 BW** beamscan is resolved at
  *every* grid SNR (flip −15 dB, i.e. never flips in-grid; dip +5.73 dB at
  18 dB SNR), MVDR flips at **−12 dB** (dip +27.67 dB at 18). At **0.7 BW**
  beamscan *never* resolves (dip −0.96 dB at 18); MVDR flips at **0 dB**.
- Jammer scene: beamscan's two peaks are **+25.00° and +36.98°** — the jammer and
  the jammer's first sidelobe; the drone-direction floor reads +24.86 dB. MVDR
  peaks +25.00° and **−9.96°** — the drone, at +20.92 dB.
- The chain: clean-scene θ error mean **0.050°**, max 0.123°. Jammed scene:
  beamscan chain mean error **53.7°** (it reads the jammer); MVDR (load 10 dB,
  mask 3°) mean **0.035°**.
- The capstone table: CPA errors 0.03 / 0.94 / 0.12 / 0.38 / 0.12 m (worst
  **0.94 m**, criterion 5 m); alert verdicts **5/5** against the truth table —
  drone_a ALERT (23.7 m @ 5.8 s), drone_b no-alert (60.1 m), fixed_wing ALERT
  (14.6 m @ 4.9 s), leaving_drone no-alert (CPA in the past), drone_j ALERT
  (18.0 m @ 5.0 s) *through the jammer*.

## References

- Orfanidis, *Electromagnetic Waves and Antennas*, chs. 22–23 (arrays, DOA; free)
  — [R4]
- Hasch et al. 2012, "Millimeter-Wave Technology for Automotive Radar Sensors in
  the 77 GHz Frequency Band" — [R25]
- Patole et al. 2017, "Automotive Radars: A review of signal processing
  techniques" — [R26]
- MIT Lincoln Laboratory, *Introduction to Radar Systems*, tracking lecture (free)
  — [R31]
- pyargus documentation: https://github.com/petotamas/pyArgus
