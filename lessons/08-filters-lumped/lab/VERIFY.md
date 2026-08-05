# Lecture 8 — instructor verification recipe

Run everything from `lessons/08-filters-lumped/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
scipy-prototypes + ABCD + skrf smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; full output is deterministic — no RNG in this lab):
- g tables: butterworth N=3 `[1. 2. 1. 1.]`; chebyshev 0.5 dB N=3
  `[1.5963 1.0967 1.5963 1.]`; N=2 load `1.9841`
- `N=1 check: recursion g1 = 0.698623, hand-derived 2*eps = 0.698623`
- g-ladder vs scipy cheb1ap response: `max |delta| = 1.42e-14 dB`
- ripple-buys-rolloff at Ω = 4.2941: chebyshev `40.52 dB`, butterworth
  `28.84 dB` (`ripple bought 11.7 dB`)
- `f0 = sqrt(55 * 65) MHz = 59.7913 MHz`, `Delta = 0.1672`; ladder rows
  `1270.279 nH / 5.5778 pF` and `20.297 nH / 349.0878 pF`, all resonating
  `59.7913 MHz`
- correct spec table: `0.5000 dB` worst passband, `52.38 dB` @35, `40.52 dB` @85
- butterworth N=4 (0.5 dB at 55/65): `57.02 dB` @35, `41.49 dB` @85
- group delay: chebyshev `68.3 / 128.5 / 108.8 ns` (f0 / 55 / 65);
  butterworth `63.9 / 99.2 / 84.0 ns`
- bug cell, both tables printed: BUG worst passband `0.9726 dB` (spec ≤ 0.5,
  **fails**), rejections `52.66` / `40.33` dB (still pass — that is the trap)
- `wrote hour3_bpf.png`, `wrote hour3_gd.png`

## 3. Starter, as the student first runs it

```
python hw8_starter.py --check
```
Expected: module 1 and module 3 print `not implemented`; module 2 prints the
mapped stop frequencies (`Omega(35 MHz) = -6.7143, Omega(85 MHz) = +4.2941`)
then `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw8_solution.py --check
MPLBACKEND=Agg python solutions/hw8_solution.py --sweep
```
Success criteria (syllabus lecture 8) against the printed facts:
- **g-values vs scipy-derived references ≤ 1e-8**: measured worst over
  N=1..8 — butterworth `7.45e-12`, chebyshev 0.5 dB `2.44e-14`, chebyshev
  3.0 dB `3.20e-14`
- classic rows reproduced: chebyshev 0.5 dB N=3 `[1.5963 1.0967 1.5963 1.]`,
  N=2 load `1.9841`
- **order answer exact**: `min order: chebyshev 0.5 dB = 3, butterworth = 4`
  (exact values 2.972 / 3.882 — one more section, Q1)
- ladder: series `1270.279 nH / 5.5778 pF`, shunt `20.297 nH / 349.0878 pF`;
  `worst branch resonance offset from sqrt(f1*f2): ~1e-16 relative`
- sweeps vs skrf referee: REF_LADDER `max |dS21| ~ 6e-18`; the design ladder
  `~ 4e-14`
- **all three spec points met, margins quoted**: worst passband attenuation
  `0.5000 dB` (margin `+0.0000` — equal-ripple, by construction); rejection
  @35 `52.38 dB` (margin `+12.38`); rejection @85 `40.52 dB` (margin `+0.52`);
  both rejections match `cheb_atten_db` analytic to `< 1e-14`
- group delay `68.3 ns` center / `128.5 ns` worst edge
- `--sweep` writes `hw8_sweep.png` (mask bars at −0.5 and −40 dB; group-delay
  panel peaking at the band edges)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw8_starter.py solutions/hw8_solution.py
```
Expected: silence.

## Cleanup

`hour3_bpf.png`, `hour3_gd.png`, and `hw8_sweep.png` are regenerable and
gitignored; delete freely.
