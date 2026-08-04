# Lecture 1 — instructor verification recipe

Run everything from `lessons/01-systems-panorama/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / pandas / skrf 1.13.0,
the smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; full output is deterministic — no RNG in this lab):
- `kT0 per Hz = -173.98 dBm/Hz`; 1 MHz noise floor `-113.98 dBm`
- Friis two ways at 50 m: `-46.03 dBm`, SNR `47.93 dB`, watts-chain agreement `0.0e+00 dB`
- Three targets: airliner `32.65 km`, fighter `12.98 km`, drone `4.11 km`
- `10 -> 20 km: SNR falls 12.04 dB`
- 400 km factor: `22,524x`
- `wrote ring_slot.png`; Freespace `|S21| = [0. 0. 0. 0. 0.] dB`
- Bug cell: honest `4.11 km` vs slipped `23.09 km` (`x5.62`)

## 3. Starter, as the student first runs it

```
python hw1_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw1_solution.py --check
MPLBACKEND=Agg python solutions/hw1_solution.py --plot
```
Success criteria (syllabus lecture 1) against the printed facts:
- every `vs watts referee` delta ≤ 1e-6 dB (measured: ~1e-14–1e-15)
- round trip: `R_max(sigma=1) = 12.98 km; SNR there = 13.0000 dB`
- `sigma x2 -> range x1.1892` (2^(1/4) = 1.1892)
- targets: airliner `32.65 km`, fighter `12.98 km`, drone `4.11 km`;
  airliner/drone ratio `7.953` = (4000)^(1/4)
- `--plot` writes `hw1_plots.png` (two panels; verticals at the three ranges;
  +1/4 guide parallel to the range curve)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw1_starter.py solutions/hw1_solution.py
```
Expected: silence.

## Cleanup

`ring_slot.png` and `hw1_plots.png` are regenerable and gitignored; delete freely.
