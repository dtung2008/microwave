# Lecture 12 — instructor verification recipe

Run everything from `lessons/12-mixers-receivers/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
mixer smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — fixed seed 1212 in cell 3.8):
- Cell 3.2: lines at 270/1330 Hz, amp `0.5000` each, next bin `1.49e-14`;
  conversion `-6.02 dB`
- Cell 3.3: amp `0.6367` at 270 Hz; conversion `-3.92 dB` (theory `-3.92`);
  aliased 5·LO sum at `3662 Hz`
- Cell 3.4: IF-bin amps `0.5000` / `0.2500` / `0.7500`
- Cell 3.5: `24/24` predicted products in exact bins; (2,2) `-31.9 dBc`,
  (3,3) `-62.8 dBc`, 4·f_LO `-41.8 dBc`; writes `mixer_grid.png`
- Cell 3.6: low-side plan — zone 6 fits `True`, image band `9.3572-9.7572 GHz`
- Cell 3.7: COLLISION lines for marine radars and the airfield radar; the tune
  `10.2428 GHz`; high-side flip → image `10.6428-11.0428 GHz`, collisions 0
- Cell 3.8: jitter `3.13 deg RMS`; measured `L(100 Hz) = -70.6` (profile −70),
  `L(1000 Hz) = -90.5` (profile −90); drone 1 m/s `2.5 dB -> BURIED`,
  3 m/s `14.4 dB -> visible`
- Cell 3.9: beat measured `100.0 Hz` vs planted `100.0`; `2668.5 Hz` per meter;
  3 km → `8.01 MHz`; ADC reach `18.74 km`

Runtime ≈ 1 s.

## 3. Starter, as the student first runs it

```
python hw12_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw12_solution.py --check
MPLBACKEND=Agg python solutions/hw12_solution.py --plot
```
Success criteria (syllabus lecture 12) against the printed facts:
- **Spur/image table matches closed form exactly to order 3**: `24` products,
  `max |df| = 0.000e+00 Hz`; FFT referee `24/24` peaks in exact bins
- Image bands at IF = 321.4 MHz: low `9.3572-9.7572 GHz`,
  high `10.6428-11.0428 GHz`
- **Chosen plan passes the interference audit**: BUG (low-side) → `2` fatal
  image collisions (marine radars at tune 10.0000; airfield radar at tune
  10.2330), feasible `False`; REF (high-side) → `0` fatal, 2 higher-order notes
  ((2,2)/(3,3) of police/amateur), feasible `True`
- Feasibility scan: low-side `none` (0/118); high-side `277.5-392.5 MHz`
  (39/118 grid points)
- Filter specs: preselector `n = 7` (n_exact 6.12, 60 dB at 10.6428 GHz);
  IF filter `n = 4` (n_exact 3.99, 60 dB at 300 MHz)
- **Minimum detectable Doppler within 5% of the analytic bound**: measured
  `2.566 m/s` vs analytic `2.542 m/s` (crossing 173.0 Hz) → error `0.94 %`
- `--plot` writes `hw12_plots.png` (left: low-side row entirely red, high-side
  green windows with slivers of red at the 300/350 MHz zone edges, 321.4 marked;
  right: measured PSD hugging the design skirt, comb lines, threshold at −13 dB,
  v_min marker near 173 Hz)

Runtime: `--check` ≈ 6 s, `--plot` ≈ 6 s.

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw12_starter.py solutions/hw12_solution.py
```
Expected: silence.

## Cleanup

`mixer_grid.png` and `hw12_plots.png` are regenerable and gitignored; delete
freely.
