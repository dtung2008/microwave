# Lecture 14 — The Radar Equation & Detection

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (`pip install -r requirements.txt`: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**; nothing new this week)
**Prerequisites:** lecture 1 (the radar equation, the course radar, the 13 dB bar),
lecture 10 (noise figure — the F in kT₀BF), lecture 13 (where G comes from), and the
basic probability from the course prerequisites (densities, CDFs, independence).
**Pre-class setup:** `lab/setup_check.py` must print `SETUP OK` (it now includes a
10⁵-draw detection smoke test).

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the equation converges, and the false alarm is worked exactly (0:00–0:50)

### 1.1 The course converges (0:00–0:08)

Slide cue: the radar equation written large, every factor stamped with the lecture
that built it.

Open by writing lecture 1's equation on the board one factor at a time — but this
time, every factor gets a citation from inside the course:

> SNR = P_t G² λ² σ / ((4π)³ R⁴ · kT₀B·F · L)

P_t arrived through **transmission lines** (L2) and **matching networks** (L3, L6)
without reflecting back; G is **lecture 13's** aperture, the same dish counted twice
because monostatic; B is a **filter** you can now synthesize (L8–9); F is **lecture
10's** noise figure, set almost entirely by the LNA you designed in L11; L is the
sum of every plumbing loss in between (L5, L7); the mixer that brings the echo down
to where this decision happens is L12. Say it plainly: *in lecture 1 this equation
was a postcard from a foreign country. Today you have lived in every term.*

One number in it was never earned: **SNR_min = 13 dB**, the "detection threshold"
lecture 1 asked you to take on faith. Three claims for today, on the board:

1. **Detection is a decision under uncertainty, and both ways of being wrong have
   prices.** P_d (detection probability) and P_fa (false-alarm probability) replace
   the 13 dB hand-wave — and by the end of hour 2 you will know that 13 dB *was*
   the honest number for (P_d = 0.9, P_fa = 10⁻⁶), almost exactly.
2. **The false-alarm mathematics is exact and you can invert it by hand.** One
   Rayleigh closed form sets every threshold in this lecture — and one factor-of-2
   slip in its exponent turns 10⁻⁶ into 10⁻³. Hour 3 commits that slip on purpose.
3. **A fixed threshold dies the moment it leaves the lab.** The real world moves
   its noise floor; CFAR — estimate the noise where the target isn't — is how
   radar survives, and it pays a measurable tax and has two measurable blind spots.

### 1.2 Radar cross section, honestly (0:08–0:20)

Slide cue: the dBsm ladder, insect to airliner.

Lecture 1 used σ as a given number. Now the honest version. σ is *defined* through
the equation: the area which, intercepting the incident power density and
re-radiating it isotropically, explains the echo you actually receive. It is a
scattering property, not a silhouette: a flat plate seen face-on returns 4πA²/λ² —
at X-band a 30 cm × 30 cm plate is ~110 m², bigger than the airliner's *whole
body* number — and the same plate tilted 30° returns almost nothing toward you.

Walk the ladder, in dBsm (dB re 1 m²), the class standards plus new tenants:

- insect: **−40 dBsm** (0.0001 m²) — and X-band weather radars see *swarms* of them
- small bird: **−30 dBsm**
- large bird / small drone: **−20 dBsm** — the pair that makes drone detection hard
- human: **≈ 0 dBsm** (walking, X-band)
- fighter, nose-on, clean: **0 dBsm**
- car: **+10 dBsm**; airliner, our class number: **+16 dBsm** (40 m²)
- broadside fighter or airliner: **+25 to +30 dBsm** — aspect swings 25 dB by itself
- cargo ship: **+30 to +40 dBsm**

Two mechanisms make σ a *random variable* rather than a number. **Aspect:** a
target is a constellation of scattering centers (engine inlets, corner-like
junctions, the flat of a tail) whose returns add as phasors; a fraction of a degree
of aspect change re-phases the sum. **Frequency:** the same phasor sum re-phases
with λ, so even a fixed geometry twinkles across a wideband waveform. The measured
consequence — deep fades and bright flashes around the mean — is what the Swerling
models in hour 2 will average honestly. When lecture 1 wrote "σ ≈ 40 m²", the ≈
was hiding a 20–30 dB dance.

