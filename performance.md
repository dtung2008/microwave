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

## Lecture 11 — Amplifier design & the LNA (verified 2026-08-07, lesson-builder agent)

Device: **real vendor file obtained** — Mini-Circuits `PGA-103+_S2P.zip` (browser
UA + referer needed; bare curl 403s), file `PGA-103+_5V_Plus25DegC.s2p`, 660 pts,
10 MHz–20 GHz. Gitignored; never committed. Offline fallback `demo_device()`
(synthetic, labeled) verified in parallel. Noise parameters are instructor-modeled
(no noise data in any .s2p), calibrated so NF(Γ_S=0) reproduces the datasheet 50 Ω
NF column (0.5/0.5/0.6/0.9/1.2/1.5 dB at 0.05/0.4/1/2/3/4 GHz).

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (stability/circle/max_gain smoke K=1.656) | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | bug (f₀-only stability) prints | passive \|Γ_L\|=0.40 → \|Γ_in\|=1.0613 at 10 MHz; finished amp \|Γ_in\|=1.175 at 16.15 GHz | 1.1 s |
| starter | `--check` | "not implemented", exit 0 | as specified (both device paths) | 0.9 s |
| solution | `--check` | K/Δ/μ vs independent path ≤ 1e-8 | dK **4.44e-16** (skrf `.stability`), dΔ **3.40e-16** (det), dμ **1.77e-14** (Edwards–Sinsky circle geometry; skrf 1.13.0 has no μ built-in) | 0.8 s |
| solution | same | both stability criteria agree everywhere | K–Δ vs μ verdicts **660/660** (demo 120/120) | — |
| solution | same | realized G_T within 0.1 dB of target in cascade | target MAG−2 = 8.2268 dB; cascade **+0.00e+00 dB** delta (matcher unitarity ~9e-16) | — |
| solution | same | frontier monotone | G_T 10.227→8.794 dB, NF 1.599→0.820 dB, **0/0 violations** | — |
| solution | `--plot` | 3 panels | `hw11_plots.png` (audit / Γ_S plane / frontier) | 1.5 s |

Headlines (vendor, 2.4 GHz): K = 1.0973, |Δ| = 0.5499, **μ = 1.2254**; μ<1 bands
**0.010–0.110 GHz** (worst 0.294) and **15.10–16.80 GHz** (worst 0.710); |S21|² =
9.685 dB, MSG = 12.128 dB, **MAG = 10.227 dB**; Γ_MS = 0.413∠−160.8°; Γ_opt move
costs **1.433 dB** of G_T for **0.78 dB** of NF; Q5 Friis (NF₂=6 dB): 2.3756 dB
(gain end) vs 2.0446 dB (noise end), tie at NF₂≈8.7 dB. Datasheet typ gain
11.0 dB@2 GHz / 8.1@3 GHz → ≈9.8 dB interpolated @2.4 vs file 9.685 dB — coheres
(datasheet gain = |S21|²). Demo device: μ<1 band 0.20–1.60 GHz (worst 0.722),
MAG = 18.001 dB, Γ_opt cost 0.663 dB. skrf 1.13 findings: `Network.stability` is
K only (no μ anywhere in the wheel); `stability_circle(target_port, npoints)`
returns loci (student circles vs loci: 8.9e-16); `max_gain` silently switches
MAG↔MSG at K=1 (mirrored in `max_gain_db` spec); `nf_circle` exists but requires
Network noise data — unusable with s2p-only files, so noise circles are hand-rolled.

## Lecture 9 — Filters II: distributed (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (γ-explicit line + coupled Z→S smoke) | <1 s |
| starter | `--check` | "not implemented", exit 0 | toolkit g-check prints; 3× "not implemented" | 0.4 s |
| solution | `--check` | stub LPF within 0.01 dB of theory at f₀ | **−0.500000 dB** (Δ<1e-6); sweep vs closed form 2.84e-14; Kuroda equivalence 6.7e-16 | 2.8 s |
| solution | same | BPF meets ripple/BW in ideal sweep | IL(f₀) 0.0000 dB; 0.5-dB BW **9.83%** vs 10% designed (J-inverter mapping physics — reconciled in ANSWERS Q4) | — |
| solution | same | reentrant passband within 1% | **7.2000 GHz, 0.000% error** | — |
| solution | same | ideal-vs-EM deltas quoted | center −26 MHz (−1.08%), all tagged **[PLACEHOLDER]** pending real openEMS export | — |
| walkthrough | `python hour3_walkthrough.py` | 2f₀-sweep bug prints | "ship it" 52.8 dB → honest sweep 0.0 dB at 7.20 GHz | 1.2 s |

Headlines: stub LPF 81.32/129.81/45.59 Ω λ/8 stubs; coupled BPF Z0e/Z0o =
70.60/39.24 (ends), 56.64/44.77 (interior) — matches Pozar Ex 8.8 to 5e-5 Ω;
Akhtarzad dimensions ends w 0.931/s 0.087 mm. Deviations: EM case study is a
loudly-labeled placeholder (openEMS not installed); coupled_dims has no in-venv
truth referee (round-trip 1e-15; quasi-static caveat taught as the lecture's
own thesis); 9.83% vs 10% BW kept as course content rather than padding Δ.

