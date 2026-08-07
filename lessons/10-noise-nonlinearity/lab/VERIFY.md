# Lecture 10 — instructor verification recipe

Run everything from `lessons/10-noise-nonlinearity/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
Friis smoke test (2.0000 dB), the two-tone smoke test, then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Expected (spot checks; fully deterministic — no RNG in this lab):
- `kT0 per Hz = -173.98 dBm/Hz`; 1 MHz floor `-113.98 dBm`
- NF↔Te table: 1.5 dB → 119.6 K; 3.0 dB → 288.6 K (the fine-print row)
- Y-factor: ENR 15 dB → `Y = 23.3872 (13.69 dB)` → `NF = 1.5000 dB`
- Three front-ends: mast `NF = 2.3387`, shack `4.0377`, filter-first `5.3792`;
  cable move saves `1.70 dB`; war story `3.04 dB thrown away`
- Two-tone: IM3 slope `3.0000`, extrapolated intercept `-5.0013 dBm`
  (planted −5); gaps 79.997 / 69.992 / 59.974 / 49.917 dB down the 5 dB steps
- SFDR at B = 1 kHz / 1 MHz / 100 MHz: `89.51 / 69.51 / 56.17 dB`;
  `P_in,max = -42.13 dBm`
- Bug cell: mast bugged `1.6470` vs true `2.3387` (both plausible); sharp
  invariant: true `2.0000` dB vs bugged `0.5411` dB
- Stakes: drone `4.106 / 4.339 / 2.066 km` for NF 3.0 / 2.0378 / 14.9267
- `wrote two_tone.png`

## 3. Starter, as the student first runs it

```
python hw10_starter.py --check
```
Expected: each module prints `not implemented`; exit code 0; no traceback.

## 4. Solution (grading reference)

```
python solutions/hw10_solution.py --check
MPLBACKEND=Agg python solutions/hw10_solution.py --plot
```
Success criteria (syllabus lecture 10) against the printed facts:

- **Cascade engine vs hand-worked chains to 0.01 dB NF / 0.1 dB IIP3:**
  every `d = ` on the three reference chains ≤ 0.01 / 0.1 in magnitude
  (measured: 0.0000 dB NF, 0.0000 dBm IIP3 — the hand values in `HAND_WORKED`
  are worked to 4 decimals in `solutions/ANSWERS-key.md`).
  Warm-up chain exact: `NF = 3.5000`, `IIP3 = -3.0000`.
- **Friis limit cases:** single LNA = the element (1.5000 / −5.0000);
  lossy-first invariant prints `adds 2.0000 dB`; 40 dB first stage → later
  stages add `0.0040 dB`.
- **Two-tone referee:** spur slope `3.0000`; extrapolated IIP3 within 0.01 dB
  of the cascade's `-7.3767 dBm` (measured d = `-0.0023`).
- **Ordering verdicts match the instructor table:**
  #1 by MDS `lna>bpf>mixer>ifamp>cable` (NF 2.0378, MDS −111.9374);
  #20 `cable>bpf>mixer>ifamp>lna` / `bpf>cable>...` tie (NF 14.9267);
  best by SFDR `lna>cable>bpf>mixer>ifamp` (69.5065 dB) and it is NOT the
  best-MDS chain (`same chain as best MDS? False`);
  the 'obvious' chain flagged at rank 9; gain spread `0.00e+00 dB`.
- **Detection-range delta through the lecture-1 engine:** best `4.339 km`,
  worst `2.066 km`, ratio `2.1000` = closed form `10^(dNF/40)`;
  spec inversion `NF <= 2.1966 dB`, round trip `4.3000 km`, `1 of 20` clears.
- `--plot` writes `hw10_plots.png` (left: 20-point map, best/worst/'obvious'
  annotated; right: SFDR staircase with slope-1/slope-3 lines, floor at
  −111.6 dBm, SFDR bar 69.5 dB).

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw10_starter.py solutions/hw10_solution.py
```
Expected: silence.

## Cleanup

`two_tone.png` and `hw10_plots.png` are regenerable and gitignored; delete freely.
