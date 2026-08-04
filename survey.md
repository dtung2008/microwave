# Survey — Microwave Engineering Foundation Course

Web-verified 2026-08-04 (three parallel research passes: university courses, textbooks &
literature, software tools). This document is the evidence base for [syllabus.md](syllabus.md);
the syllabus ends with a coverage check against §4 of this file. Convention: facts below were
checked against live web sources on the access date unless marked *(settled record — not
re-verified)* or *(inferred)*.

Course being designed: **16 lectures × 3 hours** (48 contact hours), senior-undergrad /
first-year-grad, three emphases — theory background, applications, software/simulation —
with the applications thread anchored on **radar detection of aircraft/missiles/drones and
navigation collision avoidance**. Instructor background: wireless communications.

---

## 1. What top universities teach

### 1.1 Circuit-oriented microwave foundation courses (the direct comparables)

| Course | Level | Text | Software/lab | Notes |
|---|---|---|---|---|
| Michigan EECS 411 — Microwave Circuits | senior/grad | Pozar | ADS + Momentum, VNA, fab 1–10 GHz | Capstone: receiver front-end assembled from parts designed during term |
| UCSD ECE 166 — Microwave Systems & Circuits | senior | Pozar | ADS, microstrip design/fab/test | One quarter reaches LNA, NF, IP3 |
| Georgia Tech ECE 6360 — Microwave Design (Sp 2026 syllabus obtained) | grad | Collin or Pozar; Steer/Sarabandi as free alternatives | ADS + HFSS taught weeks 1–6; MATLAB (RF + Phased Array toolboxes); 3–4 simulation projects = 20% | Project-based, no final exam |
| UMass ECE 584 (Pozar's home course) | grad | Pozar | Pozar's own lab notebook: slotted line, VNA, matching, cavities | Measurement-first |
| Texas A&M ECEN 452 — UHF Techniques | senior | — | — | S/ABCD, matching, passive design |
| UCLA EE 163A — Introductory Microwave Circuits | senior | Pozar *(inferred)* | — | Lines, matching, dividers, couplers, amps |
| Colorado ECEN 4634/5634 — Microwave & RF Lab | senior/grad | Popovic & Kuester notes | ~10 bench experiments: VNA cal, TDR, waveguide, antenna, **radar + superheterodyne labs** | The national reference for measurement-first delivery |
| UIUC ECE 453 → 447 | senior → grad | notes → Gonzalez | full RF bench; labs 50% of 447 grade | Systems/receiver course first, active design second |
| Berkeley EE 142/242A — RFIC | senior/grad | course notes | labs | RFIC/comms-circuit flavor, not Pozar-passive |

### 1.2 Field-oriented courses (the other track)

MIT 6.013 / 6.630 (Staelin free notes; Kong), Stanford EE 242 — Maxwell-first, modal
analysis, Green's functions; feeds antenna/EM research. **No surveyed field-track course
carries the Smith-chart-to-amplifier design arc.** Standard verdict: the foundation design
course is Pozar-organized; Collin is the rigor reference.

### 1.3 Radar courses (the applications source material)

- **MIT OCW RES.LL-001** (Lincoln Lab, 10 lectures, free video+slides): radar equation with
  design examples, propagation, RCS, waveforms, antennas, TX/RX, detection in noise.
- **MIT OCW RES.LL-003 "Build a Small Radar System"** (coffee-can FMCW kit, ~$360): proof
  that the complete FMCW arc — ranging, Doppler, SAR — is teachable in ~9 contact hours.
- **Ohio State ECE 5013** (official description obtained): Richards/Scheer/Holm POMR text;
  ~38 h: radar equation/detection/clutter (12 h), MTI/pulse-Doppler, pulse compression,
  CW/FM, tracking, arrays, SAR; **MATLAB projects 25% of grade, no hardware lab** — the
  proof that a radar course can be simulation-graded.
- **radar-course.org** (O'Donnell / IEEE AESS, 19 lectures, 1300+ slides, free).
- Georgia Tech GTPE short-course family (*Principles of Modern Radar*, 40+ years running)
  shows radar packs well into short contact-hour blocks.

### 1.4 Synthesis of §1

1. **The invariant core sequence** (every circuit-oriented foundation course, same order):
   transmission lines → Smith chart + matching → network/S-parameters → guided media
   (microstrip, waveguide) → dividers/couplers → resonators + filters (the topic most often
   squeezed) → diode detectors/mixers → transistor amplifier design + noise → receiver/system
   close-out. Oscillators, PAs, synthesis belong to course 2 almost everywhere.
2. **Software delivery models observed:** (a) commercial EDA as first-class citizen (GT 6360:
   ADS+HFSS tutorials then graded simulation projects — the model for a no-bench course);
   (b) measurement lab as core (Colorado, Stanford EE 344); (c) MATLAB/Python as systems glue
   (GT homework, OSU projects, MIT LL notebooks). Open-source tools appear in **no** verified
   top-program syllabus — an opportunity, not a precedent.
3. **Radar in the foundation course:** nowhere. Radar is a framing device (GT week 1) or a
   separate course (OSU 5013). **No surveyed university integrates a real detection/radar
   unit into the microwave foundation course itself** — the building blocks exist but live in
   separate courses. This course's 12-core + 4-radar design is a genuine differentiator.
4. **What 48 h buys over the ~40 h semester:** the full invariant core plus ~3–4 sessions.
   Spent here on the radar/detection thread (radar equation + detection, FMCW/Doppler/
   micro-Doppler, arrays/beamforming/collision avoidance) — the option best matched to the
   instructor's interests, with OSU 5013 / MIT LL / coffee-can as verified source material.
5. **The 3-hour block is an asset:** every strong course splits theory from tool time;
   3-hour sessions support Principles → Tools every week (the format this course inherits
   from `../optimizations`, agreed 2026-07-31).

---

## 2. Textbooks and literature

### 2.1 Core texts

- **Pozar, *Microwave Engineering*, 4th ed., Wiley 2011** — still the current edition
  (no 5th as of Aug 2026). The de facto syllabus template for exactly this course type;
  4e added the noise/nonlinearity and active chapters that suit a comms-oriented author.
  No legal free PDF → the "buy one book" option.
- **Steer, *Microwave and RF Design*, 3rd ed., 2019 — 5 volumes, open access (NC State/UNC
  Press)**: Vol 1 Radio Systems, Vol 2 Transmission Lines, Vol 3 Networks, Vol 4 Modules,
  Vol 5 Amplifiers and Oscillators; plus the single-volume *Fundamentals* condensation.
  Free PDFs: <https://repository.lib.ncsu.edu/handle/1840.20/36776>; HTML on LibreTexts.
  **The free co-primary text — every required reading in this course maps to Steer or
  Orfanidis.**
- **Orfanidis, *Electromagnetic Waves and Antennas*** (Rutgers, free, author-licensed,
  MATLAB-integrated): <https://www.ece.rutgers.edu/~orfanidi/ewa/>. Plane waves, multilayer
  matching, lines, S-parameters, arrays, apertures. **The free EM/antenna companion.**
- Collin *Foundations for Microwave Engineering* 2e (rigor reference); Ludwig & Bogdanov
  *RF Circuit Design* 2e (gentler on-ramp); Gonzalez *Microwave Transistor Amplifiers* 2e
  (amplifier lectures); Ramo/Whinnery/Van Duzer (fields-to-circuits classic); Ulaby 8e
  (undergrad EM refresher); Balanis *Advanced Engineering EM* 3e 2024 (new RCS-reduction/
  metasurface chapter — cite in the stealth/detection discussion); Balanis *Antenna Theory*
  4e 2016. *(settled record for editions except where dated above)*

### 2.2 Radar and detection

- Skolnik *Introduction to Radar Systems* 3e (classic narrative); Richards *Fundamentals of
  Radar Signal Processing* 2e (Doppler/pulse-compression/CFAR mathematics); Richards, Scheer,
  Holm *Principles of Modern Radar Vol. I* (the modern classroom text, MATLAB supplements);
  Mahafza *Radar Systems Analysis and Design Using MATLAB* 4e 2022 (homework scaffold
  goldmine); Levanon & Mozeson *Radar Signals* (waveforms/ambiguity); Chen *The Micro-Doppler
  Effect in Radar* 2e 2019 (the book on rotor/human micro-Doppler modeling).
- **Free radar course material** (carries the whole radar thread at zero cost): MIT OCW
  RES.LL-001, RES.LL-003, radar-course.org, MIT LL `radar-intro` Jupyter lectures
  (<https://github.com/mit-ll/radar-intro>).
- **FMCW/mmWave industry tutorials (free, current):** TI SPYY005 "The Fundamentals of
  Millimeter Wave Radar Sensors" (<https://www.ti.com/lit/spyy005>) — the cleanest short
  FMCW range/velocity/angle derivation in print; TI Radar Academy mmWave training series;
  Infineon "Understanding FMCW Radars" KB articles.
- **Drone/UAV detection (open access):** Coluccia, Parisi, Fascista, "Detection and
  Classification of Multirotor Drones in Radar Sensor Networks: A Review," *Sensors* 20(15)
  :4172, 2020 (<https://www.mdpi.com/1424-8220/20/15/4172>); Taha & Shoufan, *IEEE Access*
  7:138669, 2019; "A Survey on Detection, Classification, and Tracking of UAVs," arXiv:
  2402.05909 (2024); Cai et al., "Simulation of Radar Micro-Doppler Patterns for
  Multi-Propeller Drones," RADAR 2019
  (<https://okrasnov.github.io/pdf/YCai-etal-2019-RADAR.pdf>). Seminal paper: Chen, Li, Ho,
  Wechsler, "Micro-Doppler Effect in Radar," *IEEE Trans. AES* 42(1):2–21, 2006 (paywalled).
- **Automotive / collision avoidance:** Patole et al., "Automotive Radars: A Review of
  Signal Processing Techniques," *IEEE SPM* 34(2), 2017; Hasch et al., "Millimeter-Wave
  Technology for Automotive Radar Sensors in the 77 GHz Band," *IEEE TMTT* 60(3), 2012.

### 2.3 Classic papers worth assigning

Smith 1939/1944 (the chart, *Electronics*); Friis 1944 (noise figure, *Proc. IRE*); Friis
1946 (transmission formula, 2 pages); Wheeler 1947 (small antennas) and 1965 (microstrip
strips); Cohn 1957 (direct-coupled resonator filters); Matthaei–Young–Jones 1964 (the filter
"bible," reference only). *(settled record)*

### 2.4 Synthesis of §2

Structure the lectures on the Pozar topic sequence; make every **required** reading a free
Steer/Orfanidis link with Pozar chapter numbers alongside for students who buy it. The radar
thread runs entirely on free material (MIT LL + TI + open-access surveys). The only gaps in
an all-free stack — Collin-grade waveguide rigor and a free filter-synthesis handbook — are
tolerable at foundation depth (Steer Vol 3 covers practical filter design).

---

## 3. Software and simulation tools

Constraints inherited from the prior courses: Tier A = pip on a student laptop (Win/macOS/
Linux), CPU-only, no commercial licenses; Python 3.12 exactly; **numpy pinned 1.26.4**
(Windows Smart App Control blocks numpy 2.5 DLLs — incident inherited from robotics).

### 3.1 The spine: scikit-rf

- **scikit-rf 2.0.1** (PyPI, released 2026-07-03; production/stable; BSD; two active
  maintainers). Pure Python; `numpy>=1.21` (verified in pyproject.toml) — **compatible with
  the 1.26.4 pin**. 2.0 is a fresh major (plotting helpers moved `util`→`plotting`, lazy
  loading) → the survey originally recommended pinning 2.0.1; **superseded by §3.6
  risk 0** (2.0.x import-crashes under numpy 1.26.4 — the course pins **1.13.0**).
- Capabilities used by this course: `Network` (S/Z/Y/ABCD conversions, Touchstone I/O,
  cascading via `**`), `Circuit` (multiport interconnection), Smith plotting
  (`plot_s_smith`), calibration (SOLT/TRL), `VectorFitting`, time gating, `Qfactor`, and
  the media module: `DefinedGammaZ0`, `DistributedCircuit` (RLGC), `MLine` (Hammerstad–
  Jensen + dispersion), `CPW`, `Coaxial`, `RectangularWaveguide`, `CircularWaveguide`,
  `Freespace`. **Gap:** no coupled-line media class — students hand-roll even/odd-mode
  analysis (refereed by published design tables / Qucs-S).

### 3.2 Full-wave EM — honest verdict: not Tier A on Windows

- **openEMS**: free FDTD with Windows binaries, but off-PyPI (bundled local wheels), and
  stable v0.0.36 ships wheels for **Python 3.10/3.11 only** — misses this course's 3.12
  pin. → instructor-run case studies only; students post-process the exported Touchstone/
  field files in scikit-rf.
- **MEEP**: no native Windows (conda-forge Linux/macOS). **gprMax**: source build.
  **emopt**: PETSc/MPI, Linux-only in practice. **radarsimpy**: freemium binary blob,
  non-pip, **requires numpy ≥ 2.0** — conflicts with the pin; excluded (Colab mention only).
- **flaport/fdtd** (`pip install fdtd`): pure-Python 3D FDTD, numpy backend — the one
  Tier-A full-wave citizen, but educational (no ports/S-parameter extraction). Good for
  *visualizing* cutoff, standing waves, radiation; not for quantitative design.
- **PyNEC**: pip install broken on Windows (no wheels, needs SWIG); skip or Colab.
- Commercial tier (ADS, HFSS, CST, AWR): mentioned in lectures as the industrial reality,
  never required.

### 3.3 Other components

- **Filter synthesis:** no maintained pip package exists — pedagogically better anyway:
  students hand-roll g-value recursions, scaling, Richards/Kuroda, refereed by Pozar's
  closed-form tables + `scipy.signal` prototypes (`cheb1ap`, `buttap`) + skrf simulation.
- **Radar labs:** roll-your-own numpy/scipy is fully viable and the right call — chirp
  synthesis, dechirp, range FFT, range–Doppler map, CA-CFAR, STFT spectrograms are each
  20–50 lines; `scipy.signal` provides `stft`, windows (`chebwin`, `taylor`), `chirp`.
  Planted analytic ground truth (f_b = 2Rα/c, f_d = 2v/λ, HERM-line spacing = N_b·f_rot)
  makes the referee free. Drone-propeller micro-Doppler: rotating point-scatterer blade
  model, well documented in open literature (Cai 2019; Chen 2006).
- **Array processing:** `pyargus` (pip) for beamforming/DoA referee; array factor itself is
  10 lines of numpy + closed-form beamwidth/SLL referees. `arraytool` is dormant — avoid.
- **Smith charts:** skrf built-ins are the course standard; `pysmithchart` (maintained
  descendant of pySmithPlot) optional for standalone charts.
- **Qucs-S 26.x** (free, GPL, Qt6, bundles ngspice+QucsatorRF): optional GUI schematic
  cross-check for filters/matching/amps; never graded. QucsStudio: closed, Windows-only —
  mention only.
- **Real measured data:** vendor Touchstone files as homework "measurement" — Coilcraft
  (.s2p for every RF inductor), Murata SimSurfing, Mini-Circuits (per-product S2P zips,
  e.g. GALI-2+ MMIC amp). **Students download from vendor pages themselves** (redistribution
  terms vary — never bundle in the repo). Gold pattern: real MMIC .s2p → K/μ stability,
  gain circles; real 100 nH inductor .s2p vs ideal jωL → why the matching network detunes.

### 3.4 Referee map (topic → student hand-rolls → independent referee)

| Topic | Hand-rolled | Referee |
|---|---|---|
| Transmission lines | telegrapher, Γ, VSWR, ABCD cascade | skrf `DistributedCircuit` / analytic |
| Smith chart, matching | chart moves, stub/L-section design | skrf cascade at f₀; chart invariants |
| S-parameters | conversions, cascades | physics: reciprocity S=Sᵀ, passivity I−SᴴS⪰0, lossless unitarity |
| Microstrip | Hammerstad Z₀/εeff | skrf `MLine` (independent implementation) |
| Waveguide | cutoff, dispersion | skrf `RectangularWaveguide`; f_c = c/2a |
| Resonators | 3-dB Q extraction | skrf `Qfactor` fit |
| Filters | g-values, transformations, distributed realization | Pozar tables; `scipy.signal` prototypes; skrf sim |
| Amplifiers | K–Δ, gain/noise circles | μ-test cross-check; vendor datasheet spot values |
| Noise cascade | Friis formula | limit cases; skrf noisy networks |
| Arrays | array factor, tapers | closed-form beamwidth/SLL; pyargus |
| FMCW/Doppler | full pipeline | planted ground truth; Parseval through the FFT chain |
| Micro-Doppler | blade model + STFT | HERM spacing = N_b·f_rot analytic |
| Link/radar budgets | Friis + radar equation in dB | dimensional/limit checks; skrf `Freespace` |

### 3.5 Recommended Tier-A stack

```
numpy==1.26.4        # pinned — Smart App Control incident; locks Python <= 3.12
scipy>=1.11,<1.14
matplotlib>=3.8,<3.11
pandas
scikit-rf==1.13.0    # pinned — see §3.6 risk 0: 2.0.x (the survey's original pick)
                     # crashes on import under numpy 1.26.4; 1.13.0 is the last 1.x
# optional, per lecture:
pysmithchart         # standalone Smith charts (skrf built-in usually suffices)
fdtd                 # pure-python FDTD field-visualization demos
pyargus              # array DSP / DoA referee (lecture 16)
```

Install guide must say **"Python 3.12, exactly"** — 3.13/3.14 users fail at numpy.

### 3.6 Risks

0. **Post-survey install finding (2026-08-04, this machine): scikit-rf 2.0.0/2.0.1 crash
   on plain `import skrf` under numpy 1.26.4** — `calibration.py:149` evaluates
   `np.typing.NDArray` at import time and numpy 1.26 does not auto-expose `numpy.typing`
   (the claim "numpy>=1.21 compatible" in pyproject is not true in practice; it only
   appears to work when another package, e.g. pandas, has already imported numpy.typing
   in the same process). **Course pin changed to `scikit-rf==1.13.0`** (last 1.x; plain
   import verified clean; all course APIs — MLine, CPW, RectangularWaveguide,
   DistributedCircuit, Freespace, Qfactor, Circuit, skrf.data — present). Revisit 2.x
   only if the course ever moves to numpy ≥ 2.
1. scikit-rf 2.0 is weeks old — superseded by risk 0: course pins 1.13.0.
2. numpy 1.26.4 locks Python ≤3.12 — say so loudly in every README.
3. openEMS/PyNEC/radarsimpy are not Tier-A — keep demo/optional, never graded.
4. Vendor .s2p redistribution — students download, repo never bundles.
5. Qucs-S is optional GUI — keep non-graded so non-installers aren't penalized.

---

## 4. Course-design conclusions (audited by syllabus.md)

1. Pozar-organized 12-lecture core covering the invariant sequence (§1.4.1), free readings
   from Steer/Orfanidis, Pozar chapters listed for buyers.
2. A 4-lecture radar/systems thread (antennas/arrays → radar equation/detection →
   FMCW/Doppler/micro-Doppler drone case study → beamforming/DOA/collision avoidance) —
   the differentiator no surveyed course offers (§1.4.3), built on free MIT LL/TI/
   open-access material (§2.2).
3. Hours 1–2 Principles → Hour 3 Tools format; all practice in ≤3 h story-homework with
   prediction-first ANSWERS.md (inherited contracts, ported in AUTHORING.md and
   HOMEWORK-PRINCIPLES.md).
4. Tier-A pip-only graded labs on the scikit-rf spine (§3.5); full-wave as instructor-run
   openEMS case studies (§3.2); commercial EDA mentioned as industrial context only.
5. Physics invariants + planted analytic ground truth + vendor measured data implement the
   referee principle across all 16 lectures (§3.4).
6. Wireless-comms bridge: lecture 1 opens from link budgets (the instructor's and likely
   students' home turf) and lands on the radar equation, so the radar thread is seeded on
   day one.

---

## Sources (accessed 2026-08-04)

Course pages / syllabi: GT ECE 6360 Sp2026 syllabus PDF (syllabus.gatech.edu); OSU ECE 5013
description PDF (ece.osu.edu); UIUC ECE 447 Sp2025 + ECE 453 archive (courses.grainger.
illinois.edu); MIT OCW 6.013, 6.630, RES.LL-001, RES.LL-003 (ocw.mit.edu); MIT LL radar-intro
(github.com/mit-ll/radar-intro); UCSD catalog (catalog.ucsd.edu); Michigan EECS 411/430
(ece.engin.umich.edu); Berkeley EE 117 + 242A (eecs.berkeley.edu, rfic.eecs.berkeley.edu);
UCLA ECE listings (seasoasa.ucla.edu); Stanford ExploreCourses EE 242/344; Colorado ECEN
4634/5634 (colorado.edu, catalog archive); UMass ECE 584 (ece.umass.edu) + Pozar lab notebook
mirror; TAMU catalog; GT Professional Education radar courses (pe.gatech.edu).

Texts: Wiley (Pozar, Balanis), NC State repository + LibreTexts (Steer), Rutgers (Orfanidis),
Pearson (Ulaby), IET Digital Library (POMR), Routledge (Mahafza 4e), Artech (Chen 2e,
Mailloux 3e).

Radar/apps: ti.com/lit/spyy005; TI Radar Academy; Infineon community KB; mdpi.com (Sensors
drone review); arXiv 2402.05909, 2409.05985, 2307.10326; okrasnov.github.io (Cai 2019);
radar-course.org.

Tools: pypi.org/project/scikit-rf (2.0.1); github.com/scikit-rf/scikit-rf (pyproject.toml,
skrf/media listing); docs.openems.de + github.com/thliebig/openEMS-Project/releases;
meep.readthedocs.io; github.com/gprMax/gprMax; emopt.readthedocs.io; github.com/flaport/fdtd;
radarsimx.github.io (install + dependence pages); github.com/ra3xdh/qucs_s/releases;
github.com/tmolteno/python-necpp (issue #31, Windows build failure); github.com/zinka/
arraytool; pypi.org/project/pysmithchart; pypi.org/project/pyargus; coilcraft.com models
page; murata.com SimSurfing; minicircuits.com product S2P zips.

Known gaps: UCSD 166 and Michigan 411 current syllabi are login-walled (catalog + archived
materials used); scikit-rf GitHub releases page showed contradictory dates vs PyPI (PyPI
treated as authoritative); openEMS Python-3.12 wheel status may change — re-check before any
future decision to promote full-wave beyond demo tier.