Stealth, in one honest paragraph (Balanis's RCS-reduction chapter [R10] is the
assigned depth): there are exactly two levers. **Shaping** does not absorb energy —
it *redirects* it, replacing corner-like retroreflectors with facets and continuous
curvature so the specular flash goes somewhere the monostatic receiver is not.
That is why stealth aircraft look faceted or blended, and why bistatic radars are
part of the counter-stealth conversation. **Absorption** (radar-absorbing
materials) turns induced currents into heat — effective, narrowband-ish, heavy,
and maintenance-hungry. Both levers buy dB of σ; the fourth root then converts
dB of σ into range at the ruinous rate of ¼: the 30 dB a serious program buys cuts
detection range by 10^(30/40) ≈ 5.6×, not 1000×. Stealth is worthwhile, not magic —
lecture 1 said it; now you know what the 30 dB costs to obtain.

Pre-empt the question: *"so which σ goes in the equation?"* Answer: a stated
convention — the class numbers are roughly median values over aspect; serious
design uses the fluctuation model (hour 2) or measured distributions. Any single
number is a summary statistic wearing a uniform.

### 1.3 Detection is a decision (0:20–0:32)

Slide cue: two probability densities and one vertical line.

Strip the problem to its skeleton. After the receive chain (L10–12), one range
cell, one instant, one number: the envelope r out of the detector. Two hypotheses:

> H₀: noise only.  H₁: target echo plus noise.

You must output a bit. The only honest procedure: pick a threshold T; declare
"target" when r > T. Then there are exactly two ways to be wrong, and they have
names, prices, and — this is the theorem-shaped part — a *knob that trades them*:

> P_fa = P(r > T | H₀) — the screen lies to the operator.
> P_d = P(r > T | H₁) — 1 − P_d of the time, the drone walks through.

Draw the two densities: noise-only piled near zero, signal-plus-noise shifted
right, overlapping. T slices both tails. Slide T right: P_fa collapses, P_d sags.
Slide it left: the screen fills. **The threshold cannot fix the overlap; only SNR
can** — more signal slides the H₁ density right and buys both numbers at once.
That is why the whole course — every dB of NF saved in L10, of loss saved in L5–7,
of gain bought in L13 — was in service of this picture.

The first-principles version, in three lines (and then honestly waved): the
optimal test statistic is the likelihood ratio p(r|H₁)/p(r|H₀) compared to a
threshold set by the costs (Neyman–Pearson: maximize P_d at fixed P_fa). For our
densities the likelihood ratio is monotone in r — so "compare the envelope to a
threshold" is not a heuristic, it *is* the optimal detector, which is why the rest
of the lecture is about choosing T, not about better statistics. The full
machinery, including when envelope-thresholding is *not* optimal, is Richards
chs. 6–7 [R14]; we take the three lines and the conclusion.