## Lecture 10 — Noise & nonlinearity (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (Friis + IM3-bin smoke) | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic; dB-Friis bug caught | byte-identical reruns; bugged 1.6470 vs true 2.3387 dB, attenuator invariant convicts | 0.9 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.14 s |
| solution | `--check` | cascade vs hand chains ≤ 0.01 dB NF / 0.1 dB IIP3 | deltas **0.0000 / 0.0000** | 0.14 s |
| solution | same | two-tone slope referees IIP3 | slope **3.0000**; extrapolated IIP3 d = −0.0023 dBm | — |
| solution | same | ordering verdicts | 20 orderings, NF 2.0378→14.9267 dB; best-SFDR ≠ best-MDS; "obvious" chain rank 9 | — |
| solution | same | range delta via lecture-1 engine | best 4.339 vs worst 2.066 km, ratio **2.1000** = 10^(ΔNF/40) exactly | — |

Headlines: element set = task defaults (worked unmodified); all orderings share
G = 39.5 dB; best MDS −111.94 dBm; SFDR@1 MHz best 69.51 dB; Y-factor demo
recovers NF 1.5000 from ENR 15 dB. Toolkit re-provides the hw1 radar engine
(same names/contracts) per the no-cross-lesson-imports rule.

## Lecture 13 — Antennas & arrays (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (AF-vs-geometric-series + chebwin smoke) | 0.4 s |
| starter | `--check` | "not implemented", exit 0 | as specified (inherited starter KEPT after audit; 3 surgical fixes) | 0.4 s |
| solution | `--check` | uniform SLL within 0.1 dB of −13.26 | −13.1468 dB = exact finite-N closed form (Δ 3.8e-08); the 0.115 dB vs the −13.26 *asymptote* is finite-N physics, taught (see deviation) | 1.2 s |
| solution | same | beamwidth within 1% of closed form | broadside 0.169%, steered-45° 0.170% | — |
| solution | same | Chebyshev −30 ± 0.2 dB | **−30.00 dB** (chebwin guarantee Δ −0.000) | — |
| solution | same | grating onset to 0.1° | Δ **0.0002°** (−56.238°) | — |
| walkthrough | `python hour3_walkthrough.py` | degrees-into-sin bug plots | FFT≡AF to 4.5e-14; bug comb spacing π | 2.6 s |

Headlines: uniform 16-el HPBW 6.359°, D 12.041 dBi (= N to 2e-10); Chebyshev −30
broadening ×1.2550, directivity cost 0.647 dB; scene margins uniform +2.69 dB
(buried) vs Chebyshev +12.54 dB (revealed); steer-45° broadening ×1.4194;
16×16 ≈ 29.05 dBi vs the 33 dBi dish (~635 elements). Deviations: SLL criterion
read against the exact finite-N value (no correct N=16 implementation can hit the
asymptote ±0.1 dB); scene geometry fixed (drone 10°→15°, 3→3.5 km) so the taper
story has an answer; chebwin's <45 dB UserWarning filtered with explanation.

## Lecture 14 — Radar equation & detection (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (detection smoke) | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | power-vs-amplitude bug prints both P_fa | bugged **1.1e-3** vs honest 2e-6 on same 10⁶ draws (√P_fa exactly) | 1.3 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 0.4 s |
| solution | `--check` | P_fa within 3σ binomial of 1e-6 at 10⁶ trials | threshold exact; 0 of 10⁶ (expected 1, 3σ ±3e-6) — inside; 1e-2/1e-3 grids on-design | 0.5 s |
| solution | same | MC P_d within 0.5 dB of Albersheim (6–16 dB) | worst in-envelope gap **0.16 dB**; vs exact Marcum \|ΔP_d\| ≤ 0.0021 | — |
| solution | same | CFAR on 3 scenes + masking | clean 0 FA; clutter-edge masks the 995 target; two-drones masks the weaker (solo control detects) | — |

Headlines: T(1e-6) = 3.7169 (11.40 dB over mean noise); Albersheim (0.9, 1e-6) =
13.11 vs exact 13.18 dB; honest ranges shrink ×0.9934 (drone 4.11→4.08 km; the
13 dB hand-wave delivered P_d = 0.8744 — it hid meaning, not range); Swerling-1
+8 dB → drone ~2.6 km; CFAR loss 2.01 dB (N=16) → 0.97 (N=32); clutter-edge FA
elevation 13× design (800-edge ensemble at 1e-3 — single scene at 1e-6 is
statistically blind, a forced design choice). CA-CFAR interface for L15:
`ca_cfar(power_profile, n_train, n_guard, pfa) -> (detections, threshold)`,
per-side counts, strict >, edge-truncating with α recomputed.

