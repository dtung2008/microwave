# Performance ledger — verification runs

Source of truth for every number quoted in scripts, HOMEWORK.md, and VERIFY.md.
Numbers are measured on the reference machine (Windows 11, Python 3.12.10, repo venv),
never invented. Format inherited from `../optimizations/performance.md`.

## Environment (installed 2026-08-04)

numpy 1.26.4 (pinned) · scipy 1.13.1 · matplotlib 3.10.9 · pandas 3.0.5 ·
scikit-rf 1.13.0 (pinned — **not** 2.0.x: 2.0.0/2.0.1 crash on plain `import skrf`
under numpy 1.26.4, `np.typing.NDArray` at import time; verified on this machine,
survey.md §3.6 risk 0).

## Lecture 1 — Microwave systems panorama (verified 2026-08-04)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | prints `SETUP OK` | `SETUP OK` | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic, all cells run | full output, no errors; `ring_slot.png` written | 1.1 s |
| starter | `python hw1_starter.py --check` | unimplemented → "not implemented", exit 0 | as specified, exit 0 | 0.15 s |
| solution | `python solutions/hw1_solution.py --check` | dB engine vs watts referee ≤ 1e-6 dB | worst delta **1.42e-14 dB** | 0.13 s |
| solution | same | inverse round-trips forward to 0.1% | R_max(σ=1) = 12.98 km, SNR there **13.0000 dB** (exact) | — |
| solution | same | three-target ranges within 1% of instructor values | airliner **32.65 km** · fighter **12.98 km** · drone **4.11 km** (these ARE the instructor values) | — |
| solution | same | σ^¼ law | σ×2 → range ×**1.1892** (2^¼ = 1.1892); airliner/drone ratio **7.953** = 4000^¼ | — |
| plots | `MPLBACKEND=Agg python solutions/hw1_solution.py --plot` | writes `hw1_plots.png`, two panels | written; verticals at 4.11/12.98/32.65 km; +1/4 guide collinear with range curve (visually confirmed) | ~1 s |
| compile | `python -m py_compile` (all 4 .py) | silence | silence | — |

Numbers quoted in script/slides/HOMEWORK.md, all confirmed by the runs above:
FSPL(1 GHz, 1 km) = 92.45 dB · kT₀ = −173.98 dBm/Hz · 1 MHz floor = −113.98 dBm ·
WiFi at 50 m: −46.03 dBm / 47.93 dB (at 200 m: 35.89 dB; at 1 km: 21.91 dB) ·
σ=1 m² at 15 km: 10.49 dB · range doubling costs 12.04 dB (one-way 6.02) ·
400-km factor: 22,524× · deliberate-bug drone range: 23.09 km (×5.62).

Notes: lab is fully deterministic (no RNG), so outputs are exactly reproducible.
`hw1_plots.png` / `ring_slot.png` are regenerable and gitignored.

## Lecture 2 — Transmission-line theory (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic, all cells | full output; standing_wave/bounce PNGs | 1.1 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.12 s |
| solution | `--check` | Z_in vs skrf ≤ 1e-6 rel | **5.45e-16** | 0.9 s |
| solution | same | lossless \|Γ\|²+delivered = 1 ± 1e-12 | residual **0.0** | — |
| solution | same | λ/4 \|Γ(f₀)\| < 1e-10 | **7.16e-17** | — |
| solution | same | 10-dB-RL bandwidth measured | 1.2337–3.5663 GHz = **2332.5 MHz** | — |

Headlines: coax α = 0.9663 dB/m, v_p = 2e8; antenna Γ = 0.2851∠−110.0°, SWR 1.798;
"the lie" 10.90 → 30.09 dB through 10 m; transformer Z_T = 37.29 Ω at spacer 0.0973 λ;
bug: λ/4 vs 3λ/4 20-dB bands 576.8 vs 275.6 MHz. Deviation: war story moved 2f₀ → 1.5f₀
(physics — λ/2 jumper is transparent at 2f₀); syllabus updated to match.

