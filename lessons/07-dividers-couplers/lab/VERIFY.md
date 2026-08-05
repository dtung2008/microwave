# Lecture 7 — instructor verification recipe

Run everything from `lessons/07-dividers-couplers/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
Circuit smoke test (`a Wilkinson in nine lines`), then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — no RNG in this lab):
- 3.2: S(f₀) matrix with `0.-0.707107j` off the input, `-0.-0.j` isolation
- 3.3: hand vs Circuit `max|dS|` ≈ `1e-16`–`2e-16` for all three (z_arm, R) cases
- 3.4: match and isolation ≤ −20 dB over `8.20-11.80 GHz (36% fractional
  bandwidth)`; `|S21|(5 GHz) = -3.27 dB`; unitarity residual at f₀ `1.000000`;
  `wrote wilkinson_sweep.png`
- 3.5: `|S21| = -3.0103 dB, |S31| = -3.0103 dB`, phase difference `90.0 deg`;
  C/D/I rows e.g. 9.5 GHz → `3.01 / 17.56 / 20.58`, 8.0 GHz →
  `3.36 / 6.81 / 10.17` (I = C + D each row); balance ≤ 0.5 dB over
  `9.10-10.90 GHz (18%)`
- 3.6: boresight `Sigma = -3.0103 dB, Delta = -3.0103 dB`; null `psi = 90.00
  deg`, depth `-313.0 dB`; paths `0.5000` / `0.5000`, `180.000000 deg apart`;
  `wrote monopulse_psi.png`
- 3.7: report card — R = 200 column: input match `-320.00 dB` (unchanged),
  output match and isolation `-15.56 dB`

## 3. Starter, as the student first runs it

```
python hw7_starter.py --check
```
Expected: modules 1/2/3 print `not implemented`; the depth instrument
(0.100/0.200/0.300 dB) and the hybrid pedigree still print; exit code 0;
no traceback.

## 4. Solution (grading reference)

```
python solutions/hw7_solution.py --check
MPLBACKEND=Agg python solutions/hw7_solution.py --plot
```
Success criteria (syllabus lecture 7) against the printed facts:
- hand even/odd S(f₀) vs skrf-assembled model: `max|dS|` ≤ 1e-6 on all four
  (Z_line, R) cases (measured: ~1.2e-16–1.9e-16)
- corporate feed: balance spread ≤ 0.01 dB (measured `0.00e+00`); outputs all
  `-6.0206 dB`; worst output–output isolation > 30 dB at f₀ (measured
  `-320.0 dB`, float floor); match `-320.0 dB`
- invariants: reciprocal `True`, passivity residual ~1e-15, unitarity residual
  at f₀ `1.732051` = √3
- Δ-port null deeper than 60 dB at f₀ (measured `-313.0 dB` below Σ at
  ψ = 90.00°); the 180° check prints `180.000000 deg`
- depth instrument: `0.100 / 0.200 / 0.300 dB` at depths 1/2/3
- `--plot` writes `hw7_plots.png` (left: four overlapping −6.02 dB output
  curves, match and worst isolation diving at 10 GHz; right: Σ/Δ vs ψ with the
  Δ null at 90°)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw7_starter.py solutions/hw7_solution.py
```
Expected: silence.

## Cleanup

`wilkinson_sweep.png`, `monopulse_psi.png`, and `hw7_plots.png` are regenerable
and gitignored; delete freely.
