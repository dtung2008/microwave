# Lecture 3 — instructor verification recipe

Run everything from `lessons/03-smith-chart-matching/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / pandas / skrf
1.13.0, a `pysmithchart` line (ok or "not installed (optional)"), the
DefinedGammaZ0 cascade smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — the one RNG is seeded):
- `Gamma_L = -0.0974-0.2680j = 0.2851 @ -109.97 deg`, SWR `1.7976`, RL `10.90 dB`
- 4000 random passive impedances: max |Gamma| `0.999963` (< 1)
- rotation: |Gamma| `0.285098 (constant!)` at all three lengths; λ/4 inverter
  `51.8135+30.2245j`; v-min `27.8151` Ω at 0.0973 λ; v-max `89.8794` Ω at 0.3473 λ
- L-section sol 1: `X = 43.4499` Ω (`L = 2.8814 nH`), `B = 12.4722 mS`
  (`C = 0.8271 pF`), `y after series = 1.0000-0.6236j`; skrf `|Gamma(f0)| = 2.69e-16`
- stub sol 1 `d = 0.495274 lam ( 61.87 mm)`, `l = 0.414589 lam ( 51.79 mm)`;
  sol 2 `d = 0.199260 lam ( 24.89 mm)`, `l = 0.085411 lam ( 10.67 mm)`;
  skrf `1.78e-16` / `1.67e-16`
- band: worst in-band RL — L-section 1 `20.16 dB`, stub 1 `4.21 dB`, stub 2 `15.34 dB`
- bug cell: `z_in = 1.0000+0.5949j`, stub `l = 0.414589 lam`,
  `|Gamma(f0)| = 0.5273`, `SWR = 3.231` (worse than unmatched 0.2851)
- `wrote hour3_chart.png`, `hour3_band.png`, `hour3_bug.png`

## 3. Starter, as the student first runs it

```
python hw3_starter.py --check
```
Expected: the patient line (|Γ| 0.2851 / SWR 1.7976 / RL 10.90 dB), then each
module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw3_solution.py --check
MPLBACKEND=Agg python solutions/hw3_solution.py --smith
```
Success criteria (syllabus lecture 3) against the printed facts:
- **|Γ(f₀)| < 1e-8 in the skrf cascade for both designs** — measured:
  L-section `2.69e-16` / `2.55e-16`; stub `1.78e-16` / `1.67e-16`
  (+ short-stub variant `3.55e-16`); region-check load 120+90j
  `3.33e-16` / `7.24e-16`. Intermediate `Re(y) = 1.000000000`.
- **10-dB-RL bandwidths measured and quoted** — in-window (2.0–2.8 GHz)
  edges: stub 1 low edge `2.1870` GHz, all other edges edge-limited (the raw
  load already sits at 10.90 dB RL — by design, Q5); wide-sweep
  (0.5–4.5 GHz) true 10-dB bandwidths: stub 1 `1414.7 MHz` [2.1870, 3.6017],
  stub 2 `2187.6 MHz` [0.9327, 3.1204]; L-sections one-sided (L1 upper edge
  `3.5666` GHz, L2 lower edge `1.1570` GHz). 15-dB in-window: stub 1
  [2.2730, 2.5825]. Worst in-band RL: `20.16` / `24.32` / `4.21` /
  `15.34` dB.
- module-3 planted truth: measured edges vs closed form `err = 2.38e-07 Hz`
  (10 dB, interpolation on a 1-MHz grid) and `0.00e+00 Hz` (15 dB).
- **chart shows the trajectory through the correct intermediate point**
  (visual, human-read): open `hw3_smith.png` — both trajectories pass
  through their markers on the drawn g = 1 circle; band curves thread the
  center; RL panel shows both products above the raw-load line across
  2.0–2.8 GHz.

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw3_starter.py solutions/hw3_solution.py
```
Expected: silence.

## Cleanup

`hour3_chart.png`, `hour3_band.png`, `hour3_bug.png`, `hw3_smith.png` are
regenerable and gitignored; delete freely.
