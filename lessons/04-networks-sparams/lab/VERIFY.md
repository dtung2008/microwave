# Lecture 4 — instructor verification recipe

Run everything from `lessons/04-networks-sparams/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
s2a/a2s + `**` smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — the only RNG in this lab lives in the
starter's seeded generator):
- worked two-ports: pad `|S21| = 0.500 = -6.02 dB`, power sum `0.2500`; 75 Ω λ/4
  line `|S11| = 0.3846, |S21| = 0.9231 = -0.695 dB`, power sum `1.0000`; 1:2
  transformer `S11 = -0.600, S21 = +0.800`, power sum `1.0000`
- ring_slot: reciprocity `0.00e+00`, σ_max `0.99922 .. 0.99947`, unitarity `0.0777`
- conversions vs skrf on ring_slot: `s_to_abcd vs s2a : 7.73e-15`,
  `s_to_z vs s2z : 3.97e-12`, round trip `4.45e-16`
- 3-section cascade vs skrf `**`: `6.75e-16`; chain |S21| at 1 GHz `-1.182 dB`
- invariant table: line `True / 7.02e-16 / 8.88e-16`, pad `True / 1.06e+00 / 0`,
  isolator `False / 1.00e+00 / 0`, ring_slot `True / 7.77e-02 / 0`
- bug cell: naive pads `S21 = 0.000` vs correct `0.250 = -12.04 dB`; L-section +
  line naive `-7.44 dB` vs ABCD `-0.35 dB`; `is_reciprocal(naive) = False`
  (`|S12 - S21| max = 1.651`), `is_reciprocal(right) = True`
- `wrote cascade_bug.png`

## 3. Starter, as the student first runs it

```
python hw4_starter.py --check
```
Expected: modules 1–2 print `not implemented`; module 3 prints the full referee
residual table for A/B/C with `your verdict : not implemented` per network; exit
code 0; no traceback; < 1 min (measured ~1 s).

Referee residuals in that table (deterministic, seed 20260804):
- A: `recip = 4.63e-04  unitarity = 0.4170  passivity = 0.0000`
- B: `recip = 4.52e-04  unitarity = 0.0302  passivity = 0.0000`
- C: `recip = 2.48e+00  unitarity = 5.4453  passivity = 5.3528`

## 4. Solution (grading reference)

```
python solutions/hw4_solution.py --check
MPLBACKEND=Agg python solutions/hw4_solution.py --plot
```
Success criteria (syllabus lecture 4) against the printed facts:
- conversions match skrf to 1e-10 — measured: `s_to_abcd vs s2a` **1.64e-12**,
  `s_to_z vs s2z` **8.05e-12**, round trips **6.23e-14** / **5.20e-15**
- N-section cascade matches skrf `**` to 1e-10 — measured (6 mismatched
  sections): **1.02e-15**
- invariant suite hits the planted analytic values — line unitarity **8.88e-16**
  (analytic 0), pad **1.06066** (analytic 3/(2√2) = 1.06066), pad passivity 0,
  isolator `is_reciprocal = False`, line `True`
- all three planted networks correctly classified with residuals quoted —
  A `reciprocal; passive but lossy (0.4170); claim CONFIRMED`,
  B `reciprocal; passive but lossy (0.0302); claim FALSE`,
  C `NON-reciprocal; NON-passive (5.353); claim FALSE`
- `--plot` writes `hw4_plots.png` (left: |S21| dB, B hugging 0 dB, C at +8 dB;
  right: σ_max with C far above the 1.0 ceiling, B visually ON the ceiling)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw4_starter.py solutions/hw4_solution.py
```
Expected: silence.

## Cleanup

`cascade_bug.png` and `hw4_plots.png` are regenerable and gitignored; delete freely.
