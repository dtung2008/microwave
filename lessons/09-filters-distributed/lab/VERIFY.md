# Lecture 9 — instructor verification recipe

Run everything from `lessons/09-filters-distributed/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

Note on the case study: openEMS is **not installed on this machine** (course
policy: instructor-demo only, and no export has been produced yet). All
case-study numbers below are therefore from the LOUDLY-LABELED placeholder
(`PLACEHOLDER_coupled_bpf.s2p`: ideal model + documented ε_eff perturbation —
mode split ±3%, dispersion ×1.02) and are tagged `[PLACEHOLDER numbers]` in the
checker output itself. When a real `openems_coupled_bpf.s2p` is dropped into
`lab/`, rerun steps 2 and 4 and update the recorded deltas; the code path is
identical (lecture 5 precedent).

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
DefinedGammaZ0(γ explicit) + coupled-Z→S + brentq smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — no RNG in this lab; ~1.3 s):
- 3.2: the Richards table — Ω(3 GHz) = 1, Ω(6 GHz) → 3.5e+15 (numerical ∞),
  Ω(9 GHz) = −1, Ω(12 GHz) ≈ 0
- 3.3: g = [1.5963, 1.0967, 1.5963]; Kuroda'd elements
  `sh=81.32 ln=129.81 sh=45.59 ln=129.81 sh=81.32`, λ/8 = 12.49 mm;
  `|S21| at 3 GHz = -0.500000 dB`; closed-form max |Δ| `2.84e-14 dB`;
  Kuroda vs series form `7.8e-16`; `wrote hour3_stub.png`
- 3.4: stepped lengths `[23.87 45.84 23.87] deg`; 3-dB point `3.049 GHz`
  (ideal-line) / `3.112 GHz` (MLine physics); at 6 GHz `13.13 dB` vs true
  butterworth `18.13 dB`; widths `0.1784 mm` (120 Ω) / `4.0407 mm` (20 Ω);
  physical lengths `4.290 / 7.269 / 4.290 mm`; `wrote hour3_stepped.png`
- 3.5: J·Z0 `0.3137 / 0.1187`; Z0e/Z0o `70.6048/39.2355`, `56.6407/44.7687`;
  `IL at f0 = 0.0000 dB`; worst design-band atten `0.5659 dB`; 0.5-dB band
  `2.282-2.518 GHz = 9.83%`; dims `0.9307/0.0874/19.036` and
  `1.1522/0.4567/18.885` mm
- 3.6: `case study source: PLACEHOLDER ...`; center `2.4000 -> 2.3740 GHz`;
  |S21| at 2.4 GHz `-0.000 -> -0.285 dB`; near-2f₀ `-77.2 -> -0.3 dB`;
  `wrote hour3_case.png`
- 3.7: BUG sweep worst rejection above 3.2 GHz `52.8 dB` ("ship it"), honest
  sweep `0.0 dB at 7.20 GHz`; `wrote hour3_bug.png`

## 3. Starter, as the student first runs it

```
python hw9_starter.py --check
```
Expected: the `[toolkit]` g-engine validation prints (worst `7.45e-12`), then
each module prints `not implemented`; exit code 0; no traceback; < 5 s.

## 4. Solution (grading reference)

```
python solutions/hw9_solution.py --check
MPLBACKEND=Agg python solutions/hw9_solution.py --sweep
```
Success criteria (syllabus lecture 9) against the printed facts:
- **stub lowpass exact at f₀ (|S21| dB within 0.01 of theory)**: measured
  `|S21| at f_c = -0.500000 dB` vs theory −0.5000 — delta < 1e-6 dB; whole-sweep
  closed-form agreement `2.84e-14 dB`; skrf referee `1.23e-09`; Kuroda
  equivalence `6.66e-16`; second passband `9.0000 - 15.0000 GHz`
- module 2 chain: Z0e/Z0o table matches Pozar Ex 8.8 to `4.82e-05 Ω` (the
  printed-table rounding); dimension round trip `~1e-15`; dims as in step 2
- **coupled-line BPF meets ripple/BW spec in the ideal sweep**: IL(f₀)
  `0.0000 dB`; 0.5-dB ripple bandwidth `9.8333%` vs 10% designed (the
  narrowband-mapping fee, −0.17 points, is itself course content — quoted and
  reconciled in Q4); worst design-band attenuation `0.5659 dB` (overshoot
  isolated to the geometric-far edge at 2.28 GHz); atten at 2f₀ `389.3 dB`
- **reentrant passband located within 1%**: REF filter (2.0 GHz)
  `6.0000 GHz, error 0.000%`; design `7.2000 GHz, error 0.000%`, |S21| there
  `-0.00 dB`
- **ideal-vs-EM deltas quoted from the case study** `[PLACEHOLDER numbers]`:
  center `2.4000 -> 2.3740 GHz (-26.0 MHz = -1.08%)`; |S21| at 2.4 GHz
  `-0.000 -> -0.285 dB`; worst near-2f₀ `-77.1 -> -0.3 dB`
- sweeps vs skrf referee: REF `max |dS21| = 5.58e-13` (|dS11| `3.80e-09` —
  renormalize numerics); design `5.58e-13`
- `--sweep` writes `hw9_sweep.png` (left: BPF whole-life with placeholder
  overlay, design band shaded, reentrant marked at 7.20 GHz, 2f₀ zero notch;
  right: stub LPF riding the mapped-Chebyshev dots, pole at 6 GHz, second
  passband from 9 GHz)

Runtimes on this machine: `--check` 2.8 s, `--sweep` ~3 s — both far under the
1-minute budget.

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw9_starter.py solutions/hw9_solution.py
```
Expected: silence.

## Cleanup

All PNGs and `PLACEHOLDER_coupled_bpf.s2p` are regenerable and gitignored;
delete freely. Keep `openems_coupled_bpf.s2p` (instructor export) if present —
the repo never ships it.