## Lecture 3 — Smith chart & matching (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (pysmithchart optional detected) | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic | full output; 3 PNGs | 1.3 s |
| starter | `--check` / `--smith` | graceful pre-implementation | "not implemented" / instructor-fallback, exit 0 | ~1 s |
| solution | `--check` | both designs \|Γ(f₀)\| < 1e-8 | L-section **2.7e-16**, stub **1.8e-16** | 1.1 s |
| solution | same | 10-dB-RL bandwidths measured | stub1 1414.7 MHz, stub2 2187.6 MHz (wide sweep); in-window edges edge-limited (raw load RL 10.90 dB) | — |
| plots | `--smith` | trajectory through correct intermediate point | confirmed on g = 1 circle | 1.8 s |

Headlines: L-section 2.88 nH + 0.827 pF (Q = 0.624); stub d = 0.4953 λ, ℓ = 0.4146 λ (sol 1);
bug (impedance-not-admittance): d off by exactly λ/4, |Γ(f₀)| = 0.527 — worse than unmatched.
Note: 10-dB threshold barely discriminates for this load (raw RL already 10.90 dB) — worst
in-band RL + 15-dB edges quoted additively; converted into ANSWERS Q5 content.

## Lecture 4 — Network theory / S-parameters (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` | 1.0 s |
| walkthrough | `python hour3_walkthrough.py` | bug demo prints | naive S@S caught by `is_reciprocal` | 1.0 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.9 s |
| solution | `--check` | conversions vs skrf ≤ 1e-10 | s2a **1.64e-12**, s2z **8.05e-12** | 0.9 s |
| solution | same | cascade vs skrf `**` ≤ 1e-10 | 6 sections: **1.02e-15** | — |
| solution | same | 3 planted networks classified | A confirmed passive; B unitarity 0.0302 (claim false); C passivity 5.353 (claim false) | — |

Headlines: B hides 0.07 dB loss invisible on a plot; C is a +8 dB disguised amp.
Design note: naive S@S cascade of unitary networks stays unitary — the catch necessarily
runs through reciprocity; taught explicitly ("you need the whole suite").

## Lecture 5 — Planar lines & waveguides (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (fdtd 0.3.5 detected) | 1.0 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic incl. fdtd cell | diff-identical runs; fdtd λ_g 39.24 vs 39.71 mm (1.2%), κ 0.4% | 4.9 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.14 s |
| solution | `--check` | Z₀ ≤ 2% of MLine, 1–20 GHz | worst **1.73%** (with Wheeler thickness corr.) | 1.0 s |
| solution | same | ε_eff ≤ 3% | worst **2.63%** | — |
| solution | same | cutoffs exact 4 digits vs c/2a | **Δ = 0.0 Hz** | — |
| solution | same | group delay ≤ 1% of dβ/dω | worst **0.057%** | — |
| solution | same | loss ranking + numbers | WR-90 0.0321 dB vs microstrip 2.694 dB /30 cm (×84); FR-4 10.47 dB | — |

