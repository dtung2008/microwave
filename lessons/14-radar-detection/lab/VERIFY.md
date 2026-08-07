# Lecture 14 — instructor verification recipe

Run everything from `lessons/14-radar-detection/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root. Every RNG is seeded — all numbers below are
exactly reproducible.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
detection smoke test (`measured pfa 9.95e-03 at design 1e-2; Marcum(0) = Rayleigh`),
then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; ~1.3 s total):
- `mean envelope power <r^2> = 0.9998`; `<r> = 0.8859` (Rayleigh √π/2 = 0.8862);
  `wrote hw14_rayleigh.png`
- pfa 1e-3: `T = 2.6283 (8.39 dB...) measured 1.05e-03 (1051 of 1e6...)`;
  pfa 1e-6: `T = 3.7169 (11.40 dB...) measured 2.00e-06 (2 of 1e6...)`
- 1e7-trial chunked run: `8 crossings -> measured pfa = 8.0e-07`
- P_d table 6–16 dB (e.g. `12 dB: 0.6824 | 0.6794`); `(pd=0.9, pfa=1e-6):
  Albersheim 13.11 dB, exact 13.18 dB`; `wrote hw14_pd_sweep.png`
- N=10: `Albersheim 4.99 dB ... exact 5.27 dB (0.28 dB slip)`; `Gamma threshold
  T = 32.71; measured P_d ... = 0.851`; scoreboard `13.18 / 3.18 / 5.27`;
  range `x1.78` coherent, `x1.58` non-coherent
- `alpha(N=16, pfa=1e-6) = 21.94 (13.41 dB) ... CFAR loss 2.01 dB`
- scenes: clean `hits [400, 1400]`, clutter_edge `hits [1500] misses [995]`,
  two_drones `hits [1000] misses [1006]`, all `false alarms []`;
  `wrote hw14_cfar_scenes.png`; masking control `detected = True`
- bug cell: honest `measured pfa = 2.0e-06` vs bugged `T = 2.6283: measured
  pfa = 1.1e-03`; `~1,051 false alarms per second`

## 3. Starter, as the student first runs it

```
python hw14_starter.py --check
```
Expected: each module prints `not implemented` (module 3 first prints nothing —
its probe call precedes any output); exit code 0; no traceback; < 1 s.

## 4. Solution (grading reference)

```
python solutions/hw14_solution.py --check
MPLBACKEND=Agg python solutions/hw14_solution.py --plot
```
Success criteria (syllabus lecture 14) against the printed facts (~0.5 s):
- **P_fa within 3σ binomial of 10⁻⁶ at 10⁶ trials**: threshold `3.716922`
  (`d = +0.00e+00` vs exact); design 1e-2 → `1.00e-02 (10038)`, 1e-3 →
  `9.74e-04 (974)`, 1e-6 → `0.00e+00 (0 of 1e6)` — all lines say `inside`
  (3σ at 1e-6 is ±3.0e-6; expected count 1).
- **Monte Carlo P_d within 0.5 dB of Albersheim across 6–16 dB**: worst
  |ΔP_d| vs exact = `0.0021` (2e5 trials/pt); worst horizontal gap vs
  Albersheim inside its envelope = **0.16 dB**. Albersheim vs exact table:
  (0.9,1e-6) d = −0.069 dB; (0.5,1e-6) −0.011; (0.9,1e-3) −0.036;
  (0.1,1e-7) −0.753 dB flagged as the envelope's frayed corner.
- **Honest ranges**: bar `13.11 dB`; airliner `32.44 km`, fighter `12.90 km`,
  drone `4.08 km` (each ×0.9934 of lecture 1); P_d at exactly 13 dB `0.8744`.
- **CFAR reproduces on all three scenes, masking demonstrated**:
  α(16, 1e-6) = `21.942`, CFAR loss `2.01 dB` (N=32 `0.97`); measured CFAR
  P_fa on 2e5 pure-noise cells at design 1e-3 = `9.90e-04 (198)`; mean
  threshold/noise `8.63` vs α `8.64`. Scenes: clean hits `[400, 1400]` 0 FA;
  clutter_edge hits `[1500]`, **misses `[995]`** (edge masking), 0 FA;
  two_drones hits `[1000]`, **misses `[1006]`**, and the control arm prints
  `alone -> detected = True; next to the 22 dB drone -> detected = False`.
- **Edge ensemble (Q2's instrument)**: n_train 8/side → zones clear `1.0e-03`,
  edge `1.3e-02`, deep clutter `9.2e-04`, blind `0.0e+00`; FAs/edge `0.134`,
  loss `0.97 dB`. n_train 16/side → edge `1.3e-02`, FAs/edge `0.225`, loss
  `0.48 dB`.
- `--plot` writes `hw14_plots.png` (four panels: P_d curves with MC dots on
  the exact curve; honest-vs-13 dB range cliffs; clutter-edge scene with the
  masked 15 dB target under the threshold wall; two-drones scene with the
  masking hump).

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw14_starter.py solutions/hw14_solution.py
```
Expected: silence.

## Cleanup

`hw14_rayleigh.png`, `hw14_pd_sweep.png`, `hw14_cfar_scenes.png`, and
`hw14_plots.png` are regenerable and gitignored; delete freely.
