# AUTHORING.md — lecture template & conventions

Contract for authoring lectures 2–16. Lecture 1 (`lessons/01-systems-panorama/`) is the
gold reference — match its structure, tone, and depth. Syllabus scope per lecture:
[syllabus.md](syllabus.md). References/versions: [survey.md](survey.md). Homework design:
[HOMEWORK-PRINCIPLES.md](HOMEWORK-PRINCIPLES.md). Inherited from the optimizations course
(`../optimizations/AUTHORING.md`), which inherited from robotics, with the format agreed
2026-07-31: **Hours 1–2 Principles → Hour 3 Tools; practice lives in homework, not in
class.**

## Folder layout (per lecture `NN-slug/`)

```
lessons/NN-slug/
  script.en.md            # full 3-hour teaching script, English
  script.zh-hant.md       # parallel script, Traditional Chinese (Taiwan terminology)
  slides/principles.en.html  # self-contained deck for hours 1-2 (principles)
  lab/
    README.md             # install (per-OS), files table, troubleshooting
    setup_check.py        # pre-class env verification -> prints "SETUP OK"
    hour3_walkthrough.py  # live-coding cells (# %% percent format), mirrors script hour 3
    HOMEWORK.md           # the homework sheet: story, modules, commands, toolkit
    ANSWERS.md            # student answer sheet: prediction-first questions
    hwN_starter.py        # student TODO modules + toolkit + --check (measured facts)
    VERIFY.md             # instructor-side mechanical verification steps
    solutions/hwN_solution.py   # instructor solution; imports the starter's harness
    solutions/ANSWERS-key.md    # instructor answer key with the reasoning
```

## Script format (both languages)

- Header block: duration (3 h = three ~50-min segments, 10-min break/hour), delivery
  tier (all Tier A in this course), prerequisites, pre-class setup command + expected
  output.
- **Hours 1–2 — Principles**: timed sections (`### N.N Title (0:00–0:08)`; hour-1
  sections numbered 1.x, hour-2 sections 2.x), spoken-prose teaching beats, slide cues,
  claims up front, war stories, and *pre-empted student misconceptions* (state the
  question students will ask, answer it in the script). Derivations done twice where the
  lecture affords it — a fast version and a first-principles version, the second framed
  as explaining the first. Every formula lands as a number the student will later print.
- **Hour 3 — Tools**: live-coding walkthrough that mirrors `hour3_walkthrough.py`
  cell-for-cell; includes a deliberate-bug demo where the lecture affords one
  (lecture 1: adding raw watts to dBm mid-budget — the classic unit-mixing betrayal).
  Ends with the homework brief (~10 min): walk the story, the modules, the prediction
  questions, and the commands on screen; then wrap-up recap + next-lecture teaser.
- **References**: 3–6, matching syllabus.md, with URLs; prefer free texts; cite
  [references/references.md](references/references.md) keys. Required readings point at
  free sources (Steer [R2]/[R3], Orfanidis [R4]); give the Pozar [R1] chapter alongside
  for students who bought it.

zh-Hant script: parallel content, not literal translation. Standard Taiwan terminology
with English term in parentheses on first use. Code, identifiers, and paper titles stay
English. Established glossary: 微波工程 (microwave engineering), 傳輸線 (transmission
line), 特性阻抗 (characteristic impedance), 反射係數 (reflection coefficient), 駐波比
(standing wave ratio, SWR), 史密斯圖 (Smith chart), 阻抗匹配 (impedance matching),
單支節匹配 (single-stub matching), 四分之一波長轉換器 (quarter-wave transformer),
散射參數 (scattering parameters, S-parameters), 互易性 (reciprocity), 無損網路
(lossless network), 微帶線 (microstrip), 共平面波導 (coplanar waveguide, CPW), 波導
(waveguide), 截止頻率 (cutoff frequency), 色散 (dispersion), 諧振器 (resonator),
品質因數 (quality factor, Q), 功率分配器 (power divider), 定向耦合器 (directional
coupler), 混合環 (hybrid), 濾波器 (filter), 插入損耗 (insertion loss), 切比雪夫
(Chebyshev), 雜訊指數 (noise figure), 三階交調截點 (third-order intercept, IP3),
動態範圍 (dynamic range), 穩定係數 (stability factor), 低雜訊放大器 (low-noise
amplifier, LNA), 混頻器 (mixer), 本地振盪器 (local oscillator), 超外差 (superheterodyne),
鏡像頻率 (image frequency), 相位雜訊 (phase noise), 天線 (antenna), 陣列因子 (array
factor), 波束寬度 (beamwidth), 旁瓣 (sidelobe), 相位陣列 (phased array), 波束成形
(beamforming), 波束掃描 (beam steering), 到達方向 (direction of arrival, DOA), 雷達
(radar), 雷達方程式 (radar equation), 雷達截面積 (radar cross section, RCS), 都卜勒效應
(Doppler effect), 微都卜勒 (micro-Doppler), 調頻連續波 (frequency-modulated continuous
wave, FMCW), 啁啾 (chirp), 差拍頻率 (beat frequency), 距離-都卜勒圖 (range-Doppler map),
匹配濾波器 (matched filter), 脈衝壓縮 (pulse compression), 虛警率 (false-alarm rate),
偵測機率 (detection probability), 恆虛警率偵測 (constant false-alarm rate, CFAR),
鏈路預算 (link budget), 自由空間路徑損耗 (free-space path loss), 等效全向輻射功率
(EIRP), 雜訊底線 (noise floor), 訊號雜訊比 (signal-to-noise ratio, SNR), 無人機
(drone/UAV), 避撞 (collision avoidance).

