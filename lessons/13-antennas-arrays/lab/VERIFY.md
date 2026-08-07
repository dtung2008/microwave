# Lecture 13 — instructor verification recipe

Run everything from `lessons/13-antennas-arrays/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
array-factor smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; full output is deterministic — no RNG in this lab):
- uniform 16-element: `|AF|max = 16.0`, first null `7.181 deg` (formula agrees),
  `HPBW = 6.3590 deg`, `SLL = -13.1468 dB`
- `|AF(psi_k)| vs |FFT(weights, 4096)|: max difference = 4.53e-14`
- `chebwin(16, at=30): SLL = -30.0000 dB`, HPBW `7.9790 deg`, cost `x1.2548`
- steering: peaks at `+0.000 / +25.000 / +45.000 deg`, HPBW `6.3590 → 9.0260`,
  broadening `x1.419`
- grating: predicted onset `32.58 deg`; far-lobe table rises from `-19.82 dB`
  (scan 0) through `-2.41 dB` (scan 30 — the skirt pokes in early) to `-0.00 dB`;
  at scan 45: lobe at `-56.238 deg` vs formula `-56.238 deg`
- aperture sizing: `1.146 deg`, `D ~ 1.50 m`, 16-element separates only inside
  `901 m`, `12.04 dBi` vs 33 dBi tie-back, 16×16 sheet `29.05 dBi`, `~635` elements
- bug cell: `57 full-height beams, spaced 3.1416 deg` (= π on a degrees axis);
  `wrote hour3_grating.png`, `wrote hour3_bug.png`
- **no chebwin UserWarning anywhere** (filtered, with the reason in a comment)

## 3. Starter, as the student first runs it

```
python hw13_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback; the
array header line prints `N = 16, f = 10 GHz, d = 14.9896 mm = lambda/2`.

## 4. Solution (grading reference)

```
python solutions/hw13_solution.py --check
MPLBACKEND=Agg python solutions/hw13_solution.py --plot
```
Success criteria (syllabus lecture 13) against the printed facts:
- **SLL:** measured `-13.1468 dB`, delta vs the exact finite-N closed form
  `-3.78e-08 dB` (criterion: within 0.1 dB — met against the AF's own closed form;
  note the printed finite-N correction `+0.11 dB` vs the −13.26 sinc asymptote,
  which is course content, not an error)
- **Beamwidth:** `HPBW = 6.3587 deg` vs closed form `6.3480` → rel err `0.169 %`
  (criterion: within 1%); steered `9.0254` vs `9.0101` → `0.170 %`
- **Chebyshev:** `SLL -30.00 dB`, chebwin-guarantee delta `-0.000` (criterion:
  −30 ± 0.2 dB); beamwidth cost `x1.2550`; directivity cost `0.6468 dB`
- **Directivity invariant:** uniform `D = 12.0412 dBi`, delta vs 10·log₁₀N
  `+2.2e-10 dB`
- **Grating onset:** measured `-56.238 deg` vs formula, delta `0.0002 deg`
  (criterion: 0.1°); level `-0.00 dB` (full height)
- **Scene:** uniform margin `+2.69 dB` → `buried`; cheb30 margin `+12.54 dB` →
  `revealed`
- `--plot` writes `hw13_plots.png` (four panels: taper trade, two-target overlay,
  steering at λ/2, the 0.65λ grating lobe with the formula line on it)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw13_starter.py solutions/hw13_solution.py
```
Expected: silence.

## Cleanup

`hw13_plots.png`, `hour3_grating.png`, `hour3_bug.png` are regenerable and
gitignored; delete freely.
