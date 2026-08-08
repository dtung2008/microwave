# Lecture 16 — instructor verification recipe

Run everything from `lessons/16-beamforming-capstone/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root. pyargus must be installed in the venv
(`pip install pyargus` — pure Python, no pins needed; the installed wheel has no
`__version__`).

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0 /
pyargus, the pyargus DOA smoke test (peak at +20 deg), then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — all seeds fixed; ~4 s):
- array line: `N = 16, 77 GHz, d = lambda/2 = 1.9467 mm, HPBW = 6.35 deg`
- 3.2: beamscan peak `-12.00 deg`, reads `+9.91 dB`
- 3.3: two-drone peaks beamscan `['-4.82', '+4.78']`, MVDR `['-4.70', '+4.76']`;
  jammer cell: beamscan at drone `+24.86 dB`, MVDR at drone `+20.92 dB`;
  `wrote hour3_spectra.png`
- 3.4: monopulse slope `0.2195 per deg`; errors 0.014 / 0.083 / 0.208 deg
- 3.5: `fixed_wing: CPA in +1.17 s at 14.71 m -> ALERT` (truth +1.16 s, 14.60 m);
  `leaving_drone ... no alert`
- 3.6: pyargus deltas `0.000 deg` (Bartlett and Capon)
- 3.7 (the deliberate bug): K = 256 `+26.84 dB` peak +8.00; K = 8 unloaded
  `P(truth) = -114.45 dB`; K = 8 + 10 dB loading `+27.74 dB` peak +8.04;
  beamscan `+16.39 dB`; "NEGATIVE at 29% of angles"; `wrote hour3_bug.png`

## 3. Starter, as the student first runs it

```
python hw16_starter.py --check
```
Expected: header facts (HPBW 6.3480 deg), then each module prints
`not implemented`; exit code 0; no traceback; < 1 s.

## 4. Solution (grading reference)

```
python solutions/hw16_solution.py --check
MPLBACKEND=Agg python solutions/hw16_solution.py --plot
```
Success criteria (syllabus lecture 16) against the printed facts:
- **DOA vs pyargus ≤ 0.5 deg**: all six `max d` lines print `0.000 deg`
  (one_drone / two_drones / jammer × beamscan / MVDR, identical snapshots and
  grid).
- Resolution study (deterministic seeds): 1.5 BW — beamscan resolved at all
  grid SNRs (`flip at -15 dB`), MVDR `flip at -12 dB`, dips at 18 dB SNR
  `+5.73` / `+27.67 dB`; 0.7 BW — beamscan `flip at None`, MVDR `flip at 0 dB`,
  dips `-0.96` / `+14.06 dB`.
- Chain: clean-scene theta error `mean 0.050 deg, max 0.123`; jammed scene
  beamscan `mean 53.725 deg` (reads the jammer), MVDR `mean 0.035 deg`.
- **CPA error < 5 m on every tracked target**: measured |dCPA| column
  0.03 / 0.94 / 0.12 / 0.38 / 0.12 m — worst **0.94 m**.
- **Alert verdicts match the instructor truth table 5/5**, including both
  non-alerts (drone_b 60 m crossing; leaving_drone CPA in the past) and the
  jammed-scene alert (drone_j through the 40 dB jammer).
- `--check` runs in ~2 s (< 1 min budget); deterministic — two consecutive runs
  diff clean.
- `--plot` writes `hw16_plots.png` (4 panels: two-drone spectra at 0/18 dB;
  jammer spectra with the MVDR null; dip-depth vs SNR curves crossing 0; the
  corridor map with truth lines, chain dots, CPA crosses, 30 m alert circle).

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw16_starter.py solutions/hw16_solution.py
```
Expected: silence.

## Cleanup

`hour3_spectra.png`, `hour3_bug.png`, and `hw16_plots.png` are regenerable and
gitignored; delete freely.
