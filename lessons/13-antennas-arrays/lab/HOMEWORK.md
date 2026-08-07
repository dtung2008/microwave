# Homework 13 — The aperture

**Follows:** Lecture 13 (Antennas & arrays)
**Submit:** `hw13_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

The course radar has run on a 33 dBi dish since lecture 1. This week it grows its
replacement's first slice: a **16-element uniform linear array (ULA)** at 10 GHz,
elements every half wavelength — 24 cm of aperture that steers in microseconds
instead of swinging on a motor. Before anyone builds the full planar sheet, you must
answer the aperture questions: how wide is the beam, how loud are the sidelobes, what
does quieting them cost, and what breaks when you steer to 45°?

The scene that makes it concrete: an airliner crosses at 10 km while the drone from
homework 1 hovers 15° away at 3.5 km. Lecture 1's radar equation prices their echoes
— the drone comes back **17.8 dB weaker** — and this week's question is whether the
array's *sidelobes* let you see the weak echo next to the strong one at all.

Everything in this homework is lecture 13: the array factor (module 1 — the core,
the engine every diagnostic runs on), the taper trade (module 2 — uniform vs −30 dB
Chebyshev, priced in beamwidth and directivity), and phase steering with its two
taxes, broadening and grating lobes (module 3). Lecture 16 will feed this exact
engine with snapshots and call it beamforming.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `array_factor`, `pattern_stats` | **the core** — the AF engine + honest measurement | ~60 min | 35% |
| 2 | `taper_study` | uniform vs Chebyshev, costs measured | ~35 min | 25% |
| 3 | `steer_study` | scan to 45°: broadening + grating margin | ~35 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable — but note the design: modules 2 and 3 *call
your* `array_factor` and `pattern_stats`. That is deliberate; the AF engine is the
one routine you must own well enough to reason about without running. Get module 1
agreeing with the closed forms first and the rest is bookkeeping.

`pattern_stats` must **measure** from the sampled pattern — find the peak, walk to
the −3 dB points, hunt the sidelobes. No closed forms inside it: the closed forms
live in the checker, as referees. If your measurement and the formula agree to three
digits, you have two independent witnesses; if you *compute* the beamwidth from the
formula you have one witness wearing two hats.

Edges that bite, surfaced now:

- **Radians.** `np.sin` eats radians. Hour 3's deliberate bug fed it degrees and got
  a beautiful 57-beam lie. Every angle name in the starter says `_deg` or `_rad`.
- **Convention.** Element `n` sits at `x = n·d`; its geometric phase is
  `+k·d·n·sin(theta)`. Steering to θ₀ uses `phases_rad = -k·d·n·sin(theta0)`. The
  toolkit's scene overlay assumes this sign; flip it and the drone appears at −15°.
- **The −3 dB edges fall between grid samples.** The grid is fine (0.001°), but the
  1%-of-beamwidth accuracy target wants linear interpolation at the crossing.
- **At d = 0.65λ steered 45°, the grating lobe is as tall as the main beam.** So
  "the peak" is ambiguous — decide what "main" means (hint: the commanded angle)
  before your diagnostics report the wrong lobe as the beam.

## Running it — the two commands

```
python hw13_starter.py --check    # measured facts per module (the instrument)
python hw13_starter.py --plot    # the four pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues.

## The toolkit (provided — think in these nouns)

- `COURSE_ARRAY`, `SCENE`, `THETA_DEG` — the array, the two-target sky, and the
  0.001° pattern grid (plain dicts / arrays).
- `db(x)`, `undb(x)` — lecture 1's machinery, re-provided (power ratios).
- `wavelength_m(f_hz)` — λ = c/f.
- `integrate_pattern_dbi(theta_deg, af_abs)` — directivity by integrating your
  sampled pattern over the visible sphere (module 2's "directivity cost" referee-side
  plumbing; feed it the full grid).
- `scan_response_db(...)` — steers your beam across the two-target scene and returns
  total received power vs scan angle (module 2's overlay; plumbing, not physics).
- The **instrument**: closed-form uniform-ULA beamwidth (broadside and steered), the
  *exact finite-N* first-sidelobe level (not the −13.26 sinc asymptote — run
  `--check` and read the printout), the first-null and grating-angle formulas, and
  `chebwin`'s equal-ripple guarantee. Read them *after* you finish; they are also the
  cleanest statement of the physics in the file.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("complex weights, angles from
broadside in degrees, radians into `np.sin`, no normalization inside the engine"),
the AI types; you verify against the closed forms and the chebwin guarantee.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Uniform 16-element, d = λ/2, broadside: HPBW = **6.3587°** (closed form 6.3480°),
  SLL = **−13.15 dB** (exact finite-N −13.1468; the sinc story's −13.26 is the
  N → ∞ limit), first null **7.181°**, D = **12.0412 dBi** = 10·log₁₀(16) exactly.
- Chebyshev −30 dB (`chebwin(16, at=30)`): HPBW = **7.9800°**, SLL = **−30.00 dB**
  flat (equal ripple), D = **11.3944 dBi** — beamwidth ×**1.2550**, directivity
  −**0.65 dB**: the full price of 17 dB of sidelobe quiet.
- The scene: drone echo −17.78 dB at 15°. Uniform taper: margin **+2.69 dB** over
  the airliner's sidelobe floor — *buried*. Chebyshev: **+12.54 dB** — *revealed*.
- Steered to 45° (d = λ/2): HPBW = **9.0254°**, broadening ×**1.4194** (arcsin
  form; 1/cos 45° = 1.4142 is the small-beam approximation), worst lobe still
  −13.15 dB — no grating lobe.
- Largest no-grating spacing at 45° scan: **d_max = 17.5614 mm = 0.5858λ**.
- At d = 0.65λ steered 45°: grating lobe at **−56.238°** (formula −56.238°), at
  **full height** — 0.00 dB relative to the main beam.

## References

- Orfanidis, *Electromagnetic Waves and Antennas*, chs. 19–20 (arrays; free) — [R4]
- Steer, *Microwave and RF Design* Vol. 1 (antennas & RF link; free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 14.1–14.3 — [R1]
- Balanis, *Antenna Theory* 4e, ch. 6 (arrays; reference) — [R11]
