# Homework 14 — See it through the noise

**Follows:** Lecture 14 (The radar equation & detection)
**Submit:** `hw14_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

The course radar — its budget from hw10, its aperture from hw13 — has one customer
left to satisfy: the drone. The customer's contract is finally written the honest way:
**detect the drone with P_d = 0.9 at P_fa = 10⁻⁶** — not "SNR ≥ 13 dB", which is what
lecture 1 hand-waved while promising you the real mathematics later. Later is now.

Your job, in three moves: set a threshold from the exact Rayleigh statistics and then
*measure* — with a million Monte Carlo trials — whether the noise respects it; build
the P_d machinery (Albersheim's approximation, checked against Monte Carlo and the
exact Marcum referee) and redraw lecture 1's detection-range verdicts with the honest
(P_d, P_fa) spec; then face the real world, where nobody hands you the noise floor —
implement CA-CFAR (cell-averaging constant-false-alarm-rate) detection and run it on
three provided scenes: a clean one, one with a 30 dB clutter edge, and one with two
drones flying close together. Two of those scenes contain a drone your detector will
lose. Understanding *why* is the assignment.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `rayleigh_threshold`, `monte_carlo_pfa` | the threshold, set exactly and then distrusted | ~40 min | 20% |
| 2 | `albersheim_snr_db`, `monte_carlo_pd`, `honest_ranges` | the P_d machinery; lecture 1's ranges, honest | ~50 min | 30% |
| 3 | `ca_cfar` | **the core** — the detector that survives the real world | ~55 min | 35% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs, so
a broken module 1 never hides module 3.

**The two statistical domains — read this before typing.** This homework lives in two
domains and the bug of the week lives between them. The *envelope* r (what a linear
detector outputs) is Rayleigh under noise; the *power* z = r² (square-law) is
exponential. Modules 1–2 work in amplitude; module 3's CFAR works on a power profile.
The Rayleigh exponent wants the **per-channel** noise variance σ² = (noise power)/2 —
hour 3's deliberate bug put the total noise power in the σ² slot, one factor of 2 in
an exponent, and P_fa = 10⁻⁶ silently became ~10⁻³. Your `monte_carlo_pfa` exists so
that this class of bug cannot survive in *your* code: never trust a threshold you
have not measured.

**Albersheim's approximation** (module 2 — stated here so the reference is unambiguous;
using it well is the exercise): with A = ln(0.62/P_fa) and B = ln(P_d/(1−P_d)), the
per-pulse SNR required by a linear detector, N non-coherently integrated pulses,
nonfluctuating target, is

    SNR_dB = −5·log₁₀(N) + (6.2 + 4.54/√(N + 0.44)) · log₁₀(A + 0.12·A·B + 1.7·B)

Published accuracy: ~0.2 dB for 10⁻⁷ ≤ P_fa ≤ 10⁻³, 0.1 ≤ P_d ≤ 0.9, 1 ≤ N ≤ 8096.
The checker measures where that envelope holds and where its corners fray.

**CA-CFAR contract** (module 3): `ca_cfar(power_profile, n_train, n_guard, pfa)` →
`(detections, threshold)`, both arrays the length of the profile; `n_train` and
`n_guard` are counted *per side*. The threshold multiplier for N training cells is
α = N·(P_fa^(−1/N) − 1) — derive it from "the training sum is the statistic" or take
it from the hour-2 slide, but know which N it wants (the *total* training count, both
sides). Two edges that bite: at the array ends, truncate the window to the cells that
exist and recompute α for the actual count; and compare with strict `>` so a
threshold tied exactly to a cell does not fire. Lecture 15 imports this exact
interface for the range-Doppler map — build it to be reused.

## Running it — the two commands

```
python hw14_starter.py --check    # measured facts per module (the instrument)
python hw14_starter.py --plot     # the four pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues. Everything is seeded — reruns reproduce exactly.

## The toolkit (provided — think in these nouns)

- `COURSE_RADAR`, `TARGETS`, `DETECTION`, `CFAR` — the systems and the spec (mirrors
  hw1's radar and targets verbatim).
- `db` / `undb`, `wavelength_m`, `noise_floor_w` — lecture 1's machinery, re-provided.
- `radar_snr_db`, `radar_max_range_m` — hw1's module 2, now plumbing (the inverse
  accepts an `snr_req_db` override — that is where your honest bar goes).
- `marcum_pd(snr_db, pfa)`, `snr_required_exact_db(pd, pfa)` — the **exact** referee
  (Marcum Q via scipy's noncentral χ²). It checks your Monte Carlo and Albersheim; it
  never plays for you.
- `cfar_alpha`, `cfar_loss_db` — the closed-form CFAR multiplier and its price.
- `make_scene(name)` — the three scenes with planted ground truth (`"clean"`,
  `"clutter_edge"`, `"two_drones"`, plus `"two_drones_solo"`, the masking experiment's
  control arm: same noise seed, strong drone deleted).
- `binom_3sigma(p, n)` — the error bar every Monte Carlo number should wear.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("amplitude threshold from the
Rayleigh inverse, per-channel variance, strict comparison; CFAR truncates at edges
and recomputes α"), the AI types; you verify against the Monte Carlo, the Marcum
referee, and the planted scenes. If your AI writes a threshold formula, make it tell
you which σ² it used — then measure anyway.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- T(P_fa = 10⁻⁶, unit noise power) = **3.7169** — 11.40 dB above the mean noise
  power. Measured over 10⁶ trials: 0–4 crossings (the expected count is 1).
- At design 10⁻³ the same machinery measures **9.74e-4** (974 of 10⁶) — inside 3σ.
- Albersheim (P_d = 0.9, P_fa = 10⁻⁶) = **13.11 dB**; the exact answer is
  **13.18 dB**. Lecture 1's 13 dB bar was nearly honest — at exactly 13 dB the real
  P_d is **0.8744**.
- Honest ranges (P_d = 0.9, P_fa = 10⁻⁶): airliner **32.44 km**, fighter
  **12.90 km**, drone **4.08 km** — ×0.9934 of lecture 1's values.
- α(N = 16, P_fa = 10⁻⁶) = **21.94** (13.41 dB); CFAR loss **2.01 dB** (N = 32:
  **0.97 dB**).
- Clutter-edge ensemble at design 10⁻³: edge-zone P_fa ≈ **1.3e-2** (13× design),
  clear and deep-clutter zones on-design; false alarms per edge crossed **0.134**
  (n_train = 8/side) → **0.225** (16/side).
- Masking: the 15 dB drone at cell 1006 is detected alone, lost next to the 22 dB
  drone at cell 1000.

## References

- MIT Lincoln Laboratory, *Introduction to Radar Systems*, lectures 2 and 6
  (detection + CFAR, free) — [R31]
- Richards, *Fundamentals of Radar Signal Processing*, chs. 6–7 (the CFAR
  mathematics, reference) — [R14]
- *Principles of Modern Radar* Vol. I, detection chapters (reference) — [R13]
- Skolnik, *Introduction to Radar Systems*, ch. 2 (reference) — [R12]
