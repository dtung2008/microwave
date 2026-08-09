# Microwave Engineering Foundations — 16-Lecture Syllabus

Senior-undergrad / first-year-grad. Three emphases per week: **theory background,
applications, software/simulation**. Applications drawn from **wireless communications,
radar, avionics, and automotive sensing**, with an explicit **detection thread** —
aircraft / missile / drone detection and navigation collision avoidance — seeded in
lecture 1 and carried to a four-lecture radar arc (13–16). Every assignment runs
identically on **Windows, macOS, and Linux**, CPU only. Evidence base:
[survey.md](survey.md) (web-verified 2026-08-04).

**Prerequisites:** one undergraduate EM course (Maxwell's equations at a glance, plane
waves), circuit analysis (phasors, two-ports), signals (Fourier transform, convolution),
basic probability, Python.

**Format:** each lecture is one 3-hour session with a 10-minute break every hour —
**Hours 1–2 Principles → Hour 3 Tools**. The two principle hours carry the theory:
formulas derived (fast version + first-principles version), applications motivated, design
procedures worked. Hour 3 opens with a 5-minute setup verification, then puts the week's
ideas on screen in live code. **Practice happens in homework**, not in class.

**Homework** follows [HOMEWORK-PRINCIPLES.md](HOMEWORK-PRINCIPLES.md): one coherent story
per week integrating the lectures so far; the current lecture's core routine is the meat;
modules independently checkable against provided reference inputs; non-core plumbing
provided as tool-like calls named after course nouns (`db` · `friis` · `radar_range` ·
`cascade` · `smith` · `range_doppler` · `show`); **prediction-before-run questions**
answered before executing and reconciled after; solution path left underspecified;
≤ 3 hours honest effort; AI use assumed, never policed. Checkers print measured facts,
not `PASS`/`FAIL`; airtight verification lives instructor-side in each lecture's
`VERIFY.md`.

**Delivery: entirely Tier A (local pip).** The whole course runs on one small stack —
`numpy==1.26.4` / `scipy` / `matplotlib` (base), **`scikit-rf==1.13.0`** (the course
workhorse: networks, Touchstone, Smith charts, media models; 2.0.x is incompatible with
the numpy pin — survey §3.6), plus optional per-lecture
extras (`pysmithchart`, `fdtd` for field demos, `pyargus` for lecture 16). **Python 3.12,
exactly.** No Colab, no Docker, no GPU, no commercial licenses. Full-wave EM (openEMS) and
commercial EDA (ADS/HFSS/CST) appear as instructor-run demos and industrial context only —
students post-process exported results, never install the tools (survey §3.2).

**The referee principle** (inherited from the prior courses): students hand-roll the
formula or pipeline; an independent check referees it — scikit-rf media/networks for
lines and cascades, **physics invariants** (reciprocity S=Sᵀ, passivity, lossless
unitarity) for network work, closed-form tables for filters and arrays, **planted analytic
ground truth** (f_b = 2Rα/c, f_d = 2v/λ, HERM-line spacing = N_b·f_rot) for radar scenes,
and **real vendor Touchstone files** (student-downloaded) for the ideal-vs-measured gap.
The library is the referee, not the player.

**Bilingual scripts:** every lecture ships parallel English and Traditional Chinese
scripts (`script.en.md`, `script.zh-hant.md`); zh-Hant uses standard Taiwan terminology
(散射參數 / 阻抗匹配 / 雷達截面積) with English technical terms in parentheses on first
use. Code, APIs, and paper titles stay in English in both. Homework files are shared.

**Readings:** every required reading is free — Steer's open-access five-volume set [R2]
and Orfanidis [R4] — with the matching Pozar [R1] chapter listed for students who bought
it. Radar-thread readings run on MIT Lincoln Laboratory OCW material [R31][R33], TI's
FMCW white paper [R34], and open-access drone-detection literature [R28][R29][R30].

**Arc:** lectures 1–5 waves, lines & networks · 6–9 passive design · 10–12 the receiver ·
13–16 radar & detection systems.

**Chapter 0 (pre-course, optional):** [Maxwell as Arrows](lessons/00-maxwell-as-arrows/tour.en.md)
— qualitative electromagnetics before any calculation: the three speeds of one
ampere (drift vs signal), flux as an integral, ∇'s 1/m, curl as circulation
density (shear vs vortex, walked numerically), the seven arrow rules with coax
power flow solved in three sentences (∫E×H = VI to 7×10⁻¹² W), the barber-pole
caveat, and the empty magnetic-current slot (duality, slot antennas, force-free
fields). Every number reproducible by `tour_numbers.py`; no solver library used.
Recommended when the prerequisite EM course is more than a couple of years old.

| # | Lecture | Application anchors | Hands-on tool |
|---|---------|--------------------|---------------|
| 1 | Microwave systems panorama: dB, link budgets, the radar equation | comms links, radar preview | NumPy + first contact with scikit-rf |
| 2 | Transmission-line theory | cables, antenna feeds | NumPy (skrf referee) |
| 3 | The Smith chart & impedance matching | antenna matching | skrf Smith plotting |
| 4 | Microwave network theory: S-parameters | every component after this week | skrf Network + invariant checks |
| 5 | Planar lines & waveguides | PCBs, radar front-ends | hand-rolled Hammerstad vs skrf MLine |
| 6 | Broadband matching & resonators | wideband radar/comms front-ends | skrf cascade + Qfactor |
| 7 | Power dividers & couplers | array feed networks | skrf Circuit |
| 8 | Filters I: insertion-loss synthesis | receiver band selection | scipy prototypes + skrf |
| 9 | Filters II: distributed realizations | microstrip filters | skrf media + hand synthesis |
| 10 | Noise & nonlinearity | receiver dynamic range | NumPy cascade engine |
| 11 | Amplifier design & the LNA | radar/comms receivers | skrf + real vendor .s2p |
| 12 | Mixers, detectors & receiver architectures | superheterodyne, FMCW dechirp | NumPy behavioral models |
| 13 | Antennas & arrays | radar apertures, 5G | NumPy array factor |
| 14 | The radar equation & detection | aircraft/missile detection | NumPy Monte Carlo + CFAR |
| 15 | FMCW, Doppler & micro-Doppler | drone detection, automotive | NumPy/SciPy pipeline |
| 16 | Beamforming, DOA & collision avoidance — capstone | UAV avoidance, 77 GHz automotive | NumPy + pyargus |

---

## Lecture 1 — Microwave systems panorama: dB, link budgets, and the radar equation

**Scope.** What "microwave" means and why distributed effects change everything (the λ
argument: when wire length ≈ wavelength, Kirchhoff dies); the frequency landscape from
WiFi to W-band and who lives where (comms, radar, navigation); dB culture done right
(dB/dBm/dBi/dBsm, and why you never add two dBm); the Friis transmission formula derived
from isotropic spreading + aperture; noise floor kT₀B; SNR; the monostatic radar equation
as Friis folded back on itself with an RCS in the middle; detection range. The course map:
how lectures 2–16 build every block of the radar/receiver just sketched.

**Objectives.** Convert fluently between linear and dB quantities; assemble a link budget
from EIRP to receiver SNR; derive the radar equation from the Friis formula and explain
every factor's physical origin; compute detection range against a noise floor; state why
R⁴ (not R²) governs radar and what that costs in practice.

