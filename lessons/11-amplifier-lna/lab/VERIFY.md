# Lecture 11 — instructor verification recipe

Run everything from `lessons/11-amplifier-lna/lab/` with the course venv
(`../../../.venv/Scripts/python.exe` on Windows). Record measured numbers in
`performance.md` at the repo root.

**Vendor file first.** Download `PGA-103+_S2P.zip` from the Mini-Circuits
PGA-103+ page (browser; the site 403s bare `curl` — a browser User-Agent +
referer works if you must script it) and extract
`PGA-103+_5V_Plus25DegC.s2p` here. It is gitignored (`lessons/**/lab/*.s2p`)
and must never be committed. Every step below runs twice: with the file
(vendor path) and with it temporarily moved away (demo path).

## 1. Environment

```
python setup_check.py
```
Expected: `ok:` lines for numpy 1.26.4 / scipy / matplotlib / skrf 1.13.0, the
stability/circle/max_gain smoke test (`K = 1.656`), the vendor-file line
(`ok: vendor file present` or the step-0 `note:`), then **`SETUP OK`**.

## 2. Walkthrough (student's pre-class + hour-3 path)

```
python hour3_walkthrough.py
```
Vendor-path spot checks (deterministic — no RNG in this lab):
- `at f0: K = 1.0973  |Delta| = 0.5499  mu = 1.2254`
- gain zoo: `|S21|^2 = 9.685`, `MSG = 12.128`, `MAG = 10.227` dB; gap `0.54 dB`
- bands: `0.010-0.110 GHz (worst mu = 0.294)`, `15.100-16.800 GHz (0.710)`;
  `K-Delta says the same thing at every point: True`
- `Gamma_MS = 0.4130 at -160.8 deg`; cascade `= 10.2268 dB` (= MAG)
- noise: `NF at the gain match : 1.599 dB`; Γ_opt move `costs 1.433 dB`
- bug cell: passive `|Gamma_L| = 0.400` at 0.010 GHz → `|Gamma_in| = 1.0613 > 1`;
  finished amp `max |Gamma_in(f)| = 1.175 at 16.150 GHz` → reflection-amplifier line
- three PNGs written (`walkthrough_mu/circles/amp.png`)

Demo-path spot checks: band `0.200-1.600 GHz (worst mu = 0.722)`; `mu at f0 =
1.304`; `MAG = 18.001 dB`; Γ_opt move `costs 0.663 dB`; bug cell prints
`|Gamma_in| = 1.0132 > 1` at 0.650 GHz and the "matchers happen to stay
passive-side" closing line.

## 3. Starter, as the student first runs it

```
python hw11_starter.py --check
```
Expected: device line, then each module prints `not implemented` (module 3
prints the noise-model facts first — they are toolkit, not student); exit 0;
no traceback. Same with the vendor file absent, plus the `file not found …
download step 0 first` device line.

## 4. Solution (grading reference)

```
python solutions/hw11_solution.py --check
MPLBACKEND=Agg python solutions/hw11_solution.py --plot
```
Success criteria (syllabus lecture 11) against the printed facts, vendor path:
- `dK = 4.44e-16  dDelta = 3.40e-16  dmu(geometric) = 1.77e-14` — all ≤ 1e-8
  (K refereed by skrf `Network.stability`; μ by the Edwards–Sinsky
  geometric-distance path; skrf 1.13.0 has **no** μ built-in)
- `K-Delta verdict vs mu verdict: agree at 660/660 frequencies`
- circles vs skrf `stability_circle` loci: worst `8.88e-16`
- `max_gain_db vs skrf max_gain … 1.69e-14 dB`; MAG identity
  `G_T - MAG = -1.78e-15 dB`
- cascade referee `vs target = +0.00e+00 dB` (bar 0.1 dB); matcher
  losslessness ~1e-15 (hw4's `unitarity_residual`)
- frontier `G_T 10.227 -> 8.794 dB, NF 1.599 -> 0.820 dB`, `monotone? … 0
  … 0 times`
- `--plot` writes `hw11_plots.png` (audit / Γ_S plane / frontier panels)

Demo path: same residual scales; bands `0.200-1.600 GHz`; agree at 120/120;
cascade `+0.00e+00 dB`; frontier `18.001 -> 17.338 dB`, `1.059 -> 0.820 dB`.

Datasheet cross-check (vendor only, ANSWERS Q4): typ gain 11.0 dB @ 2 GHz /
8.1 dB @ 3 GHz interpolates to ≈ 9.8 dB @ 2.4 GHz; file |S21|² = 9.685 dB —
coheres. Q5 anchor numbers (`system_nf_db`, NF₂ = 6 dB): vendor 2.3756 dB
(gain end) vs 2.0446 dB (noise end); demo 1.2173 vs 1.0131 dB.

## 5. Compile gate

```
python -m py_compile setup_check.py hour3_walkthrough.py hw11_starter.py solutions/hw11_solution.py
```
Expected: silence.

## Cleanup

`walkthrough_*.png` and `hw11_plots.png` are regenerable and gitignored;
delete freely. The vendor `.s2p` stays local-only (gitignored); delete it to
re-test the demo path.