Now the densities, concretely. The receiver hands you I and Q — two independent
Gaussian noise channels, each with variance σ², total noise power N = 2σ² (this
factor of 2 is today's landmine; plant a flag on it). The envelope r = √(I²+Q²):

- Under H₀: **Rayleigh**. p(r) = (r/σ²)·exp(−r²/2σ²).
- Under H₁ (steady echo of amplitude A): **Rician** — Rayleigh's shifted cousin,
  a bell around A for strong signal.

Common student question, pre-empt it: *"why not detect on I directly?"* Because
the echo's phase is unknown — the target's range sets it modulo λ/2, and λ/2 is
1.5 cm. The envelope discards the unknowable phase and keeps the energy; that is
the whole reason Rayleigh (not Gaussian) runs today's mathematics.

### 1.4 The false alarm, worked exactly (0:32–0:45)

Board work — the centerpiece of hour 1. Integrate the Rayleigh tail. It closes:

> P_fa = ∫_T^∞ (r/σ²) e^(−r²/2σ²) dr = **exp(−T²/2σ²)**

No approximation. Invert it by hand on the board:

> T = σ·√(2·ln(1/P_fa)) = √(N·ln(1/P_fa))   (N = 2σ², the noise power)

The homework's normalized numbers (N = 1): P_fa = 10⁻⁶ → ln(1/P_fa) = 13.816 →
**T = 3.7169** — the threshold sits **11.40 dB above the mean noise power**, at
3.72× the rms envelope. Say the second form out loud: the budget of lecture 1
computes N = kT₀BF in watts; the threshold is one square root away from it.

Why 10⁻⁶ and not something comfortable like 10⁻³? Count decisions. B = 1 MHz means
roughly 10⁶ independent looks per second. At P_fa = 10⁻⁶ that is *one false blip
per second* — already enough that real systems stack confirmation logic (m-of-n
across scans) on top. At 10⁻³ it is a thousand per second: the screen goes white.
P_fa is set by the decision *rate*, and the decision rate is set by B — the same B
that lecture 1 called a noise tax now taxes you twice.

The knife edge, quantified (this is why threshold errors are lethal): P_fa depends
on T through an *exponential of a square*. Move the threshold **half a dB** and
the exponent scales by 10^(±0.05): P_fa = 10⁻⁶ becomes 1.9×10⁻⁷ (up half a dB) or
4.5×10⁻⁶ (down half a dB) — a factor of ~5 each way, from 0.5 dB. Nothing else in
this course responds to half a decibel like that. This sensitivity is exactly why
hour 3 measures every threshold with a million Monte Carlo draws instead of
trusting anyone's algebra, including ours — and why the factor-of-2 exponent slip
(using the total noise power N where the per-channel σ² belongs) is not a 3 dB
nuisance like it would be in a budget, but a *P_fa → √P_fa* catastrophe:
10⁻⁶ → 10⁻³, silently. Hour 3 reproduces it; the war story in hour 2 shows what
it looks like on a display.

### 1.5 Hour recap (0:45–0:50)

Three sentences, then break: the radar equation is now fully yours — every factor
has a home lecture, and the last unearned number (13 dB) falls this hour next
door; σ is a scattering property that fluctuates 20–30 dB and stealth buys its dB
with shaping and absorption, paid back at one-quarter rate by the fourth root;
the false alarm is exact — P_fa = exp(−T²/2σ²), T = √(N·ln(1/P_fa)), 3.72 on unit
noise, and half a dB of threshold moves P_fa by 5×. Hour 2 puts the target into
the noise and gets P_d — then teaches the threshold to set itself.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: P_d, Albersheim, integration, and CFAR (1:00–1:50)

### 2.1 P_d, and the 13 dB bar audited at last (1:00–1:15)

Slide cue: the P_d vs SNR curve at P_fa = 10⁻⁶.

Under H₁ the envelope is Rician, and its tail integral does not close in
elementary functions — it is **Marcum's Q function**, and P_d = Q₁(√(2·SNR),
√(2·ln(1/P_fa))). Scipy evaluates it exactly (noncentral χ²; the homework toolkit
wraps it as `marcum_pd` — the referee). But engineers on whiteboards for seventy
years have used **Albersheim's approximation**, and so will you:

> A = ln(0.62/P_fa),  B = ln(P_d/(1−P_d))
> **SNR_dB = −5·log₁₀N + (6.2 + 4.54/√(N+0.44)) · log₁₀(A + 0.12AB + 1.7B)**

State its contract like a datasheet, because it has one: **~0.2 dB accuracy for
10⁻⁷ ≤ P_fa ≤ 10⁻³, 0.1 ≤ P_d ≤ 0.9, 1 ≤ N ≤ 8096** (N = non-coherently
integrated pulses; linear detector; *nonfluctuating* target). An approximation
with a stated envelope is an instrument; one without is a rumor. Hour 3 measures
the envelope — including a corner where it frays (at P_d = 0.1, P_fa = 10⁻⁷ the
error is measured at 0.75 dB; envelopes have corners).

Now the audit the course has owed you since week one. Feed in the honest customer
spec — P_d = 0.9, P_fa = 10⁻⁶, N = 1:

> Albersheim: **13.11 dB**. Exact (Marcum): **13.18 dB**.

