# Lecture 2 — instructor verification recipe

Run everything from `lessons/02-transmission-lines/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / pandas / skrf 1.13.0,
the `DistributedCircuit / DefinedGammaZ0` smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; full output is deterministic — no RNG in this lab):
- `Z0 = 50.0001-0.0589j ohm`; `gamma = 0.1112+75.3983j /m -> alpha = 0.9663 dB/m,
  vp = 2e+08 m/s`; `lambda = 83.33 mm; a 10 m feed is 120.0 wavelengths`
- antenna: `|Gamma| = 0.2851 at -110.0 deg -> SWR = 1.798, RL = 10.90 dB`;
  `mismatch loss = 0.368 dB`
- referee: `gamma vs skrf: 0.0`, `z0 vs skrf: 0.0`;
  `z_in(10 m) two ways, max rel err: 5.448e-16`
- the lie previewed: `RL at the antenna: 10.90 dB; at the far end of 10 m: 30.09 dB`
- standing waves: `pattern max/min = 1.2851/0.7149 -> ratio 1.7976`;
  `first minimum at 0.0976 lambda from the load (8.13 mm)`; `wrote standing_wave.png`
- bounce: `one-way delay 50 ns; launch 0.6667 V; Gamma_s = -0.333, Gamma_L = +0.500;
  final DC 0.8571 V`; staircase `1.0000 -> 0.8333 -> 0.8611 -> 0.8565`;
  `overshoot +16.7%`; `wrote bounce.png`
- bug cell: `spacer 8.106 mm -> plane 27.815 ohm, Z_T = 37.293 ohm`; lossless
  `lambda/4 = 7.2e-17, 3lambda/4 = 2.7e-17`; with loss `RL 55.79 dB` / `51.97 dB`;
  20-dB-RL bands `576.8 MHz (2.112-2.688 GHz)` vs `275.6 MHz (2.262-2.538 GHz)`

## 3. Starter, as the student first runs it

```
python hw2_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw2_solution.py --check
MPLBACKEND=Agg python solutions/hw2_solution.py --sweep
```
Success criteria (syllabus lecture 2) against the printed facts:
- **Z_in matches skrf to 1e-6 relative across the sweep** — measured:
  `z_in(10 m) vs skrf referee across the sweep: max rel err = 5.45e-16`
  (and `gamma rel err = 0.00e+00, z0 rel err = 0.00e+00` vs `DistributedCircuit`)
- **lossless energy conservation |Γ|² + delivered = 1 ± 1e-12** — measured:
  `lossless line: |Gamma|^2 + delivered - 1 = 0.00e+00`
- **λ/4 transformer |Γ(f₀)| < 1e-10 by construction** — measured: `7.16e-17`
  (skrf `DefinedGammaZ0` rebuild says `4.22e-17`; sweep agreement `8.56e-16`)
- **10-dB-RL bandwidth measured and quoted** — `1.2337-3.5663 GHz = 2332.5 MHz`
  (97.2% of f₀); also 20-dB: `2.1115-2.6885 GHz = 577.0 MHz` (24.0%)
- ledger at f₀: `delivered 99.3 mW, reflected 0.95 mW, heat 899.7 mW (sum =
  1.000000000000)`; `line loss (one way) = 9.66 dB, mismatch loss = 0.37 dB`;
  THE LIE line: `10.90 dB` at the antenna vs `30.09 dB` at the transmitter
- fix geometry: `spacer = 8.1056 mm = 0.0973 lambda`, plane `27.8151 ohm`,
  `Z_T = 37.2928 ohm`, `ell_T = 20.8333 mm`
- `--sweep` writes `hw2_sweep.png` (two panels: three measurement planes with the
  fix curve threading 10-dB; delivered-power curves under the line-loss ceiling)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw2_starter.py solutions/hw2_solution.py
```
Expected: silence.

## Cleanup

`standing_wave.png`, `bounce.png`, and `hw2_sweep.png` are regenerable and
gitignored; delete freely. Delete `__pycache__/` dirs likewise.