**3-hour breakdown.**
- H1–H2 Principles: the λ argument with numbers (3 GHz, 10 cm, your PCB is an antenna);
  spectrum tour anchored on detection systems (L-band surveillance, X-band fire control,
  K/W-band automotive); dB algebra and its traps; Friis derived twice — energy-spreading
  fast version, aperture/directivity first-principles version; noise floor from kT₀B with
  the −174 dBm/Hz number every RF engineer memorizes; radar equation assembled live on the
  board; worked example: can an X-band radar with given P_t, G, σ see a 747 at 400 km? a
  cruise missile? a DJI quadcopter?
- H3 Tools: Python env verification; NumPy as an RF calculator — `db`/`undb`, vectorized
  link budgets, detection-range curves vs σ on log axes; first contact with scikit-rf
  (`Network`, the bundled `ring_slot` example plotted in dB and on the Smith chart — a
  preview of lectures 3–4; plus the honest lesson that `skrf.media.Freespace` is a
  *lossless medium* — spreading loss is antenna bookkeeping, not a medium property);
  deliberate-bug demo: a link budget that silently adds watts to dBm and reports a
  wildly optimistic answer.

**Homework (~3 h) — "Can this radar see the drone?"** One story: build a link-budget
engine (dB machinery + Friis) for a comms downlink, extend it to the monostatic radar
equation with a noise floor, then run a three-target study — airliner (σ ≈ 40 m²),
fighter (σ ≈ 1 m²), small drone (σ ≈ 0.01 m²) — against a mid-size surveillance radar.
Core routine: the radar-equation solver (forward: SNR at range; inverse: maximum detection
range at required SNR). Predict first: σ drops 40 dB from airliner to drone — detection
range shrinks by what factor, and why not 10⁴? Referee: an instructor-provided
**linear-watts physics chain** (power density S = P_tG_t/4πR², aperture A_e = Gλ²/4π,
P_r = S·A_e — no dB anywhere) referees the student's dB-domain engine: two independent
implementations that disagree loudly if watts and dB were ever mixed; plus forward/inverse
round-trip (R_max(SNR(R)) = R) and limit checks (σ ×2 → range ×2^¼).

**Success criterion.** Student's dB-domain Friis and radar-equation results match the
toolkit's linear-watts referee to 1e-6 dB on reference inputs; inverse detection range
round-trips the forward solver to 0.1%; the three-target ranges land within 1% of the
instructor's measured values (performance.md); prediction answers reconciled (human-read).

**Setup (pre-class, Tier A).** Python 3.12 + `pip install -r requirements.txt` (numpy
1.26.4, scipy, matplotlib, scikit-rf 1.13.0) — identical on all OSes; run
`lab/setup_check.py` → `SETUP OK`.

**References.** Steer Vol. 1 chs. 1–2 (radio systems, free [R2]); Pozar ch. 14 intro +
radar/Friis sections [R1]; Friis 1946 [R21] (2 pages — assign it whole); MIT LL radar
course lecture 1 [R31]; radar-course.org [R32].

---

## Lecture 2 — Transmission-line theory

**Scope.** The telegrapher's equations from an RLGC cell; traveling waves, characteristic
impedance Z₀, propagation constant γ = α + jβ; reflection coefficient Γ, standing waves,
SWR; input impedance of a terminated line and the tangent transformation; the λ/4 and λ/2
special cases; power flow and return loss; lossy lines and dB/m; time domain — bounce
diagrams and why a digital engineer's "ringing" is our |Γ|.

**Objectives.** Derive Z₀ and γ from RLGC; compute Γ, SWR, and Z_in(ℓ) for any
termination; translate between return loss, |Γ|, SWR, and mismatch loss without a table;
explain a bounce diagram; identify when a line is "electrically long."

**3-hour breakdown.**
- H1–H2 Principles: RLGC cell → telegrapher → wave equation (fast: phasor substitution;
  first-principles: the limit process); Z₀ meaning — the ratio the line *enforces*;
  Γ derivation and the reflected-power picture; standing-wave anatomy with the crank
  diagram previewing the Smith chart; Z_in(ℓ) derived and the quarter-wave inverter
  celebrated; loss, attenuation, and where the dB/m numbers come from; war story: the
  half-wavelength jumper that "did nothing" at the bench at f₀ and everything at 1.5f₀
  (where it turns 3λ/4 — at 2f₀ it is a full λ and transparent again).
- H3 Tools: hand-rolled line engine in NumPy (Γ, SWR, Z_in vs ℓ and f); skrf
  `DefinedGammaZ0`/`DistributedCircuit` as the referee; standing-wave pattern animation;
  bounce-diagram demo; deliberate bug: forgetting the tangent's periodicity and
  "designing" a 3λ/4 transformer that also works — or does it, with loss?

**Homework (~3 h) — "The feed line that lies."** One story: a 10 m coax run feeds a
mismatched antenna (Z_L = 36 − j21 Ω). Modules: (1) the line engine — Γ, SWR, Z_in(ℓ, f)
from RLGC; (2) power accounting — incident/reflected/delivered power and mismatch loss
vs frequency, including line loss; (3) the λ/4 fix — place and size a quarter-wave
transformer and measure what it does off-frequency. Predict first: at which ℓ/λ does
Z_in look purely real, and how many times per wavelength? Referee: skrf line models.

**Success criterion.** Z_in matches skrf to 1e-6 relative across the sweep; delivered
power conserves energy (|Γ|² + delivered fraction = 1 ± 1e-12 lossless); λ/4 transformer
achieves |Γ(f₀)| < 1e-10 by construction and the student reports the measured 10-dB-RL
bandwidth; predictions reconciled.

**Setup (Tier A).** Same env as lecture 1.

**References.** Steer Vol. 2 chs. 2–3 [R2]; Pozar ch. 2 [R1]; Orfanidis chs. 10–11 [R4].

---

## Lecture 3 — The Smith chart & impedance matching

**Scope.** The Smith chart as the conformal map of Γ ↔ z; constant-resistance and
constant-reactance circles; SWR circles; moving along a line = rotating on the chart;
admittance chart and the shunt/series duality; matching with L-sections (lumped, the
2-GHz-and-below world), single-stub tuning (the distributed world), and the quarter-wave
transformer revisited; forbidden regions and why one topology can't reach everything;
bandwidth of a match as the price of resonance.

**Objectives.** Read and plot impedances on the chart; execute L-section and single-stub
designs by hand (chart) and by formula; choose the right topology for a given load
region; explain why matching narrows bandwidth and anticipate the Bode–Fano wall
(lecture 6).

**3-hour breakdown.**
- H1–H2 Principles: the bilinear map derived (fast: plug in; first-principles: why circles
  map to circles); a guided chart walk — plot, rotate, match — done on the document camera
  the way it will appear in every datasheet forever; L-section design equations derived
  from the chart geometry; single-stub design (shunt open/short) with both analytic and
  chart solutions; matching-bandwidth intuition: the match is a resonance, Q tells the
  bandwidth; pre-empted misconception: "the chart is obsolete, software does this" —
  answer: the chart is the *coordinate system* the software plots in; you read stability,
  noise, and match trade-offs on it in lecture 11.
- H3 Tools: skrf Smith plotting (`plot_s_smith`); the lecture-2 line engine's output
  walked around the chart; live L-section and stub designs verified by cascade; deliberate
  bug: matching the impedance instead of the admittance for a shunt stub — the point lands
  diametrically wrong on the chart, visibly.

**Homework (~3 h) — "Match the antenna, twice."** One story: last week's antenna
(Z_L = 36 − j21 Ω at 2.4 GHz) must be matched two ways — an L-section (lumped) and a
single shunt stub (distributed) — and the two designs compared as *products*. Modules:
(1) L-section designer (both topologies, choose by load region); (2) stub-match designer
(analytic d and ℓ, both solutions); (3) the comparison — |Γ(f)| for both across
2.0–2.8 GHz, 10-dB-RL bandwidths measured. Predict first: which design is wider-band and
why (count the stored-energy elements)? Referee: skrf cascade — |Γ(f₀)| must vanish by
construction; the chart plot itself.