Pause on it. Lecture 1's "13 dB" was not a hand-wave after all — it was the
compressed form of *this* specification, and now you can decompress it. The honest
detection ranges move by ×10^(−0.11/40) = **×0.9934**: airliner 32.65 → 32.44 km,
fighter 12.98 → 12.90, drone 4.11 → **4.08 km**. And at exactly 13 dB the
delivered P_d is **0.8744**. So what did the hand-wave actually hide? Not range —
*meaning*. "Detectable to 4.11 km" always meant "an 87–90% coin per look, at one
false blip per million cells." Detection ranges are not walls; they are the
R where a steep probability curve crosses a contract number.

How steep? From the P_d curve and R⁴: near 4 km the drone loses ~3.9 dB of SNR
per km (40·log₁₀(5/4)); P_d = 0.9 → 0.5 takes only 13.18 − 11.24 ≈ 1.9 dB. Half a
kilometer of sky is the whole cliff. That steepness is *good* engineering news —
it means R_max is a meaningful number — and it is homework Q1's reconciliation.

### 2.2 Swerling, one honest slide (1:15–1:22)

Slide cue: nonfluctuating vs Swerling-1 P_d curves.

Everything above assumed the echo amplitude A is steady. Section 1.2 already told
you it is not — σ dances with aspect. Swerling's models are the standard
vocabulary for that dance: case 0/5 (nonfluctuating — today's mathematics),
cases 1–2 (many comparable scatterers — σ exponential, i.e. the whole *power*
Rayleigh-fades; slow/fast versions), cases 3–4 (one dominant scatterer plus
a chorus). One formula worth the board, because it is closed-form and shocking —
Swerling 1, single pulse:

> P_d = P_fa^(1/(1+SNR))   (SNR linear)

Invert at (0.9, 10⁻⁶): SNR = ln(P_fa)/ln(P_d) − 1 = 130.1 → **21.1 dB**. The
fluctuating target needs **8 dB more** than the steady one for the same P_d = 0.9
— because fluctuation means the target sometimes *fades*, and demanding 90%
success forces you to fund the fades. (At P_d = 0.5 the gap nearly vanishes;
fluctuation punishes ambition.) In range: ×10^(−8/40) ≈ 0.63 — the honest drone
range drops from 4.08 toward **2.6 km** if the drone Rayleigh-fades. One slide is
all we spend, but carry the moral: *when someone quotes a detection range, ask
"at what P_d, what P_fa, and which Swerling."* Those three questions are this
lecture in operational form.

### 2.3 Integration — why 10 pulses ≠ 10× range (1:22–1:30)

The radar does not get one look; a scanning beam paints the target with a burst
of pulses. Add them. Two ways:

**Coherent** (before the envelope detector, phases aligned — L15's Doppler
processing does exactly this): N pulses add as voltage, noise as power → SNR
gains exactly **10·log₁₀N**. Ten pulses = +10 dB.

**Non-coherent** (after the detector, phases discarded): envelopes of noise no
longer average toward zero — part of the gain is spent re-detecting. The exact
requirement (hour 3 computes it from the Gamma/noncentral-χ² closed forms):
single pulse needs 13.18 dB; ten coherent pulses need 3.18 dB per pulse; ten
non-coherent need **5.27 dB** per pulse. The non-coherent tax: **2.1 dB** at
N = 10 (Albersheim's N-term prices it at every N; the tax grows like √N-ish for
large N).

Now the punchline the syllabus promised: ten pulses is nowhere near ten times
range. Range rides the fourth root: +10 dB coherent → ×10^(10/40) = **1.78×**
range; non-coherent → **1.58×**. To *double* the drone's detection range you need
+12 dB after all taxes — 16 coherent pulses, or ~25 non-coherent. Integration is
how real radars afford detection (megawatt peak power is the other, worse way),
but R⁴ makes every route expensive. This is also the seed of lecture 15: FMCW
radars integrate coherently *by construction* — the FFT is the integrator.

### 2.4 CFAR — the threshold that sets itself (1:30–1:44)

War story first, sixty seconds, because everything in this section exists because
of installations like it. A coastal surveillance radar is commissioned; the
threshold was set in the lab, against thermal noise, P_fa = 10⁻⁶, beautifully
verified. On the coast, sea clutter raises the effective noise floor 20 dB. Put
it through hour 1's closed form — the exponent divides by 100:

> P_fa = (10⁻⁶)^(1/100) = 10^(−0.06) = **0.87**

Not 10⁻⁴. *Eighty-seven percent.* At a million decisions per second, ~870,000
false alarms per second: the screen is white, the operator turns the gain down
(raising the threshold blindly), and the radar detects nothing at all. Nobody
mis-soldered anything. The threshold was simply a *constant* in a world that
isn't. Let the class sit with how violent the exponential is: a 20 dB floor shift
moved P_fa by *five orders of magnitude and then saturation*.

The fix is a sentence: **estimate the noise where the target isn't.** For each
cell under test (CUT), average the power in n_train cells on each side — skipping
n_guard guard cells so the target's own energy does not pollute its jury — and
set the threshold as a multiple of that local estimate. That is cell-averaging
CFAR: constant false-alarm rate, because the threshold now *rides* the floor.

The mathematics is one clean derivation (square-law domain: power z = r² is
exponential under noise — note the domain change, the second place today's
factor-of-2 bug can hide). The sum of N training powers is Gamma; integrating the
CUT's exponential tail against the estimate gives, exactly:

> P_fa = (1 + α/N)^(−N)  →  **α = N·(P_fa^(−1/N) − 1)**

where the threshold is α × (training mean). Check the limit: as N → ∞,
α → ln(1/P_fa) — the known-noise multiplier from hour 1 (in power form),
recovered. For our baseline N = 16, P_fa = 10⁻⁶: **α = 21.94 (13.41 dB)** vs the
ideal 13.82 (11.40 dB). The gap is the **CFAR loss**: 10·log₁₀(α_N/ln(1/P_fa)) =
**2.01 dB** at N = 16, **0.97 dB** at N = 32. The price of *estimating* the floor
from 16 cells instead of knowing it: two dB, forever, everywhere — about 11% of
detection range. More training cells cheapen it. So why not N = 200?

Because the training window is a bet that the world is *homogeneous* across it,
and the world has edges. Two failure modes, both in the homework's scenes:

**Clutter edges.** Where the sea meets the land — or a 30 dB clutter region
begins — a CUT just inside the clutter has half its jury still voting "cheap
clear-side noise": the threshold underestimates, and false alarms spray from the
edge (measured in the homework's ensemble: ~13× the design P_fa in the edge zone,
and *worse* with a longer window, which straddles more). Just past the far edge,
the mirror image: a clear-side CUT with clutter in its jury is over-thresholded —
a blind strip. The homework plants a 15 dB target there and the detector walks
past it.

**Masking.** Two drones six cells apart: the strong one sits in the weak one's
training window, inflates its noise estimate ~10 dB, and the weak drone —
comfortably detectable alone — vanishes. The jury convicted the noise floor of
being a target's neighbor. Fixes exist (smallest-of, censored, order-statistic
CFAR) and each buys its robustness with extra loss or new edge behavior;
homework Q4 asks you to pick one and name its price.