Headlines: 50 Ω RO4350B w = 1.1131 mm, ε_eff = 2.7361; λ/4 transformer 4.6305 mm;
cutoffs 6.5571/7.8686/9.4878 GHz. Deviations: ε_r-bug measures **13.2% short** (not the
syllabus's "20% long" — syllabus updated); openEMS case study = clearly-labeled runtime
placeholder + code ready for real instructor export; fdtd PEC-by-zeroing unstable → metal
walls as high-conductivity AbsorbingObject (validated 1.2%/0.4%).

## Lecture 6 — Broadband matching & resonators (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (Qfactor smoke Q_L 250.0) | 1.7 s |
| walkthrough | `python hour3_walkthrough.py` | bug (Q_L as Q_u) prints | fix factor ×2.00 shown | 1.6 s |
| starter | `--check` | "not implemented", exit 0 | as specified | <2 s |
| solution | `--check` | minimum N verified | theory N=2 (20.09 dB) FAILS exact sweep (18.98); **min N = 3** (29.44 dB) | 1.2 s |
| solution | same | hand cascade vs skrf referee | \|Γ\| delta **9.0e-16** | — |
| solution | same | Q within 2% of Qfactor; trap caught | worst **1.05%**; trap: Q_u/Q_L = 25.5× | — |

Headlines: Bode–Fano 12.5 Ω ∥ 2.2 pF → 78.96 dB ceiling (feasible); ∥ 10 pF → 17.37 dB
(20-dB spec impossible by theorem); largest physical C = 8.686 pF. Deviation (syllabus
updated): "worst RL within 0.5 dB of theory" is unattainable at 4:1 ratio (small-reflection
error +1.1 dB at N=2, +2.0 at N=3) — the gap is now centerpiece pedagogy; enforced criterion
is hand-vs-skrf ≤ 1e-12 plus gap quoted and reconciled.

## Lecture 7 — Dividers & couplers (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (Circuit smoke) | 1.0 s |
| walkthrough | `python hour3_walkthrough.py` | bug (R doubled) prints | match survives, isolation −15.56 dB | 1.2 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.9 s |
| solution | `--check` | even/odd S(f₀) vs skrf ≤ 1e-6 | worst **1.94e-16** (4 cases) | 1.0 s |
| solution | same | balance ≤ 0.01 dB; isolation > 30 dB | spread **0.0 dB**; isolation −320 dB (float floor) | — |
| solution | same | Δ null > 60 dB | **−313 dB** at ψ = 90°, paths 180.000000° apart | — |

Headlines: Wilkinson S(f₀) = −3.0103 dB at −90° exactly; 20-dB band 36%; branch-line
0.5-dB balance band 18%. skrf 1.13 findings recorded: Circuit port order = connection-list
appearance order; DefinedGammaZ0 default gamma is dispersionless (pass γ = jω/c explicitly);
90° hybrid nulls at ψ = 90° not boresight (made PREDICT-FIRST Q2; rat-race contrast taught).

## Lecture 8 — Filters I (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` | 1.0 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic | full output; 2 PNGs | 1.1 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.13 s |
| solution | `--check` | g-values vs scipy ≤ 1e-8 | Butterworth **7.45e-12**, Cheb 0.5 dB **2.44e-14** (N ≤ 8) | 1.0 s |
| solution | same | order answer exact | Chebyshev **3** vs Butterworth **4** | — |
| solution | same | spec met, margins quoted | ripple 0.5000 (+0.00), 35 MHz +12.38 dB, 85 MHz +0.52 dB | — |

Headlines: f₀ = 59.7913 MHz (√(f₁f₂)); ladder 1270.3 nH / 5.578 pF series, 20.30 nH /
349.09 pF shunt; group-delay spread ≈ 9 m radar range smear; bug (f₀ arithmetic mean):
0.9726 dB edge ripple — fails spec while rejections still pass.

## Lecture 12 — Mixers & receivers (verified 2026-08-05, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | products visible; bug collision prints | 24/24 diode products; switch −3.92 dB = theory; collision at 10.2428 GHz | 1.1 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.4 s |
| solution | `--check` | spur table = closed form to order 3 | max \|Δf\| = **0.0 Hz**; FFT referee 24/24 | 5.6 s |
| solution | same | plan passes audit | high-side IF 321.4 MHz: 0 fatal (low-side infeasible for EVERY legal IF) | — |
| solution | same | min Doppler within 5% of bound | 2.566 vs 2.542 m/s → **0.94%** | — |

Headlines: chosen plan high-side LO, IF = 321.4 MHz (Nyquist zone 6 of 100 MS/s);
preselector n = 7, IF filter n = 4; v_min = 2.57 m/s at 60 dB clutter with −40/−70/−90
dBc/Hz profile. War story set at S-band 2.9 GHz (X-band image can't reach 2.4 GHz Wi-Fi).