## Slides (`slides/principles.en.html`)

- Copy lecture 1's `<style>` block and nav `<script>` verbatim (they descend from the
  optimizations/robotics courses — includes the `.od` over-dot class); change only
  content sections. Self-contained: no CDN, no external fonts/images; inline SVG for
  diagrams (Smith charts, line sections, spectra).
- One deck covers both principle hours: 22–30 slides ≈ 100 minutes, with a visible
  hour boundary (a "Hour 2" divider slide after the ~50-minute mark). Conventions:
  `.kicker` section labels, `.box rule` (blue) for rules/theorems, `.box trap` (red)
  for pitfalls, recap slide last.
- Math in HTML/Unicode (sup/sub, `.mat` bracket grids). **Never Unicode combining
  marks** — use the `.od` class for dotted rates. Quantify every symbol on the slide
  where it first appears (no unexplained letters — students will ask).
- **Acronym rule (inherited):** every acronym's FIRST appearance in a lecture's deck
  carries its full name on that slide — inline parenthetical on busy slides
  (`SWR (standing wave ratio)`), a small muted footnote when several expansions cluster.
  Applies to SWR/VNA/LNA/NF/IP3/FMCW/RCS/CFAR/SNR/EIRP/DOA/MMIC/CPW/TEM/… — anything
  abbreviated. Slides must never overflow to fit a footnote — the template scrolls as a
  safety net, but scrolling in a live lecture is a design failure.

## Notation ledger (course-wide; extend, never contradict)

Follows Pozar [R1] wherever it has a convention.

| Symbol | Meaning |
|---|---|
| Z₀ | characteristic impedance (50 Ω unless stated) |
| Z_L, Z_in | load / input impedance; lowercase z = normalized (z = Z/Z₀) |
| Γ | reflection coefficient; SWR = (1+|Γ|)/(1−|Γ|) |
| γ = α + jβ | propagation constant (α nepers/m, β rad/m); λ = 2π/β |
| S_ij | scattering parameters (50-Ω reference unless stated); [ABCD] cascade matrix |
| ε_r, ε_eff | relative / effective permittivity (microstrip) |
| f_c | waveguide cutoff frequency |
| Q_u, Q_L, Q_e | unloaded / loaded / external quality factor |
| g_k | lowpass prototype element values (filters) |
| F, NF | noise factor (linear), noise figure (dB); T_e equivalent noise temperature |
| IP3, P_1dB | third-order intercept, 1-dB compression (dBm) |
| K, Δ, μ | Rollett stability factor, |S| determinant, mu-test |
| G_T, G_A, G_P | transducer / available / power gain |
| P_t, P_r, G_t, G_r | transmit/receive power and antenna gains (link budgets) |
| AF(θ) | array factor; d element spacing; N element count |
| σ | radar cross section, m² (dBsm in dB) |
| R | range, m; f_d = 2v/λ Doppler shift; v radial velocity |
| B, T_c, α_c = B/T_c | chirp bandwidth, duration, slope; f_b beat frequency |
| k, T₀ | Boltzmann constant, 290 K reference (noise floor = kT₀B) |
| P_d, P_fa | detection / false-alarm probability |