**Success criterion.** Both designs achieve |Γ(f₀)| < 1e-8 in the skrf cascade; measured
10-dB-RL bandwidths within 1% of instructor values; the student's chart plot shows the
match trajectory passing through the correct intermediate point (visual, human-read);
predictions reconciled.

**Setup (Tier A).** Same env; optional `pip install pysmithchart` for standalone charts.

**References.** Steer Vol. 3 ch. 6 (matching, free [R2]); Pozar ch. 5 [R1]; Smith 1939/
1944 [R19] (assign for history + the joy of it); Orfanidis ch. 13 [R4].

---

## Lecture 4 — Microwave network theory: S-parameters

**Scope.** Why voltage and current lose meaning at microwave and what replaces them
(traveling-wave amplitudes); impedance/admittance/ABCD matrices and where each shines;
scattering parameters defined, measured (VNA in one slide — what those two port cables
do), and interpreted (S₁₁ match, S₂₁ gain/loss, S₁₂ isolation); reference planes and
de-embedding; reciprocity, losslessness (unitarity), passivity — the invariants that
referee everything after this week; signal-flow graphs and Mason's rule lite; cascading
with ABCD and with S via the ** operator.

**Objectives.** Convert S ↔ Z ↔ ABCD; cascade two-ports correctly; test a measured or
modeled network for reciprocity, passivity, and (claimed) losslessness and interpret
violations; shift reference planes; read a datasheet S-parameter plot with suspicion.

**3-hour breakdown.**
- H1–H2 Principles: normalized wave variables derived from V, I, Z₀ (fast) and from
  power flow (first-principles); the S-matrix as "what a VNA measures"; worked
  two-ports: the attenuator, the ideal transformer, the length of line; unitarity of the
  lossless S-matrix proved and turned into a numerical residual ‖SᴴS − I‖; reciprocity
  from network symmetry; passivity as eigenvalue statement; signal-flow graphs with the
  one-loop rule; cascade algebra; pre-empted misconception: "S₂₁ = gain, always" —
  answer: only into matched terminations; mismatch reshapes everything (lecture 11's
  G_T vs S₂₁ distinction planted here).
- H3 Tools: skrf `Network` from a Touchstone file; conversions and cascades vs
  hand-rolled; **build the invariant checkers** (`is_reciprocal`, `passivity_residual`,
  `unitarity_residual`) that the rest of the course reuses; deliberate bug: cascading
  S-matrices by matrix multiplication (wrong!) vs ABCD (right) — the checker catches the
  non-physical result.

**Homework (~3 h) — "Trust, but verify the two-port."** One story: three "measured"
two-port datasets arrive (instructor-planted): a healthy passive filter, a network whose
file claims losslessness but isn't unitary, and one that violates passivity (a
disguised amplifier — or a bad measurement?). Modules: (1) conversion library S↔ABCD↔Z +
cascade; (2) the invariant suite — reciprocity/passivity/unitarity residuals with
tolerances; (3) the verdicts — classify all three networks and defend the classification.
Predict first: can a passive network have |S₂₁| > 1 at some frequency? (Careful.)
Referee: skrf's own conversions to 1e-10; the physics invariants themselves.

**Success criterion.** Conversions match skrf to 1e-10; cascade of N sections matches
skrf `**` to 1e-10; all three planted networks correctly classified with residuals quoted;
predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 3 chs. 2–3 [R2]; Pozar ch. 4 [R1]; scikit-rf docs [R37].

---

## Lecture 5 — Planar lines & waveguides

**Scope.** Where transmission lines physically live: microstrip (the workhorse —
quasi-TEM, effective permittivity, Hammerstad–Jensen synthesis/analysis, dispersion),
CPW and stripline in one slide each; rectangular waveguide — why hollow pipes guide,
TE/TM modes, cutoff f_c = c/2a, single-mode bandwidth, dispersion β(f), and why radar
transmitters still love waveguide; loss mechanisms compared (conductor, dielectric,
radiation); substrate choices (FR-4 vs Rogers) and what tan δ costs at 10 GHz;
instructor-run openEMS demo: fields in a microstrip cross-section, exported and shown.

**Objectives.** Size a 50 Ω microstrip on a given substrate by hand (Hammerstad);
compute ε_eff and guided wavelength; determine waveguide single-mode band and in-band
dispersion; choose between microstrip/CPW/waveguide for a given frequency/power/loss
requirement; read a stackup like an RF engineer.

**3-hour breakdown.**
- H1–H2 Principles: microstrip fields and the ε_eff compromise (fast: capacitance
  average; first-principles: why quasi-TEM works below ~10 GHz on thin boards);
  Hammerstad–Jensen worked to a real 50 Ω width on FR-4 and on RO4350B; dispersion and
  when the quasi-TEM lie catches up with you; waveguide modes from the boundary-value
  problem (fast: standing-wave count; first-principles: separation of variables), cutoff,
  the WR-90 X-band example every radar text uses; group vs phase velocity — the ω-β
  diagram; loss budget shootout at 2.4 / 10 / 77 GHz; war story: the FR-4 patch array
  that lost 40% of its power in the substrate.
- H3 Tools: hand-rolled Hammerstad functions vs skrf `MLine` (an independent
  implementation with dispersion); skrf `RectangularWaveguide` dispersion curves; `fdtd`
  package demo — watch the TE₁₀ mode refuse to propagate below cutoff; openEMS microstrip
  case-study files post-processed (instructor-exported Touchstone); deliberate bug: a
  microstrip "50 Ω" design that used ε_r instead of ε_eff for the wavelength — every stub
  in the following lectures would land ~13% short on this stackup (measured; the match
  resonates 1.5 GHz high).

**Homework (~3 h) — "Design the board, spec the pipe."** One story: an X-band (10 GHz)
sensor front-end needs (a) a 50 Ω microstrip environment on RO4350B and (b) a waveguide
run to the antenna. Modules: (1) Hammerstad synthesis — width for 50 Ω, ε_eff, λ_g, and a
λ/4 transformer's physical length; (2) waveguide picker — for WR-90/WR-75/WR-62 compute
single-mode bands, in-band β(f) and group delay over 200 MHz; (3) loss shootout —
microstrip (conductor + dielectric, formulas provided in toolkit) vs waveguide loss over
30 cm at 10 GHz. Predict first: does the λ/4 transformer get physically longer or shorter
if you switch FR-4 → RO4350B, and by roughly what factor? Referee: skrf `MLine` and
`RectangularWaveguide`.

**Success criterion.** Hand Z₀ within 2% and ε_eff within 3% of skrf `MLine` across
1–20 GHz; waveguide cutoffs exact to 4 digits vs c/2a; group delay within 1% of the
analytic dβ/dω; loss ranking correct with numbers quoted; predictions reconciled.

**Setup (Tier A).** Same env; optional `pip install fdtd` for the field demo.

**References.** Steer Vol. 2 chs. 4–5 [R2]; Pozar chs. 3, 3.8 [R1]; Wheeler 1965 [R22];
openEMS docs (demo context only).

---

## Lecture 6 — Broadband matching & resonators

**Scope.** Why one λ/4 section is narrowband and what to do about it: multisection
quarter-wave transformers (binomial = maximally flat, Chebyshev = equal-ripple, the
theory of small reflections), tapered lines in one picture; the Bode–Fano criterion —
the physics ceiling on match bandwidth, and reading it as an engineering budget;
microwave resonators: series/parallel RLC near resonance, transmission-line resonators
(λ/2, λ/4), Q_u / Q_L / Q_e and coupling; measuring Q from a sweep — the 3-dB method and
its traps.

