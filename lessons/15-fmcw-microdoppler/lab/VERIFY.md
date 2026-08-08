# Lecture 15 — instructor verification recipe

Run everything from `lessons/15-fmcw-microdoppler/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root. Every RNG is seeded — all numbers below are
exactly reproducible.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy 1.13.1 / matplotlib / skrf 1.13.0,
the dechirp smoke test (`60 m target -> beat bin 120, f_b = 12.0 MHz;
scipy.signal.stft present`), then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; ~1.4 s total, fully deterministic):
- 3.2: `beat per meter ... 200.14 kHz/m`; `FFT peak at bin 120 -> f_b = 12.000 MHz
  (formula ... 12.008 MHz)`; `R = 59.958 m`
- 3.3: apparent range `60.0053 -> 60.0522 m (shift +46.8 mm; closed form +51.3 mm)`;
  worst case `250 mm = HALF a range bin`
- 3.4: peaks `30.2 dB (29.98, +0.00)`, `24.2 dB (80.44, -15.21)`,
  `19.5 dB (150.40, +30.04)`; Parseval residual `0.00e+00`
- 3.5: separations 1.0/0.6/0.5/0.4 m → rect `2/2/2/1` peaks, Hann `2/1/1/1`
- 3.6: `no window: weak cell 16.11 dB | sidelobe floor 13.67 dB | CFAR threshold
  30.24 dB -> buried`; `Hann: 17.73 | -3.41 | 13.46 -> DETECTED`
- 3.7: `v_tip = 69.1 m/s -> +/-35.5 kHz`; `HERM comb: 180 lines ... spacing =
  200.000 Hz`; `wrote hour3_microdoppler.png`

## 3. Starter, as the student first runs it

```
python hw15_starter.py --check
```
Expected: each module prints `not implemented` (modules 2–3 print nothing first —
their probe calls precede any output); exit code 0; no traceback; < 2 s.

## 4. Solution (grading reference)

```
python solutions/hw15_solution.py --check
MPLBACKEND=Agg python solutions/hw15_solution.py --map
```
Success criteria (syllabus lecture 15) against the printed facts (~2 s):
- **Waveform audit**: B = 300 MHz / T_c = 10 µs / N = 512 all four lines say
  `meets` (ΔR 0.4997 m, coverage 255.82 m, v_unamb 97.34 m/s, Δv 0.3802 m/s);
  T_c legal window `[7.82, 12.98] us`; blade check `f_tip = 35.50 kHz ...
  unaliased`.
- **All planted targets within one range and one Doppler bin**: airliner tail
  (180.20, 0.00) → (180.38, +0.00) err (+0.35, +0.00) bins; car (45.30, +11.80)
  → (45.47, +11.79) err (+0.34, −0.04); drone (25.10, 0.00) → (24.98, +0.00)
  err (−0.23, +0.00). Exactly **3 targets extracted**, no extras (expected FA
  per frame 0.026). Map noise median −1.58 dB; **Parseval residual 0.00e+00**.
  Q1's instrument line: drone column body 21.2 dB at v = +0.00; strongest
  cells away from v = 0 are the blade band edges, 11.3–11.5 dB near
  ±66–69 m/s — real blade energy, below the CFAR bar.
- **The buried-drone (window) experiment with numbers**: leakage floor −1.98 dB
  (Hann) vs **+27.07 dB** (no window); CFAR threshold at the drone's cell
  12.74 dB vs **41.56 dB**; drone in target list **True vs False**; without
  the window only 2 targets remain.
- **HERM spacing within 2%**: measured **200.000 Hz** vs planted 200.0 —
  error **0.000%**; lines ≥15 dB over floor span −35.80..+35.40 kHz
  (f_tip 35.50 kHz); implied f_rot 100.0 Hz = 6000 rpm.
- `--map` writes `hw15_map.png` (four panels: the map with three annotated
  blips; the v=0 row with the no-window sidelobe shelf and the threshold wall
  over the drone; the STFT with blade flashes touching the ±35.5 kHz guides;
  the HERM comb on the 200 Hz grid with the DC body line).

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw15_starter.py solutions/hw15_solution.py
```
Expected: silence.

## Cleanup

`hour3_microdoppler.png` and `hw15_map.png` are regenerable and gitignored;
delete freely.