### 2.5 Clutter in one slide, and hour recap (1:44–1:50)

The clutter slide, with the course radar's own numbers: at the drone's 4.08 km,
a 3.6° beam (that is what 33 dBi buys — G ≈ 26000/θ², lecture 13) paints a
footprint ~257 m wide, and B = 1 MHz cuts range into 150 m cells. The ground
patch competing with the drone in its own cell: ~257 × 150 m ≈ 3.9×10⁴ m² —
**+46 dBsm of illuminated dirt**. Even a modest reflectivity σ⁰ = −10 dB leaves
+36 dBsm of clutter against a −20 dBsm drone: **the ground is ~56 dB bigger than
the drone — call it 60**. No threshold mathematics survives that ratio in the
power domain. The honest answer is a different axis entirely: the ground does not
*move*. Doppler — lecture 15 — is where the drone finally outruns the dirt (and
lecture 12's phase-noise skirt already told you what limits *that*).

Recap in three sentences: P_d comes from Rician statistics — Albersheim
approximates it inside a stated 0.2 dB envelope, and the honest (0.9, 10⁻⁶) spec
costs 13.18 dB, which is what lecture 1's 13 dB secretly was; fluctuation and
integration reprice it — Swerling 1 demands 8 dB more, ten coherent pulses refund
exactly 10, and the fourth root converts all of it to range at 25 cents on the
dollar; and thresholds must be *estimated locally* — CA-CFAR at α = N(P_fa^(−1/N)−1)
costs 2 dB and fails, measurably, at edges and next to neighbors. Hour 3 makes
every one of those sentences print.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: Monte Carlo detection and CA-CFAR in NumPy (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number. Everything is
seeded — the class sees exactly the numbers below.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib 3.10.x.
Nothing new this week — the exact referees (noncentral χ², Gamma) ship in the
scipy already installed.

### 3.2 The noise after the envelope detector (2:03–2:10)

Cell 3.2: a million complex-noise draws, unit total power, envelope taken.
Measured mean envelope power 0.9998 (built to be 1); mean envelope 0.8859 vs the
Rayleigh √π/2 = 0.8862. The histogram lands on the pdf 2r·e^(−r²) like a glove —
`hw14_rayleigh.png`, with the P_fa = 10⁻⁶ threshold drawn where the tail is
already invisible. Point at the gap between the bulk and the threshold: *the
entire detection business lives in that last invisible sliver.*

### 3.3 The exact inverse — then the measurement that does not trust it (2:10–2:18)

Cell 3.3: T = √(ln(1/P_fa)) typed from the board. At 10⁻³: T = 2.628, measured
**1.05×10⁻³** (1051 crossings of 10⁶ — inside the ±9.5×10⁻⁵ 3σ band). At 10⁻⁶:
T = 3.717, measured **2×10⁻⁶** — two crossings, where the expected count is *one*.
Stop and teach the meta-lesson: a million trials cannot measure a one-in-a-million
probability; the 10⁻³ row verified the formula's *shape*, and the closed form
carries the trust down to 10⁻⁶. Then the chunked 10⁷-trial run: 8 crossings,
8.0×10⁻⁷ — the "≥ 10/P_fa trials" rule of thumb, demonstrated. (Homework Q3 is
exactly this discussion, written down.)

### 3.4 P_d vs SNR — Monte Carlo, Albersheim, exact (2:18–2:26)

Cell 3.4: plant a steady target, sweep SNR 6–16 dB, 10⁵ trials per point, against
the exact Marcum curve and Albersheim's approximation: measured 0.2484 vs exact
0.2480 at 10 dB; 0.6824 vs 0.6794 at 12; 0.9723 vs 0.9721 at 14. Then the audit
line the lecture promised: **(P_d = 0.9, P_fa = 10⁻⁶) → Albersheim 13.11 dB,
exact 13.18 dB.** `hw14_pd_sweep.png` is the curve; the class should notice the
Monte Carlo dots sitting *on* the exact curve while Albersheim's dashed line
hovers a tenth of a dB off — an approximation performing exactly to its
datasheet, and (in the checker) fraying at its stated corner.

### 3.5 Integration, measured (2:26–2:32)

Cell 3.5: ten-pulse non-coherent integration. The noise-only sum is Gamma(10) —
threshold **32.71** exact by construction, no Monte Carlo needed (planted truth).
At Albersheim's recommended 4.99 dB/pulse the measured P_d is **0.851**, not 0.9 —
because the exact requirement is **5.27 dB**: a 0.28 dB Albersheim slip near its
envelope's edge, *watched happening*. The scoreboard prints: single pulse
13.18 dB; ten coherent 3.18; ten non-coherent 5.27 (tax: 2.1 dB). Range: **×1.78
coherent, ×1.58 non-coherent — NOT ×10.** R⁴ again, and forever.

### 3.6 CA-CFAR — live, on three scenes (2:32–2:40)

Cell 3.6: the cfar function is ~12 lines (prefix sums, clipped windows,
α = N(P_fa^(−1/N)−1) — the closed form from the board; α(16, 10⁻⁶) = 21.94,
13.41 dB, CFAR loss 2.01 dB printed first). Run the three homework scenes, same
seeds the students will get:

- **clean**: hits at cells 400 (20 dB) and 1400 (15 dB), zero false alarms — the
  threshold hugs 13.4 dB above the floor, and the promise holds.
- **clutter_edge**: the 20 dB target *inside* 30 dB clutter is caught (the
  threshold climbed the wall with the clutter — that is the whole point of CFAR),
  but the 15 dB target five cells *before* the edge is gone — the edge's blind
  side, on screen.
- **two_drones**: the 22 dB drone is caught; the 15 dB drone six cells away is
  gone — and the plotted threshold hump over the pair shows exactly whose power
  raised whose bar. Then the control arm, same seed, strong drone deleted:
  detected = True. Masking, demonstrated with a controlled experiment.

`hw14_cfar_scenes.png` stays on screen into the homework brief.

### 3.7 Deliberate bug — power statistics where amplitude statistics apply (2:40–2:44)

Cell 3.7, the slip hour 1 flagged: the noise power is 1 W *total*, but I and Q
each carry only ½ — the Rayleigh exponent wants the per-channel σ². Type the
plausible wrong line: put the total power in the σ² slot. The threshold comes out
2.628 instead of 3.717 — both look like fine thresholds, nothing crashes — and
the same million noise draws that measured 2×10⁻⁶ now measure **1.1×10⁻³**.
P_fa^(1/2): a factor of 2 *in an exponent* is not a 3 dB error, it is three
orders of magnitude. Print the operational translation: ~1,051 false alarms per
second at B = 1 MHz instead of ~1 — the screen goes white, in the lab, politely,
with a seed. The fix is the habit the whole course has been building: the formula
looked right; **the Monte Carlo caught it**. Never ship a threshold you have not
measured.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. The story: the course radar must detect the drone at
(P_d = 0.9, P_fa = 10⁻⁶) — the honest contract, end to end:

- Module 1: the exact Rayleigh inverse and the Monte Carlo that distrusts it
  (10⁶ trials, binomial error bars — the 3.3 discussion, yours).
- Module 2: Albersheim + Monte Carlo P_d against the Marcum referee, then
  lecture 1's three detection ranges redrawn with the honest spec — and the
  P_d-vs-range cliff that replaces the "range wall" picture.
- Module 3 — **the core**: `ca_cfar(power_profile, n_train, n_guard, pfa)` →
  (detections, threshold), the exact interface lecture 15 will import. Three
  scenes with planted truth; one edge; one masking; a checker ensemble that
  measures the edge false-alarm rate either side of doubling the window.
- **Predictions first:** Q1 (does honesty move the drone's 4.11 km, and by 1%,
  10%, or 50%?) and Q2 (doubling the training window moves CFAR loss and edge
  false alarms — which directions?) are answered *before* running.
- `--check` prints facts, not PASS/FAIL; everything is seeded; ≤ 3 hours; AI
  welcome — the predictions and reconciliations must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: detection is two error rates and a knob, and the
13 dB of week one decompressed into (P_d = 0.9, P_fa = 10⁻⁶) = 13.18 dB exactly;
the Rayleigh closed form set every threshold today, and one factor of 2 in its
exponent — committed live — turned 10⁻⁶ into 10⁻³ until a million draws caught
it; and CFAR keeps the promise a fixed threshold cannot, for 2 dB, except at
edges and next to neighbors, where you watched it fail on purpose. Teaser: the
drone is still 56 dB under the dirt in the power domain — next lecture the radar
stops asking "how strong" and starts asking "how fast": FMCW, Doppler, and the
map where the hovering drone's blades give it away.

---

## References

- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems* (RES.LL-001),
  lectures 2 (radar equation/detection) and 6 (detection & CFAR) — free:
  https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
- [R14] Richards, *Fundamentals of Radar Signal Processing*, 2e, chs. 6–7 — the
  detection and CFAR mathematics this lecture compresses (reference).
- [R13] Richards, Scheer, Holm (eds.), *Principles of Modern Radar*, Vol. I —
  detection chapters (reference).
- [R10] Balanis, *Advanced Engineering Electromagnetics*, 3e — the RCS-reduction
  chapter behind the stealth slide (reference).
- [R12] Skolnik, *Introduction to Radar Systems*, 3e, ch. 2 — the classic
  treatment of the radar equation with P_d/P_fa (reference).