**Objectives.** Design binomial and Chebyshev multisection transformers to a bandwidth
spec; state and apply Bode–Fano to declare a spec feasible or impossible *before*
designing; model any resonator near resonance as RLC; extract Q_u and Q_L from swept
data; explain coupling coefficient and critical coupling.

**3-hour breakdown.**
- H1–H2 Principles: theory of small reflections (fast: phasor sum; first-principles: the
  multiple-bounce series that it approximates); binomial and Chebyshev section-impedance
  recursions worked; the bandwidth-vs-N trade plotted; Bode–Fano derived in outline,
  applied in full — "your boss's spec violates a theorem" as a career skill; resonator
  taxonomy; Q definitions from stored/dissipated energy (fast) and from pole location
  (first-principles); coupling and the loaded-Q formula; war story: the "high-Q" cavity
  measurement ruined by the coupling the probe itself added.
- H3 Tools: transformer designer in NumPy, swept in skrf, ripple measured; Bode–Fano
  budget calculator; synthetic resonator sweeps → 3-dB and fitted Q extraction vs skrf
  `Qfactor` (an independent fitting method); deliberate bug: measuring Q_L and reporting
  it as Q_u — the two differ by exactly the coupling everyone forgets.

**Homework (~3 h) — "The impossible spec."** One story: a client wants 50 → 12.5 Ω
matched to 20-dB return loss over an octave. Modules: (1) Bode–Fano feasibility verdict
for a given load model — is the spec physical? (2) Chebyshev multisection designer —
find minimum N, design it, sweep it; (3) resonator lab — extract Q_u/Q_L from three
synthetic resonator datasets (one with a coupling trap). Predict first: doubling N buys
how many more dB of worst-case in-band return loss for this ratio? Referee: skrf cascade
sweep; `Qfactor` fits; the small-reflection theory's own ripple formula.

**Success criterion.** Hand ABCD cascade of the designed transformer matches the skrf
referee to 1e-12 in |Γ|; the theory-vs-exact-sweep gap (small-reflection approximation
error, +1–2 dB at this 4:1 ratio — measured, and itself course content) quoted and
reconciled; minimum-N answer correct by exact sweep (N = 3, not theory's N = 2);
Q extractions within 2% of `Qfactor` fits (and the coupling trap caught); predictions
reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 3 ch. 7 [R2]; Pozar chs. 5.5–5.8, 6 [R1]; Fano via Pozar's
treatment (free alternative: Steer Vol. 3).

---

## Lecture 7 — Power dividers & couplers

**Scope.** Three-ports and the impossibility theorem (matched + reciprocal + lossless:
pick two); the Wilkinson divider — how one resistor buys isolation; even/odd-mode
analysis as *the* technique (developed carefully — it returns for coupled lines);
four-ports: directional couplers, coupling/directivity/isolation defined honestly;
branch-line (90°) and rat-race (180°) hybrids; coupled-line couplers and the even/odd
impedances; where these live in real systems — array feeds, balanced amplifiers,
mixers, monopulse comparators (radar tie-in).

**Objectives.** Prove the three-port impossibility and explain the Wilkinson's escape;
run an even/odd analysis on a symmetric network unaided; specify a coupler by C/D/I from
its S-matrix; design a branch-line hybrid and a Wilkinson at f₀; explain what a monopulse
comparator does with four hybrids.

**3-hour breakdown.**
- H1–H2 Principles: the impossibility proof from unitarity (it's three lines of algebra —
  do it twice, second time slowly); Wilkinson analyzed by even/odd decomposition, the
  isolation resistor's job revealed; branch-line hybrid by the same method; coupled-line
  coupler: even/odd impedances, coupling from the impedance contrast; C/D/I with real
  directivity numbers from datasheets; monopulse: sum and difference beams from a
  comparator of hybrids — how a fire-control radar knows *where* in the beam the target
  sits (thread to lecture 16); pre-empted misconception: "isolation = directivity" —
  they differ by the coupling.
- H3 Tools: skrf `Circuit` assembling a Wilkinson from ideal lines + resistor; the
  even/odd hand analysis checked against the assembled model; branch-line sweep — the
  90° split verified, the bandwidth measured; deliberate bug: an "isolated" Wilkinson
  with the resistor value doubled — match survives, isolation collapses; the checker's
  C/D/I table catches it.

**Homework (~3 h) — "Feed four antennas."** One story: a four-element array (lecture 13
preview) needs equal-amplitude feed: a corporate tree of three Wilkinsons, plus a
branch-line hybrid for a monopulse experiment. Modules: (1) even/odd Wilkinson analysis —
closed-form S at f₀ and the isolation-resistor derivation; (2) the corporate feed
assembled in skrf `Circuit`, swept, port balance and isolation measured; (3) monopulse
teaser — feed the hybrid's Σ and Δ ports, verify the 180° null. Predict first: the
corporate feed's worst-case output imbalance grows how with tree depth if each Wilkinson
has 0.1 dB amplitude error? Referee: unitarity/reciprocity suite from lecture 4; the
closed-form ideal S-matrices.

**Success criterion.** Hand even/odd S(f₀) matches the skrf-assembled model to 1e-6;
corporate feed balance within 0.01 dB (ideal elements) and isolation > 30 dB at f₀;
Δ-port null deeper than 60 dB at f₀; predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 4 chs. 5–6 [R2]; Pozar ch. 7 [R1].

---

## Lecture 8 — Filters I: the insertion-loss method

**Scope.** Filters as the receiver's front door; specification language (passband ripple,
stopband rejection, group delay); the insertion-loss method — lowpass prototypes,
Butterworth/Chebyshev g-values (recursion, not just the table), impedance and frequency
scaling, lowpass→highpass/bandpass/bandstop transformations; order estimation from a
rejection spec; group delay and why the steepest filter isn't always the right one;
where lumped filters stop working and lecture 9 begins.

**Objectives.** Translate a rejection spec into minimum order; generate g-values by
recursion and validate against tables; scale and transform prototypes to any f₀/Z₀/BW;
predict passband ripple and stopband rolloff before sweeping; read group delay as a
system engineer (pulse fidelity — radar tie-in).

**3-hour breakdown.**
- H1–H2 Principles: spec language with a real crowded-spectrum story (your radar IF next
  to a cell uplink); the insertion-loss framework; Butterworth from maximal flatness
  (fast) and from pole positions (first-principles); Chebyshev ripple mechanics and the
  g-value recursion derived; scaling/transformation algebra worked fully for the bandpass
  case (the one with the traps); order-estimation nomogram replaced by the closed form;
  group-delay contrast Butterworth vs Chebyshev at the band edge; pre-empted
  misconception: "more ripple allowed = worse filter" — it's a *trade*, ripple buys
  rolloff.
- H3 Tools: g-value recursion vs `scipy.signal.cheb1ap`/`buttap` (independent referee);
  ladder → S₂₁ sweep in skrf via ABCD of Ls and Cs; the bandpass transformation live,
  group delay plotted; deliberate bug: applying the bandpass transformation with
  fractional bandwidth defined against f₀ vs against √(f₁f₂) — close enough to pass a
  glance, wrong enough to miss the spec edge.