## Lecture 15 — FMCW, Doppler & micro-Doppler (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` | `SETUP OK` (dechirp smoke: 60 m → bin 120) | <1 s |
| walkthrough | `python hour3_walkthrough.py` | no-window bug buries the drone, with numbers | no-window: 16.11 dB vs threshold 30.24 → buried; Hann: 17.73 vs 13.46 → detected | 1.1 s |
| starter | `--check` | "not implemented", exit 0 | as specified | 1.3 s |
| solution | `--check` | all planted targets within 1 range + 1 Doppler bin | worst **0.35 range / 0.04 Doppler bins**; 3 targets, 0 extras | 1.6 s |
| solution | same | HERM spacing within 2% of N_b·f_rot | **200.000 Hz vs 200.0 → 0.000%** | — |
| solution | same | Parseval through FFT chain | residual **0.0** | — |

Headlines: waveform B = 300 MHz, T_c = 10 µs, N = 512 → ΔR 0.4997 m, v_unamb
±97.34 m/s, Δv 0.3802 m/s, CPI 5.12 ms; T_c legal window [7.82, 12.98] µs;
drone blades v_tip 69.12 m/s → ±35.5 kHz (unaliased by design — the spec's
v_unamb line exists because of the blades); f_rot 100 Hz = 6000 rpm recovered;
R–v coupling +46.8 mm at 20 m/s measured. Per-cell CFAR P_fa 1e-7 (map-size
argument taught). Course-wide sign convention set: v = range rate, receding
positive (L16 CPA inherits it).

## Lecture 16 — Beamforming, DOA & collision avoidance (capstone) (verified 2026-08-07, lesson-builder agent)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | `SETUP OK` (incl. pyargus) | `SETUP OK` | 1.5 s |
| starter | `--check` | "not implemented" ×4, exit 0 | as specified | 0.14 s |
| solution | `--check` | DOA within 0.5° of pyargus on identical snapshots | **0.000°** on all 6 comparisons (3 scenes × Bartlett/Capon) | 1.8 s |
| solution | same | CPA error < 5 m on all intruders | worst **0.94 m** | — |
| solution | same | alert truth table incl. correct non-alert | **5/5** (3 alerts + 2 non-alerts, incl. jammed scene) | — |
| walkthrough | `python hour3_walkthrough.py` | few-snapshot MVDR bug + diagonal-loading fix | K=8: −114.45 dB at own target; +10 dB loading → +27.74 dB (honest 27.05) | 1.7 s |

Headlines: 16-el ULA @77 GHz, HPBW 6.348°; resolution flip (predict-first):
1.5 BW — beamscan resolves at every tested SNR (above the Rayleigh-style limit;
the expected wrong prediction is the teaching point), MVDR flips at −12 dB;
0.7 BW — beamscan never, MVDR flips at 0 dB. Jammer 40 dB over drone: beamscan
reads jammer + its sidelobe (chain θ error 53.7°), MVDR recovers the drone at
0.035°. pyargus API fully usable (DOA_Bartlett/DOA_Capon/corr_matrix_estimate;
axis-referenced cos θ convention mapped and taught). Course wrap: the L1 block
diagram closes with every box opened.

## Full-course sweep (2026-08-07)

All 16 lessons: complete file sets (script.en + script.zh-hant + slides + 9 lab
files each) · setup_check / starter --check / solution --check all exit 0 ·
all 16 hour-3 walkthroughs run clean headless · every .py compiles.

## Chapter 0 — Maxwell as Arrows (pre-course; verified 2026-08-09)

| Path | Command | Criterion | Measured | Runtime |
|---|---|---|---|---|
| numbers | `python tour_numbers.py all` | deterministic; every quoted number reproduced | diff-identical reruns; drift 7.35e-5 m/s, τ 2.49e-14 s, signal 0.667c; shear circ/area −2.0000 at all loop sizes; vortex 2π any R; coax ∫E×H = 2.00000 W vs VI (Δ 6.9e-12); barber-pole pitches 90/45/18.4°; Lundquist curl residual ≤ 1.0e-4 | ~2 s |
| figures | `python tour_figures.py` | all 6 regenerate | fig01–fig06 written (committed — content, not lab byproduct) | ~4 s |
| compile | `py_compile` both .py | silence | silence | — |

New chapter (user-requested 2026-08-09, option "Chapter 0 primer"): qualitative
Maxwell — three speeds of current, flux as integral, ∇'s 1/m, curl as
circulation density, the seven arrow rules (coax P = VI by Poynting), the
barber-pole/Helmholtz caveat, magnetic current & force-free fields. Follows the
optimizations `00-wind-tour` precedent: essay + reproducibility scripts +
committed figures; no lab, no slides, English-only, numpy(+scipy Bessel) only.
Syllabus preamble updated with the Chapter 0 pointer.

Revision 2026-08-09 (user review of Chapter 0): §0.3 "units audit" judged too
thin for a section — table folded into §0.0 (equations now stated with units
in one place); §0.1 Drude/Ohm enrichment paragraph demoted to a footnote (the
course needs the conclusion, not the derivation); NEW §0.3 "Divergence is flux
density" added as §0.4's exact dual — point-charge field: enclosing-box flux
4π at any size, −0.0000 non-enclosing, flux/volume → 0 off the charge (Gauss's
law found numerically, mirroring §0.4's Ampère 2π); fig07_divergence.png added.
Numbers script re-verified deterministic; all 7 figures regenerate.
