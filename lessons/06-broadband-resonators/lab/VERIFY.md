# Lecture 6 — instructor verification recipe

Run everything from `lessons/06-broadband-resonators/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the two
smoke tests (media cascade; `Qfactor` fitting a planted Q_L = 250 to < 1%), then
**`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — the only RNG in this lab lives in
`hw6_starter.resonator_dataset` with fixed crc32 seeds):
- single λ/4 section: worst in-band RL `9.09 dB`, 20-dB fractional BW `17.1%`
- Chebyshev table: theory RL N=1..4 = `9.20 / 20.09 / 31.48 / 42.92 dB`,
  N=3 sections `[40.4, 25., 15.47]`
- theory-vs-exact table: swept worst RL `9.09 / 18.98 / 29.44 / 39.22 dB`
  (gaps `+0.11 / +1.10 / +2.04 / +3.70 dB`) — N=2 **misses** the spec
- skrf cascade referee (N=3): max |Γ| delta `~1e-15`
- Bode–Fano: `2.2 pF → 78.96 dB feasible`, `10 pF → 17.37 dB IMPOSSIBLE`,
  largest physical C `8.686 pF`
- resonator cell: 3-dB `Q_L = 250.0`; skrf Qfactor `Q_L = 250.0, Q_0 = 500.0`
- bug cell: `Q_u = 250.0 / (1 - 0.50) = 500.0`, `x2.00` (and `x25` foreshadowed)
- `wrote hour3_lecture6.png`

## 3. Starter, as the student first runs it

```
python hw6_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw6_solution.py --check
MPLBACKEND=Agg python solutions/hw6_solution.py --sweep
```
Success criteria (syllabus lecture 6) against the printed facts:
- **Bode–Fano verdicts:** ideal_pad `no ceiling`; revised_pad (2.2 pF) ceiling
  `78.96 dB` FEASIBLE; first_board (10 pF) ceiling `17.37 dB` IMPOSSIBLE;
  largest physical C `8.686 pF`.
- **Minimum N stated and verified:** `minimum N by THEORY = 2` but its exact sweep
  prints `18.98 dB ... MISSES`; `minimum N by EXACT SWEEP = 3` (29.44 dB). The
  N=3 sections are `[40.397, 25.0, 15.472] Ω`; step-sum invariant `−1.386294`
  equals ln(12.5/50).
- **Worst in-band RL vs Chebyshev theory:** gaps `+0.11 / +1.10 / +2.04 / +3.70 dB`
  for N=1..4. ⚠ NOTE: the syllabus criterion "within 0.5 dB of the Chebyshev
  theory value" is **physically unattainable at this 4:1 ratio for N ≥ 2** — the
  measured small-reflection error is the homework's Q4. The enforced numerical
  criterion is instead: hand cascade vs skrf referee `max |Γ| delta ≤ 1e-12`
  (measured `~9e-16`), with the theory-vs-exact gap quoted and reconciled.
- **Q extractions within 2% of `Qfactor` fits:** measured deltas
  A `+0.19% / +0.22%`, B `−0.02% / −0.02%`, C `+0.06% / +1.05%` (Q_L / Q_u).
- **Coupling trap caught:** `C_cavity Q_u / Q_L = 25.5x` printed.
- `--sweep` writes `hw6_sweep.png` (left: N=1..4 exact RL curves, N=2 dipping
  below the 20 dB line inside the shaded octave; right: three resonators on a
  common Q_L axis, C peaking near 0 dB).

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw6_starter.py solutions/hw6_solution.py
```
Expected: silence.

## 6. Determinism spot-check

Run `python solutions/hw6_solution.py --check` twice; outputs must be identical
(dataset seeds are crc32 of the resonator names, not Python's randomized `hash`).

## Cleanup

`hour3_lecture6.png` and `hw6_sweep.png` are regenerable; delete freely.