**Homework (~3 h) — "Clean the band."** One story: lecture 1's radar receiver IF at
60 MHz needs a bandpass filter: 10 MHz passband ≤ 0.5 dB ripple, ≥ 40 dB rejection at
±25 MHz. Modules: (1) g-value engine (recursion, any N, both families) validated against
the scipy prototypes; (2) the synthesizer — order estimate, scale, transform to the
bandpass ladder; (3) the sweep — S₂₁/S₁₁ and group delay, spec table filled with
measured numbers. Predict first: Butterworth needs how many more sections than
0.5-dB-ripple Chebyshev for this spec? Referee: scipy prototypes to 1e-10; the analytic
Chebyshev rejection formula; skrf sweep.

**Success criterion.** g-values match scipy-derived references to 1e-8; synthesized
filter meets all three spec points in the skrf sweep with margins quoted; the
Butterworth-vs-Chebyshev order answer exact; predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 4 ch. 2 [R2]; Pozar ch. 8 [R1]; Cohn 1957 [R23];
Matthaei–Young–Jones [R18] (reference only).

---

## Lecture 9 — Filters II: distributed realizations

**Scope.** Turning lecture 8's ladders into copper: Richards' transformation (lumped ↔
commensurate lines), Kuroda identities (making the unbuildable buildable);
stepped-impedance lowpass (the quick-and-wide workhorse); coupled-line bandpass filters —
even/odd modes (lecture 7's investment pays off) and the J-inverter design procedure;
periodicity — distributed filters have reentrant passbands, and where they bite;
practical realities: junction discontinuities, why simulated ≠ fabricated, and what
full-wave EM adds (instructor openEMS case study of a coupled-line filter vs the ideal
model).

**Objectives.** Apply Richards + Kuroda to synthesize a stub lowpass; design a
stepped-impedance lowpass and know its rolloff limitations; design a coupled-line
bandpass from the g-values; predict reentrant passbands; articulate the ideal-vs-EM gap
and its sources.

**3-hour breakdown.**
- H1–H2 Principles: Richards' transformation as frequency mapping (fast) and as the
  deeper commensurate-line statement (first-principles); Kuroda worked as the four
  identities with one derived; stepped-impedance approximation and its validity limits;
  coupled-line section as an impedance/admittance inverter; the full coupled-line BPF
  procedure run on the board for N=3; reentrance explained with the Richards frequency
  circle; the EM-gap discussion with the openEMS case-study numbers on screen; war
  story: the fabricated filter 4% low — every length cut for ε_eff at DC, not f₀.
- H3 Tools: stepped-impedance designer swept in skrf `MLine`; coupled-line BPF designed
  by hand formulas, its ideal response swept (toolkit provides the coupled-line ABCD
  from even/odd impedances); the instructor's openEMS Touchstone loaded next to the
  ideal — the student sees the shift; deliberate bug: forgetting reentrance and
  declaring victory on a sweep that stopped at 2f₀.

**Homework (~3 h) — "Copper at last."** One story: realize lecture 8's IF filter
philosophy at microwave — a 2.4 GHz coupled-line bandpass (N=3, 0.5 dB ripple, 10%
fractional bandwidth) on RO4350B. Modules: (1) Richards/Kuroda stub lowpass at 3 GHz
(warm-up, exact at f₀ by construction); (2) coupled-line BPF synthesis — J-inverters →
even/odd impedances → (via toolkit's inverse-Hammerstad) physical dimensions; (3) sweep
0.1–10 GHz — spec table at f₀ *and* the reentrant passband located and reported.
Predict first: where exactly does the first reentrant passband land, and why there?
Referee: g-values from hw8's own validated engine; skrf sweep; the openEMS case-study
file as the "reality" overlay (provided).

**Success criterion.** Stub lowpass exact at f₀ (|S₂₁| dB within 0.01 of theory);
coupled-line BPF meets ripple/BW spec in the ideal sweep; reentrant passband located
within 1%; ideal-vs-EM deltas quoted from the provided case study; predictions
reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 4 chs. 2–3 [R2]; Pozar ch. 8.5–8.8 [R1]; openEMS case-study
files in `lessons/09-filters-distributed/lab/`.

---

## Lecture 10 — Noise & nonlinearity

**Scope.** Where noise comes from (thermal, shot, flicker in one slide); noise
temperature and noise figure, the 290 K convention and its fine print; Friis's cascade
formula — why the first stage rules; SNR through a receiver; antenna temperature and
G/T (the satellite/radar system metric); nonlinearity: compression (P_1dB), harmonics,
two-tone intermodulation, IP3, and the spur-free dynamic range; the linearity-noise
squeeze that defines receiver design; measuring NF and IP3 (Y-factor and two-tone in
concept).

**Objectives.** Convert among F, NF, T_e; cascade noise and IP3 through an arbitrary
chain; compute SFDR and identify which stage limits each end; place the LNA and the
attenuator pad correctly and defend the placement; connect kT₀B (lecture 1) to a real
receiver's sensitivity.

**3-hour breakdown.**
- H1–H2 Principles: thermal noise from the physics (fast: kTB asserted with the
  Johnson–Nyquist story; first-principles: available power from a resistor); NF defined
  the honest way (SNR degradation, source at 290 K); **Friis 1944 derived twice** and
  read from the original paper [R20]; cascade worked on three candidate front-ends;
  nonlinearity as a Taylor series — harmonics and IMD fall out of algebra; IP3 as an
  extrapolated fiction that predicts real spurs; cascade IP3; SFDR derived and drawn;
  the receiver squeeze; war story: the "improved" front-end with the LNA moved after
  the cable — 3 dB of system NF thrown away forever.
- H3 Tools: cascade engine (NF + IP3 + gain, any chain) in NumPy; the three candidate
  front-ends ranked live; two-tone simulation — an actual x + αx³ nonlinearity driven
  by two tones, FFT, the 3:1 spur growth measured; deliberate bug: cascading NF in dB
  (Friis needs linear) — plausible numbers, wrong answer, invariant check (system NF ≥
  first-stage NF... or is it) catches it.

**Homework (~3 h) — "The receiver budget."** One story: lecture 1's drone-detection
radar needs its receive chain designed: antenna → (cable, LNA, filter, mixer, IF amp)
in *some* order. Modules: (1) the cascade engine (gain/NF/IP3 element list → system
G/NF/IIP3/SFDR); (2) the shootout — all sensible orderings of the given five blocks
ranked by sensitivity and by SFDR, with the planted "obvious" ordering that's wrong;
(3) sensitivity — minimum detectable signal vs bandwidth, tying back to lecture 1's
detection range (the radar sees farther with the right chain — how much farther?).
Predict first: moving the 6-dB pad from the front to behind the LNA changes system NF
by how much? Referee: Friis limit cases (first-stage-dominant, lossy-first-element);
the two-tone FFT's measured spur slope.

**Success criterion.** Cascade engine matches hand-worked reference chains to 0.01 dB
in NF and 0.1 dB in IIP3; ordering verdicts match instructor's table; detection-range
delta computed correctly from the lecture-1 engine (imported, not rewritten);
predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 1 ch. 4 + Vol. 5 ch. 4 [R2]; Pozar ch. 10 [R1]; Friis 1944
[R20] (assign the original — 4 pages).

---

## Lecture 11 — Amplifier design & the LNA

**Scope.** The transistor as a measured two-port (we design with S-parameters, not
physics — and when that assumption cracks); power gains that matter (G_T, G_A, G_P) and
why S₂₁² is none of them; stability — K–Δ and μ, stability circles, and what
"conditionally stable" costs you; constant-gain and constant-noise circles; the
noise-match vs gain-match tension that defines the LNA; bias in one slide; a complete
single-stage LNA design procedure executed end-to-end on a real device's .s2p.

**Objectives.** Compute K, Δ, μ and draw stability circles from any .s2p; distinguish
and compute the three gains; design input/output matches for a gain target; run the
noise-vs-gain trade with Γ_opt; execute the full LNA procedure on a vendor device and
sanity-check against its datasheet.

**3-hour breakdown.**
- H1–H2 Principles: why measured S-parameters suffice (and the frequency limit of that
  claim); gain zoo derived from the signal-flow graph (fast: formulas; first-principles:
  Mason on the two-port flow graph — lecture 4's investment); stability derived — where
  the instability physically comes from (feedback through S₁₂), K–Δ and μ with the
  μ > 1 one-number verdict; circles constructed; noise circles and Γ_opt; the LNA
  procedure as a checklist; pre-empted misconception: "unconditionally stable means
  stable at the design frequency" — it means stable for *every* passive termination at
  that frequency; check the whole band, oscillators are built at the frequency you
  ignored.
- H3 Tools: a real Mini-Circuits MMIC .s2p (student-downloaded, part number and link in
  the README) loaded in skrf; K/Δ/μ computed across the file's whole band; stability
  and gain circles plotted on the Smith chart (lecture 3's chart, now earning rent);
  matches designed and cascaded, G_T measured; deliberate bug: designing at f₀ where
  μ > 1 while μ < 1 at 200 MHz — the "stable" amp that isn't.

**Homework (~3 h) — "Your first LNA."** One story: design a single-stage 2.4 GHz LNA
around a real vendor device (.s2p from Mini-Circuits; toolkit degrades gracefully if
the file is missing). Modules: (1) the stability audit — K/Δ/μ across the full file,
verdict per band, circles at three frequencies; (2) gain design — matches for a
G_T target 2 dB below G_T,max, verified by cascade; (3) the trade — with the provided
noise parameters, chart the gain-vs-NF frontier and pick a design point, defended in
one paragraph. Predict first: your gain match is not the noise match — moving to Γ_opt
costs how much G_T? Referee: μ-test vs K–Δ (two independent criteria must agree);
skrf-computed G_T vs the datasheet's typical gain at 2.4 GHz.

**Success criterion.** K/Δ/μ match skrf's built-ins to 1e-8; both stability criteria
agree everywhere; realized G_T within 0.1 dB of target in the cascade; the frontier
plot shows the expected monotone trade (human-read); predictions reconciled.

**Setup (Tier A).** Same env + one vendor .s2p download (link in lab README).

**References.** Steer Vol. 5 chs. 2–3 [R2]; Pozar chs. 11–12 [R1]; Gonzalez [R7]
(reference).

---

## Lecture 12 — Mixers, detectors & receiver architectures

**Scope.** Frequency conversion — why we do it (gain, filtering, and ADCs live at low
frequency) and what does it (nonlinearity or switching); the diode detector
(square-law) and the single-diode mixer; conversion loss, image frequency — the mirror
that folds noise and interferers onto your IF; superheterodyne architecture and
frequency planning (choosing the IF: image rejection vs filter difficulty);
direct-conversion and its DC/flicker demons in one slide; oscillators and phase noise
at system level (Leeson's insight, what phase noise does to Doppler radar — the
skirt that buries the slow drone); the FMCW dechirp receiver as "the mixer is the
ranging engine" (bridge to lecture 15).

**Objectives.** Explain conversion by trigonometry and by switching; compute image
frequencies and design an IF plan that survives a given interference environment; draft
a receiver block diagram with per-stage frequencies and levels; read a phase-noise plot
and compute its effect on a Doppler measurement; explain why FMCW radar is a mixer plus
an FFT.

**3-hour breakdown.**
- H1–H2 Principles: cos·cos algebra (fast) and the switching-mixer Fourier view
  (first-principles — why real mixers are switches); conversion loss accounting; the
  image derived, drawn, and *heard* (an audio-rate demo); superhet planning worked on
  the board for an X-band radar receiver: two candidate IFs, interference table,
  verdict; phase noise — Leeson qualitatively, dBc/Hz read from a plot, integrated
  into a Doppler error; the FMCW receiver diagram — transmit chirp, mix with echo,
  beat frequency IS range (the full derivation waits for lecture 15, the hardware
  insight lands now); war story: the radar that detected every airport shuttle bus —
  image response to the parking-lot Wi-Fi.
- H3 Tools: behavioral mixer in NumPy (ideal multiplier, then a switching mixer) —
  spectra before/after, image demonstrated by construction; frequency-plan calculator —
  feed it the band plan, get the spur/image table; phase-noise-corrupted Doppler
  simulation (toolkit provides the noise synthesis); deliberate bug: an IF plan that
  puts the image squarely on a strong known emitter — the plan "works" until the
  interference table is consulted.

**Homework (~3 h) — "The frequency plan."** One story: plan the receiver for the
course's X-band drone radar: RF 10.0–10.4 GHz, strong emitters at listed nearby bands,
ADC tops out at 100 MS/s. Modules: (1) the image/spur calculator (RF, LO, IF ±
harmonics to order 3); (2) the plan — choose high-side/low-side LO and IF, defend
against the emitter table, filter specs fall out (lecture 8's language); (3) Doppler
corruption — with the provided phase-noise profile, how slow a drone can this radar
still see? Predict first: high-side vs low-side LO flips the image to which band, and
which choice survives the emitter at 9.6 GHz? Referee: the trig identities (spur table
must match closed-form m·f_LO ± n·f_RF); the behavioral simulation's measured spectra.

**Success criterion.** Spur/image table matches closed form exactly to order 3; chosen
plan passes the interference audit (instructor's table); minimum detectable Doppler
within 5% of the analytic integrated-phase-noise bound; predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Steer Vol. 5 chs. 5–6 [R2]; Pozar ch. 13 [R1]; TI SPYY005 [R34]
(the FMCW receiver pictures).

---

## Lecture 13 — Antennas & arrays

**Scope.** The antenna as the transducer between circuits (Z, Γ — lectures 2–3) and
fields (pattern, gain — lecture 1's G finally earns its definition); fundamental
parameters: pattern, directivity, gain, efficiency, effective aperture, polarization;
the Friis formula closes its loop; workhorse elements in one pass each — dipole, patch
(design formulas provided), horn; **arrays as the main event**: the array factor
derived, element spacing and grating lobes, uniform-amplitude beamwidth and the
−13.2 dB sidelobe, tapering (raised-cosine, Chebyshev) and the beamwidth-vs-sidelobe
trade, phase steering (the phased array — lecture 16's hardware); pattern
multiplication; aperture-size intuition: beamwidth ≈ λ/D and what that means for a
drone-hunting radar's antenna.

**Objectives.** Compute directivity/gain/aperture and convert among them; predict AF
beamwidth, sidelobes, and grating-lobe onset from N, d, λ; design an amplitude taper
to a sidelobe spec and quote its beamwidth cost; steer a beam in phase and predict the
scan loss; size an aperture for a required angular resolution.

**3-hour breakdown.**
- H1–H2 Principles: parameters defined from the far-field picture (no vector-potential
  machinery — Orfanidis cited for the derivation); D ↔ A_eff ↔ beamwidth relations;
  the dipole and patch as data points, not derivations; array factor derived (fast:
  geometric series summed; first-principles: phasor picture on the board — N spokes
  closing); nulls, beamwidth, the sinc-like envelope, −13.2 dB; grating lobes from the
  same formula — the d > λ/2 crime and when radar designers commit it anyway; tapers
  as window functions (the DSP student's homecoming: it's the same mathematics as
  spectral leakage); steering = linear phase; scan loss; sizing worked example: what
  dish does it take to separate two drones 100 m apart at 5 km?
- H3 Tools: the array-factor engine in NumPy (it is 10 lines — written live);
  beamwidth/SLL measured from the sampled pattern vs closed forms; Chebyshev taper via
  `scipy.signal.windows.chebwin`, its exact SLL verified; steering animation across
  scan angles, grating lobe walking into view at the predicted angle; deliberate bug:
  pattern computed with degrees fed into `np.sin` — beautiful, plausible, wrong.
**Homework (~3 h) — "The aperture."** One story: size and shape the antenna for the
course radar: a 16-element linear array at 10 GHz. Modules: (1) the AF engine
(arbitrary weights/phases/spacing) with measured beamwidth/SLL/grating diagnostics;
(2) the taper study — uniform vs Chebyshev −30 dB: beamwidth cost, directivity cost
(toolkit integrates the pattern), and which one sees the drone next to the airliner
(two-target pattern overlay); (3) steering — scan to 45°, quote beam broadening and
grating margin vs d. Predict first: −30 dB Chebyshev broadens the −3 dB beamwidth by
what factor over uniform? Referee: closed-form uniform-array beamwidth and −13.2 dB
SLL; `chebwin`'s guaranteed equal-ripple sidelobes.

**Success criterion.** Measured uniform-AF SLL within 0.1 dB of −13.26 dB and
beamwidth within 1% of closed form; Chebyshev design hits −30 ± 0.2 dB SLL; grating
onset angle matches the formula to 0.1°; predictions reconciled.

**Setup (Tier A).** Same env.

**References.** Orfanidis chs. 15, 19–20 (free [R4]); Steer Vol. 1 antenna chapter
[R2]; Balanis [R11] (reference); Pozar ch. 14.1–14.3 [R1].

---

## Lecture 14 — The radar equation & detection

**Scope.** Lecture 1's radar equation, now with its parts understood (G from lecture
13, NF from lecture 10, B from lecture 8 — the course converges); radar cross section
σ — what it is physically, why it fluctuates, target-class numbers and stealth in one
honest slide (shaping + absorption, Balanis's RCS-reduction chapter cited); the
detection problem as hypothesis testing: noise statistics after the envelope detector
(Rayleigh/Rician), threshold setting, P_fa and P_d, the threshold-vs-sensitivity knife
edge; SNR required for (P_d, P_fa) — Albersheim's approximation; Swerling fluctuation
intuition; integration (coherent vs non-coherent) — why 10 pulses ≠ 10× range; CFAR —
why a fixed threshold dies in the real world and how cell-averaging CFAR adapts;
clutter in one slide (the ground is 60 dB bigger than the drone).

**Objectives.** Compute (P_d, P_fa) from SNR and back (Albersheim); set a threshold
for a specified P_fa from noise statistics; explain and implement CA-CFAR, including
its losses and its blindness (masking); quantify integration gain both ways; rank
target classes by detectability and articulate what stealth actually buys.

**3-hour breakdown.**
- H1–H2 Principles: the assembled radar equation with every term's home lecture named
  (the convergence slide); RCS phenomenology — the dBsm ladder from insect to airliner,
  fluctuation, the two stealth mechanisms; detection as decision theory (fast:
  threshold picture; first-principles: likelihood ratio in three lines, then honestly
  waved to Richards [R14]); Rayleigh false-alarm mathematics *worked exactly* —
  P_fa = exp(−T²/2σ²) invertible by hand; P_d vs SNR curves and Albersheim; the
  integration argument; CFAR derived from "estimate the noise where the target isn't";
  masking and the two-drone problem; war story: the coastal radar whose P_fa was set
  in the lab — sea clutter raised the floor 20 dB and the screen went white.
- H3 Tools: Monte Carlo detection in NumPy — noise draws, threshold from the exact
  Rayleigh inverse, measured P_fa vs designed (the student watches 10⁶ trials confirm
  a formula); P_d vs SNR sweep against Albersheim; CA-CFAR on a synthetic range
  profile with two targets and a clutter edge — detections, false alarms, and the
  masking failure demonstrated; deliberate bug: setting the threshold on power vs
  amplitude statistics — a factor-of-2 exponent error that turns P_fa = 10⁻⁶ into
  10⁻³ (the screen-goes-white bug, reproduced).

**Homework (~3 h) — "See it through the noise."** One story: the course radar (its
budget from hw10, its aperture from hw13) must detect the drone at a specified P_fa =
10⁻⁶. Modules: (1) threshold + Monte Carlo P_fa verification (exact Rayleigh inverse,
10⁶ trials); (2) P_d machinery — Albersheim vs Monte Carlo across SNR, then the
detection-range curves of lecture 1 redrawn with honest (P_d, P_fa) instead of a bare
SNR (how much range did the "13 dB" hand-wave hide?); (3) CA-CFAR — implement, run on
provided scenes (clean, clutter edge, two close drones), report P_fa/P_d/CFAR loss and
the masking case. Predict first: doubling the CFAR training window changes CFAR loss
and clutter-edge false alarms in which directions? Referee: the exact Rayleigh closed
form (planted truth); Albersheim's published accuracy envelope; scene ground truth.

**Success criterion.** Measured P_fa within 3σ binomial of 10⁻⁶ design at 10⁶ trials
(instructor's run recorded in performance.md); Monte Carlo P_d within 0.5 dB of
Albersheim across 6–16 dB SNR; CFAR results match instructor's on all three scenes;
predictions reconciled.

**Setup (Tier A).** Same env.

**References.** MIT LL lectures 2, 6 [R31]; Richards [R14] chs. 6–7 (reference); POMR
[R13] (reference); Balanis RCS chapter [R10] (stealth slide); Skolnik [R12].

---

## Lecture 15 — FMCW, Doppler & micro-Doppler

**Scope.** Why CW radar can't range and pulse radar struggles close-in — and how
frequency modulation fixes both; the FMCW chirp: transmit s(t), delayed echo, the
dechirp mixer (lecture 12's hardware), beat frequency f_b = 2Rα_c/c — range from a
frequency measurement; range resolution c/2B (bandwidth, not power, buys resolution);
Doppler f_d = 2v/λ; the two-chirp ambiguity and the chirp-sequence waveform: range
FFT × Doppler FFT = the range-Doppler map (the modern radar's retina); ambiguity and
resolution trades (T_c, N_chirps, B — the waveform designer's triangle); micro-Doppler:
rotating blades as phase modulation, the HERM-line spectrum with spacing N_b·f_rot,
why a drone and a bird separate on a spectrogram when they overlap on a blip; the
automotive 77 GHz FMCW world (collision avoidance preview).

**Objectives.** Derive f_b and the range mapping; design a chirp-sequence waveform to
range/velocity resolution + unambiguity specs; build and read a range-Doppler map;
explain STFT trade-offs; model blade micro-Doppler and predict HERM spacing; classify
drone vs bird from spectrogram structure.

**3-hour breakdown.**
- H1–H2 Principles: FMCW geometry on the f-t plane (fast: the two ramps); the dechirp
  algebra (first-principles: full phase expansion, the R-v coupling term kept honest);
  resolution c/2B derived from FFT bin width — the punchline "bandwidth is
  resolution"; the chirp-sequence 2-D processing derived as two DFTs with physical
  axes; the waveform-design triangle worked for the course radar's numbers; micro-
  Doppler: blade-tip phase modulation derived (fast: sinusoidal phase → Bessel
  sidebands; first-principles: the rotating-scatterer model of Chen [R24]); HERM
  spacing; the TI 77 GHz architecture as the industrial instance [R34]; war story:
  the wind farm that filled a surveillance radar's Doppler space with 200 m/s blade
  tips.
- H3 Tools: the full pipeline built live in NumPy on a synthetic scene with planted
  targets — chirp synthesis, delay/Doppler channel (toolkit), dechirp, range FFT,
  range-Doppler map with axes in meters and m/s; resolution verified against two
  targets one bin apart; drone blade model → `scipy.signal.stft` spectrogram, HERM
  lines measured against N_b·f_rot; deliberate bug: forgetting the window on the
  range FFT — a strong airliner's sidelobes bury the drone 30 dB down in the next
  10 cells (spectral leakage, lecture 13's taper lesson, now lethal).

**Homework (~3 h) — "The drone in the parking lot."** One story: a 77 GHz FMCW
sensor watches a scene: an airliner-sized reflector far out, a car, and a hovering
quadcopter. Modules: (1) waveform design — B, T_c, N_chirps to meet given resolution/
unambiguity specs (closed-form audit); (2) the pipeline — dechirp → windowed range
FFT → Doppler FFT → CFAR (imported from hw14) → target list with R, v; (3)
micro-Doppler — STFT of the quadcopter's cell, HERM spacing measured → blade count ×
rotation rate recovered. Predict first: the planted quadcopter hovers (v = 0) — where
does its *body* land on the range-Doppler map, and where do its blades? Referee: every
target's (R, v) is planted — errors must sit within one resolution cell; HERM spacing
vs N_b·f_rot exact by construction; Parseval through the FFT chain.

**Success criterion.** All planted targets recovered within one range and one Doppler
bin; measured HERM spacing within 2% of N_b·f_rot; the no-window vs window comparison
reproduces the buried-drone effect with numbers (instructor's deltas in
performance.md); predictions reconciled.

**Setup (Tier A).** Same env.

**References.** TI SPYY005 [R34]; Chen 2006 [R24] (course-pack) + Chen [R16]
(reference); Cai 2019 [R30] (free); MIT LL coffee-can course [R33]; Coluccia 2020
[R28] + arXiv survey [R29] (the drone-detection landscape).

---

## Lecture 16 — Beamforming, DOA & collision avoidance — capstone

**Scope.** The phased array closes the loop: steering vectors (lecture 13's AF as a
vector operation), beamforming as spatial filtering; conventional (delay-and-sum)
beamforming and beamscan DOA; the MVDR/Capon beamformer — adaptivity in one honest
derivation, and what it buys against interference (jamming, multipath); monopulse
angle refinement (lecture 7's comparator, now in software); MIMO radar in one slide —
why automotive sensors get N·M virtual elements from N+M channels; the collision-
avoidance stack: from detections to tracks (α-β filter — the honest minimum), closest
point of approach (CPA) and time-to-collision from (R, v, θ) streams; TCAS and
automotive AEB as the two industrial instances; the capstone: the whole course in one
pipeline — waveform → channel → front-end noise → array snapshots → range-Doppler →
CFAR → DOA → track → avoid/ignore decision.

**Objectives.** Form and steer beams from array snapshots; implement beamscan and
MVDR DOA and articulate when MVDR wins; refine angle by monopulse ratio; compute CPA
and time-to-collision from radar tracks and defend an alert threshold; assemble the
full sensing chain and identify which lecture owns each block's failure modes.

**3-hour breakdown.**
- H1–H2 Principles: the snapshot model x = A s + n built carefully (this is the
  wireless students' MIMO homecoming — say so); delay-and-sum (fast: steer and sum;
  first-principles: matched filter in space); beamscan DOA and its resolution = the
  beamwidth (lecture 13 closes); MVDR derived by constrained minimization (one
  Lagrange multiplier — kept clean), the interference-nulling picture, the sample-
  covariance caveat; monopulse ratio from Σ/Δ (lecture 7 closes); MIMO virtual array
  argument; tracking minimum: α-β filter equations and what they smooth; CPA/TTC
  geometry derived; alert logic and the false-alarm economics (lecture 14's P_fa,
  now with a cockpit attached); TCAS/AEB case studies from the literature [R25][R26].
- H3 Tools: array snapshot simulator (toolkit) → beamscan spectrum live; MVDR vs
  beamscan on two close sources + one jammer (the null appears on screen); monopulse
  refinement demo; the capstone pipeline assembled from the course's own homework
  modules (hw13 AF, hw14 CFAR, hw15 range-Doppler) — a multi-target scene flows
  end-to-end to avoid/ignore verdicts; pyargus cross-check of the DOA estimates;
  deliberate bug: MVDR with a covariance estimated from too few snapshots — the
  adaptive beamformer that nulls its own target (diagonal loading as the fix).

**Homework (~3 h) — "Detect, locate, avoid."** The capstone story: a 16-element
77 GHz array guards a corridor; scenes contain crossing drones, a fast fixed-wing
intruder, and (scene 3) a jammer. Modules: (1) DOA — beamscan + MVDR on provided
snapshots, resolution and jammer cases compared; (2) the chain — plug DOA into the
hw15 pipeline's output for full (R, v, θ) target lists per frame; (3) avoid — α-β
track (toolkit), CPA/TTC per target, alert decisions against the given threshold,
defended in ANSWERS.md against both miss and false-alarm costs. Predict first: two
drones 1.5 beamwidths apart — does beamscan separate them? does MVDR? at what SNR
does your answer flip? Referee: pyargus DOA on identical snapshots; planted scene
truth (all trajectories known); CPA closed form.

**Success criterion.** Beamscan/MVDR DOA within 0.5° of pyargus on identical
snapshots; all planted intruders tracked with CPA error < 5 m; alert decisions match
the instructor's truth table on all scenes (including the correct *non*-alert);
predictions reconciled.

**Setup (Tier A).** Same env + `pip install pyargus`.

**References.** Orfanidis arrays chapters [R4]; Patole 2017 [R26]; Hasch 2012 [R25];
Mailloux [R17] (reference); MIT LL tracking lecture [R31]; arXiv UAV survey [R29].

---

## Coverage check (vs survey)

Survey §1.4.1 invariant core: transmission lines ✔ (L2), Smith chart + matching ✔
(L3, L6), network/S-parameters ✔ (L4), guided media ✔ (L5), dividers/couplers ✔ (L7),
resonators ✔ (L6), filters ✔ (L8–9, two sessions — the survey's "standard casualty of
schedule pressure" given room instead), detectors/mixers ✔ (L12), amplifier + noise ✔
(L10–11), receiver/system close-out ✔ (L12, and globally via the radar thread).
Oscillators/PAs/synthesis: correctly left to a second course per survey precedent;
oscillator phase noise covered at system level in L12.

Survey §1.4.4 headroom spent on the radar thread ✔ (L13–16: aperture → detection →
FMCW/micro-Doppler → beamforming/avoidance), using the verified source material (MIT
LL [R31][R33], OSU 5013's topic proportions, TI [R34], open drone literature
[R28][R29][R30]).

Survey §2.4 free-readings rule ✔ — every required reading maps to Steer [R2]/[R3],
Orfanidis [R4], or free radar material; Pozar chapters listed alongside throughout.

Survey §3 tool verdicts ✔ — scikit-rf 1.13.0 spine (all lectures; §3.6 risk 0
supersedes the survey's original 2.0.1 recommendation), physics-invariant
and planted-truth referees (L4, L14–16), vendor .s2p student-downloaded (L11),
full-wave as instructor demo only (L5, L9), pyargus confined to L16, no Tier-B/C
dependencies anywhere.

Instructor-profile fits: wireless-comms bridge opens the course (L1 link budgets →
radar equation); MIMO/beamforming homecoming named in L16; detection thread touches
L1, L10, L12 (Doppler/phase noise), L13 (two-target aperture), and owns L14–16.
