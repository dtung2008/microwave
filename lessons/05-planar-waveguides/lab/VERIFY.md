# Lecture 5 — instructor verification recipe

Run everything from `lessons/05-planar-waveguides/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, an
`ok: fdtd 0.3.5` (or a non-fatal note if absent), the MLine +
RectangularWaveguide smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — no RNG in this lab; ~5 s total,
almost all of it cell 3.5's FDTD):
- 3.2: RO4350B 50 Ω width `1.1131 mm`, eps_eff `2.7361`, lam_g `18.124 mm`;
  FR-4 `0.9302 mm` / `3.3323` / `16.423 mm`
- 3.3: worst disagreement 1–20 GHz `z0 1.73%  eps_eff 2.63%`;
  `wrote microstrip_referee.png`
- 3.4: cutoffs `6.557140 / 7.868568 / 9.487824 GHz` (skrf agrees, all digits);
  30 cm delays `1.3254 / 1.6215 / 3.1674 ns`; `wrote omega_beta.png`
- 3.5: FDTD lambda_g `39.24 mm` vs theory `39.71 mm` (1.2%); below-cutoff decay
  `100.3 Np/m` vs analytic `100.0` (0.4%); `wrote fdtd_cutoff.png`
- 3.6: `case study source: PLACEHOLDER ...` (until the real openEMS export is
  dropped in as `openems_microstrip.s2p`); |S21| at 10 GHz `-0.2433 dB` /30 mm
  → `8.110 dB/m`; phase-extracted eps_eff `2.7436`; `wrote openems_case.png`
- 3.7: bug lengths `4.0176 mm` (ε_r) vs `4.6305 mm` (ε_eff), truth `1.1526x`
  longer; bugged stub `78.1 deg` at 10 GHz, quarter-wave at `11.53 GHz`

## 3. Starter, as the student first runs it

```
python hw5_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback; <1 s.

## 4. Solution (grading reference)

```
python solutions/hw5_solution.py --check
MPLBACKEND=Agg python solutions/hw5_solution.py --sweep
```
Success criteria (syllabus lecture 5) against the printed facts:
- hand Z₀ vs skrf MLine across 1–20 GHz: worst **1.73 %** (bar 2 %); hand ε_eff
  worst **2.63 %** (bar 3 %); at 10 GHz: 0.20 % / 0.27 %
- waveguide cutoffs vs c/2a: `d = 0.000e+00 Hz`, printed to 6 decimals
  (`6.557140 / 7.868568 / 9.487824 GHz`) — exact, beyond the 4-digit bar
- group delay (numerical gradient) vs analytic dβ/dω over 9.9–10.1 GHz: worst
  **0.057 %** (bar 1 %); vs skrf |v_g| referee: **0.000 %**
- loss ranking with numbers: RO4350B microstrip **2.694 dB**/30 cm
  (1.206 + 1.488) vs WR-90 **0.0321 dB**/30 cm → waveguide, ×84; skrf referee
  prints alongside (MLine 3.135 + 4.975 dB/m — the Pozar estimate sits ~4 % and
  ~0.4 % from it; RectangularWaveguide 0.1070 dB/m, matching the hand TE₁₀
  formula to 4 digits)
- transformer: RO4350B L = **4.6305 mm** vs FR-4 **4.2080 mm**, ratio **1.1004**
  (Q1's measured answer)
- `--sweep` writes `hw5_sweep.png` (left: flat hand lines vs skrf's rising
  ε_eff/Z₀ curves; right: three ω-β curves above the light line, WR-62 nearly
  flat at the 10 GHz marker)

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw5_starter.py solutions/hw5_solution.py
```
Expected: silence.

## Cleanup

All PNGs and `PLACEHOLDER_mline.s2p` are regenerable and gitignored; delete
freely. Keep `openems_microstrip.s2p` (instructor export) if present — the repo
never ships it.