dB conventions, stated once here and everywhere they're used: dB = 10·log₁₀ of a power
ratio; dBm re 1 mW; dBi re isotropic; dBsm re 1 m²; **never add two dBm quantities**.
When a symbol must collide with the ledger, rename yours, not the ledger's.

## Homework code

- Student work = TODO functions in `hwN_starter.py`, NumPy-first ("the library is the
  referee, not the player" — the checker measures against scikit-rf, a physics
  invariant, or planted analytic ground truth, per HOMEWORK-PRINCIPLES.md).
- CLI pattern: `--check` prints **measured facts per module** (|Γ| at f₀, worst-band
  return loss, error vs the skrf referee, unitarity residual, detection-range error vs
  closed form) — an instrument, not a grade; modules not yet implemented print "not
  implemented" and the run continues. Plus one visual flag (`--plot`, `--smith`,
  `--sweep`, `--map`...) that produces the picture the ANSWERS.md questions are about.
  Exit code reflects crashes only, not correctness.
- The toolkit (provided plumbing) lives in the starter above the TODO line, named after
  course nouns; solutions import the starter's toolkit and harness — one harness, two
  users.
- Edge cases that will bite students are *surfaced and hinted* in HOMEWORK.md, not
  hidden.
- Vendor Touchstone files (Coilcraft / Mini-Circuits / Murata) are **downloaded by the
  student from the vendor page** (link + exact part number in HOMEWORK.md); the repo
  never bundles them (redistribution terms vary). The harness must degrade gracefully
  ("file not found — download step 0 first") when the file is absent.
- CPU-only, laptop-scale budgets: every `--check` under ~1 minute, every sweep under
  ~5. Never require a GPU.

## Environment (this machine — verify against it)

- Windows 11, Python 3.12, venv at repo root (`.venv`), packages in
  [requirements.txt](requirements.txt). Interpreter: `C:\Program Files\Python312\python.exe`
  (no `py` launcher on this machine — create venvs with the full path).
- numpy **pinned 1.26.4** (Smart App Control blocks numpy 2.5.x DLLs — incident
  inherited from the robotics course; also locks Python ≤ 3.12 — install guides must say
  "Python 3.12, exactly"). scikit-rf **pinned 1.13.0** — NOT 2.0.x: 2.0.0/2.0.1 crash on
  plain `import skrf` under numpy 1.26.4 (`np.typing.NDArray` evaluated at import time;
  verified on this machine 2026-08-04, survey §3.6 risk 0). Versions actually installed
  are recorded in [performance.md](performance.md) after `pip install`.
- Full-wave EM (openEMS) is instructor-demo only — students receive exported Touchstone/
  field files and post-process in scikit-rf; never a student install (survey §3.2).
- Always `python -m py_compile` every .py you write.
- Record every executed verification in [performance.md](performance.md) — measured
  numbers vs the syllabus success criterion.

## Hard-won process rules (inherited from optimizations/robotics)

1. **Reproduce the student's exact code path** when verifying — run the starter the way
   the homework tells the student to run it, from the lab directory.
2. Expect version skew between survey claims and installed reality; trust the venv.
   (Case in point, found on day one: the survey recommended scikit-rf 2.0.1 and its
   pyproject claims numpy>=1.21, but plain `import skrf` crashes under numpy 1.26.4 —
   the course pins 1.13.0 instead. Verify import paths and APIs against the installed
   wheel, not tutorials or release notes.)
3. Every unexplained symbol on a slide generates a student question — quantify inline.
4. When a student confusion surfaces (in review or class), it becomes permanent script
   content ("expect and welcome the X reaction...").
5. Matplotlib on this machine: interactive windows block the run — verification scripts
   should save figures (`savefig`) rather than `show()` when run with `--check`-style
   flags; `show()` is for the student-facing visual flags.
6. Numbers quoted in scripts/HOMEWORK.md ("the reference solution's detection range is
   14.2 km") must be measured on this machine and recorded in performance.md, not
   invented.
7. Never round-trip course markdown through PowerShell 5.1 `Get-Content`/`Set-Content`
   — it reads BOM-less UTF-8 as ANSI and silently mojibakes every em-dash and math
   symbol (optimizations incident, 2026-07-31). Use the Edit/Write tools for content;
   shell text-processing only on pure-ASCII files.
8. dB hygiene is a course-wide teaching point *and* a code-review point: every function
   signature says whether it takes/returns dB or linear; the lecture-1 deliberate bug
   (watts added to dBm) exists so the convention sticks.
