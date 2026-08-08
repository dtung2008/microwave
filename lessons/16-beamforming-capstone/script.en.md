# Lecture 16 — Beamforming, DOA & Collision Avoidance (Capstone)

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course env: numpy 1.26.4, scipy, matplotlib,
scikit-rf 1.13.0; **Python 3.12, exactly**; this lecture adds `pip install pyargus`)
**Prerequisites:** lecture 13 (the array factor and its conventions), lecture 14
(P_fa/P_d and CFAR), lecture 15 (the FMCW pipeline and the (R, v) sign convention),
and — for the closing hour — every other lecture in the course.
**Pre-class setup:** `pip install pyargus` in the course venv, then run
`lab/setup_check.py` — it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class. This is the
final lecture: hour 3 ends with the course wrap-up, not just the lecture's.

---

## Hour 1 — Principles I: the snapshot model, beamscan, and MVDR (0:00–0:50)

### 1.1 What closes today (0:00–0:08)

Slide cue: the loop-closing slide — four arrows converging on one pipeline.

Open with the inventory, because this lecture owns almost nothing new — it *closes*
things. Lecture 13 gave us the array factor and never said what to do with the
element signals besides summing them; today we keep them separate and read angles
out of them. Lecture 7 built a monopulse comparator out of hybrids and promised
"software, lecture 16"; today we take the ratio. Lecture 14 taught the price of a
false alarm in probability; today the false alarm gets a cockpit. Lecture 15's
pipeline ends with a target list of (R, v) — range and range rate, no direction;
today we append θ and then, for the first time in sixteen weeks, the radar *does*
something: it decides whether to move.

Three claims for today — the last board-full of the course:

1. **Beamforming is matched filtering in space.** The steering vector is the
   template; everything from lecture 13 is this statement read backwards.
2. **Adaptivity is one Lagrange multiplier** — MVDR is a three-line derivation,
   and what it buys (a 40 dB jammer removed without being told where it is) looks
   like magic until you watch the covariance do it.
3. **The decision is geometry, not bravado.** Closest point of approach and
   time-to-go have closed forms; the hard part — the part lecture 14 trained you
   for — is choosing what alert rate you can live with.

Say it to the wireless-comms students directly, because this is their homecoming:
the snapshot model we are about to write, x = A s + n, is *the* MIMO equation —
the same A-matrix your channel-estimation courses diagonalize, the same
eigen-machinery. You spent this course learning what the analog world does to that
equation before software ever sees it; today you get to use both halves at once.

### 1.2 The snapshot model, built carefully (0:08–0:20)

Board work — this model carries the whole lecture, so build it slowly and honestly.

A plane wave from direction θ (measured from broadside, the course convention from
lecture 13) crosses a ULA (uniform linear array), element n at x = n·d. The wave
reaches element n earlier or later than element 0 by a path difference
n·d·sin θ — a *time* delay τ_n = n·d·sin θ / c.

Now the assumption that makes array processing linear algebra instead of
convolution: **narrowband**. If the signal's envelope changes negligibly in the
time the wavefront needs to cross the aperture (29 mm here — about 0.1 ns), a
delay is just a phase: element n sees the same complex sample, rotated by
e^(+j·k·d·n·sin θ), k = 2π/λ. Stack the sixteen phases into a column and it has a
name — the **steering vector** a(θ). It is lecture 13's array-factor phase, written
as a vector instead of summed.

One snapshot = the sixteen complex numbers the array delivers at one instant (in
our FMCW world: one range-Doppler cell of one chirp, taken across the array —
lecture 15 gave us the cell, today we keep its wavefront). M sources at angles
θ₁…θ_M with complex amplitudes s₁…s_M, plus receiver noise:

> x = A s + n, A = [a(θ₁) … a(θ_M)] — N×M, the array manifold.

Collect K snapshots and form the **sample covariance** R̂ = XXᴴ/K. Everything in
this lecture is a different way of interrogating R̂. Its true value is
R = A P Aᴴ + σ²I — signal structure sitting on a noise floor — and every method
today is a bet on how well K snapshots estimated it. Hold that thought; hour 3
breaks it deliberately.

Pre-empt the question: *"why is the drone's s a random number? It's one aircraft."*
Because lecture 14 taught you echoes fluctuate — aspect angle, blade flash,
multipath. We model s as complex Gaussian per snapshot (Swerling-style), and the
homework toolkit does exactly that. The steering vector is the part that holds
still; the amplitude never was.

### 1.3 Delay-and-sum — derived twice (0:20–0:32)

**Level 1 — steer and sum (the fast version).** To listen toward θ₀, undo each
element's phase and add: y = w ᴴx with w = a(θ₀)/N. Signals from θ₀ add in phase
(sixteen phasors, one direction — lecture 13's picture); everything else adds with
scrambled phases and mostly cancels. That *is* the phased array, receiving.

**Level 2 — matched filter in space (the first-principles version).** Ask instead:
what w maximizes SNR for a signal arriving along a(θ₀) in white noise? Output
signal power |wᴴa|²p, output noise σ²‖w‖². The Cauchy–Schwarz argument you know
from matched filters in time (lecture 15's pulse compression) gives w ∝ a(θ₀) —
the matched filter *is* the steering vector. SNR gain: exactly N — 12 dB for
sixteen elements, the same N that lecture 13 called directivity. One idea, third
appearance, and say so: **correlate with the template of what you seek** — in
time (matched filter), in delay (pulse compression), now in space (beamforming).

The number to anchor: our 16-element, λ/2 array at 77 GHz has HPBW = **6.35°**
(hw13's closed form, reused verbatim in the toolkit). Everything in the homework
is priced in this beamwidth.

### 1.4 Beamscan DOA — and what "resolution = beamwidth" actually means (0:32–0:40)

DOA (direction of arrival) estimation, method zero: point the delay-and-sum beam
everywhere and plot the output power —

> P_bs(θ) = a(θ)ᴴ R̂ a(θ) / N².

This is the **beamscan** (or Bartlett) spectrum. It is lecture 13's pattern used
backwards, so it inherits lecture 13's limits: peaks are beamwidth-wide, sidelobes
are −13.2 dB, and two sources closer than about one beamwidth merge into one lump.
That is the honest content of "resolution = the beamwidth."

Now pre-empt the over-application, because the homework's predict-first question
is aimed straight at it: *does the rule mean two drones 1.5 beamwidths apart
cannot be separated?* No — 1.5 BW is *above* the limit; the measured beamscan
spectrum shows two peaks with a **+5.7 dB dip** between them at 18 dB SNR, and
keeps showing them down to −15 dB. The rule says separations *below* ~1 BW are
lost. Commit to your prediction before you run; the reconciliation is the
assignment.

And one bias worth naming now (students will find it in `--check`): with two
sources present, each peak sits on the other's mainlobe skirt, which *pulls the
peaks together* — the measured beamscan peaks sit at ±4.9° for sources planted at
±4.76°. Peak positions from overlapping lobes are biased even when resolved.
MVDR's sharper peaks shrink the pull to almost nothing.

### 1.5 MVDR — adaptivity in one Lagrange multiplier (0:40–0:50)

The beamscan beam is fixed; it treats a jammer like any other off-axis signal —
attenuated by whatever sidelobe happens to lie there. Capon's 1969 question:
choose w freshly *for each look direction*, to minimize total output power while
holding the look direction's gain at exactly one:

> minimize wᴴR̂w subject to wᴴa(θ) = 1.

One Lagrange multiplier, kept clean on the board (this is the derivation the
syllabus promises, so do every line):

> L = wᴴR̂w + λ(1 − wᴴa) ∂L/∂wᴴ = R̂w − λa = 0 ⟹ w = λR̂⁻¹a
> constraint ⟹ λ = 1/(aᴴR̂⁻¹a) ⟹ **w_mvdr = R̂⁻¹a / (aᴴR̂⁻¹a)**

Output power = the MVDR spectrum, P_mvdr(θ) ∝ 1/(aᴴR̂⁻¹a). Read the mechanism out
loud: minimizing output power *subject to unity gain at θ* means the optimizer
spends its degrees of freedom nulling whatever correlated energy is loudest —
without ever being told where it is. The jammer's location is encoded in R̂; the
inverse digs it out.

What it buys, in numbers the class will re-measure in hour 3: a jammer at +25°,
40 dB above a drone at −10°. Beamscan's spectrum at the drone's angle reads
+24.9 dB — the *jammer's sidelobe floor*, 15 dB above the drone's own echo; its
two tallest peaks are the jammer and the jammer's first sidelobe. The drone has
vanished. MVDR at the same angle: +20.9 dB, the drone at full array gain, because
the adapted weights put a deep null on +25° for every look direction except the
jammer's own. Below the beamwidth, MVDR also resolves what beamscan cannot — at a
price: **superresolution is bought with SNR and snapshots**, and the homework
measures the exact SNR where it flips.

The caveat, stated now, demonstrated in hour 3: everything above used R̂, the
*sample* covariance. MVDR trusts it completely. With K comfortably above N
(K ≥ 2N is folklore, K = 4N is comfort) that trust is earned; with K < N, R̂ is
rank-deficient, and the minimizer discovers it can "cancel" the strongest thing
in the data — the target itself. Hour 3's deliberate bug shows the target's MVDR
reading collapse from +27 dB to **−114 dB** with K = 8, and diagonal loading
(R̂ + εI) buy it back. Adaptivity is a loan against the covariance estimate.

War story, 60 seconds: an adaptive sidelobe canceller on a coastal surveillance
set, proudly nulling a shore-based interferer — until a software update shortened
the covariance window "to react faster." The array began softly nulling its own
low-elevation returns whenever a strong echo sat in the training data; detection
range against small boats quietly degraded 6 dB and *nobody saw a failure*,
because an adaptive null is silent. It was found months later by a routine
calibration sphere reading low. Moral for the homework: adaptive systems fail by
*subtraction* — you must referee them against planted truth, which is exactly
what your checker does.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: monopulse, MIMO, tracks, and the decision (1:00–1:50)

### 2.1 Monopulse — lecture 7's comparator, now in software (1:00–1:12)

Beamscan gives angle to ~a beamwidth; the corridor guard needs better without
scanning. Lecture 7 built the hardware answer out of four hybrids: a **sum beam**
Σ and a **difference beam** Δ, formed simultaneously from the same aperture —
hence *mono*-pulse, one pulse suffices.

In software the comparator is two weight vectors: Σ = uniform (the matched
filter), Δ = the same weights with the sign flipped on half the aperture. On
boresight Δ nulls exactly (the two halves cancel — lecture 7's 180° hybrid did
this in copper). Off boresight by δθ, Δ grows linearly while Σ barely moves, so
the ratio is a **discriminant**: with our split it lands in the imaginary part,
Im(Δ/Σ) ≈ k_m·δθ, with slope k_m measured once from the steering vectors
(0.2195 per degree for our array — hour 3 calibrates it live).

One division refines the angle to a small fraction of the beamwidth: measured in
hour 3, a target at +0.90° comes back as +0.914° — 0.014° error against a 6.35°
beamwidth, from one CPI. Also measured: at −2.3° the error grows to 0.21°,
because the discriminant is linear only near the null. Monopulse refines *within*
a beam; it does not replace finding the beam. That division of labor — beamscan
coarse, monopulse fine — is exactly how fire-control radars have worked since the
1950s (and why lecture 7 called the comparator the most consequential 3 dB in
radar).

### 2.2 MIMO radar — the virtual array, one slide (1:12–1:20)

The automotive question: a 77 GHz sensor wants a 1° beam — that needs ~100λ of
aperture, ~120 elements at λ/2. Nobody ships 120 receive chains in a bumper.

MIMO (multiple-input multiple-output) radar's answer, one slide because the idea
is one line: with N_t transmitters sending *orthogonal* waveforms (time-staggered
chirps in practice — TDM), each of the N_r receivers can separate all N_t echoes.
Each (transmit m, receive n) pair measures the channel with total phase
k·(x_tx,m + x_rx,n)·sin θ — the sum of positions. The set {x_tx,m + x_rx,n} acts
as a **virtual array** of N_t·N_r elements. Choose spacings cleverly (TX elements
spaced N_r·λ/2 apart) and the virtual array is a filled ULA of N_t·N_r·(λ/2):
**N + M channels buy N·M elements.** A 3-TX, 4-RX chip — the standard automotive
part — behaves as a 12-element array; three such chips cascade into the 1° imaging
radars now on production trucks [R25][R26].

For the wireless students: yes, this is the same trick as MIMO channel rank — the
radar just gets to *choose* its geometry, so it engineers the ranks to multiply.
Everything else in today's lecture (steering vectors, MVDR, monopulse) applies to
the virtual array verbatim; that is why we teach the 16-element ULA without
apology.

### 2.3 The tracking minimum — the α-β filter (1:20–1:30)

The chain now emits, four times a second, (R, v, θ) per target. Detections are
noisy; decisions need velocity *vectors*, which no single frame provides. The
honest minimum tracker — below Kalman, above nothing — is the **α-β filter**, per
axis:

> predict: x̂⁻ = x̂ + v̂·Δt
> residual: r = z − x̂⁻ (z = the new measurement)
> correct: x̂ ← x̂⁻ + α·r v̂ ← v̂ + (β/Δt)·r

Two gains, one trade: large α/β chase measurements (fast response, noisy
velocity), small α/β trust the model (smooth velocity, lag under maneuver). The
course fixes α = 0.5, β = 0.2 — the homework asks you to *reason* about them, not
tune them. Say the lineage honestly: the α-β filter is the steady-state Kalman
filter for constant-velocity motion; when a maneuvering target or varying
measurement quality matters, you graduate to the full Kalman (MIT LL's tracking
lecture [R31] from here). And name the elephant we stepped around: **data
association** — which detection belongs to which track — is given by the toolkit;
real trackers spend half their code earning it. One homework, sixteen weeks; we
spend the budget on the decision.

Pre-empt the misconception: *"why filter at all — I measure position every
0.25 s, just difference two frames for velocity."* Do the arithmetic on the
board: differencing amplifies noise by √2/Δt — 0.1 m of position noise becomes
0.57 m/s of velocity noise per pair, on targets moving 9 m/s, and the CPA
extrapolates that error over seconds. The α-β filter is nothing but a principled
way of differencing over *many* frames; by the last frame its velocity error is
what makes the homework's CPA land within a meter instead of ten.

### 2.4 CPA and time-to-go — the geometry of "will it hit us" (1:30–1:40)

Board derivation, four lines, promised to the homework. Track state: position p,
velocity v (2-D, sensor at origin, both from the α-β filter). Future separation
|p + v·t|². Minimize: d/dt |p + vt|² = 2(p + vt)·v = 0 ⟹

> **t_CPA = −(p·v)/|v|²  d_CPA = |p + v·t_CPA|**

Read the signs like an engineer: p·v < 0 means closing (some velocity points back
along the sight line) — t_CPA positive, the close approach is ahead. p·v > 0:
opening; the CPA is behind you; whatever the range is doing, geometry says
relax. |v| = 0: hovering — the CPA is *now*, at range |p|.

Contrast with the naive **TTC** (time to collision) every driver's intuition
computes: R/(−Ṙ), range over closing rate. For a head-on target they agree. For a
*crossing* target the radial rate collapses to zero as it approaches CPA — the
homework's drone_b crosses at a safe 60 m, its −Ṙ → 0, and R/Ṙ → ∞ "no danger" —
which happens to be the right verdict for exactly the wrong reason, with no way
to tell a 60 m pass from a 24 m pass. Only the angle measurement upgrades Ṙ to a
velocity *vector*, and only the vector separates "coming close" from "coming
slowly." This is what the array was for.

### 2.5 The alert, and what it costs — TCAS and AEB (1:40–1:48)

The rule the homework defends: **alert iff 0 < t_CPA ≤ 20 s and d_CPA < 30 m.**
Two thresholds, two failure directions, and lecture 14 already taught the
mathematics of both. A missed alert is lecture 14's missed detection with the
cost function made vivid. A false alert is P_fa **with a cockpit attached**: the
system's advice causes a maneuver, and unnecessary maneuvers are not free — they
are themselves dangerous, and they burn trust at compound interest. An alerting
system whose operators have learned to ignore it is strictly worse than no
system.

The two industrial instances, one minute each:

- **TCAS** (traffic collision avoidance system, aviation): interrogates
  transponders, tracks in exactly our (R, Ṙ, θ)-plus-altitude terms, and issues
  RAs (resolution advisories — climb/descend commands) on a time-to-go logic
  ("tau") descended from R/Ṙ with protections for the crossing case. Its
  false-alert economics are written in certification law; the 2002 Überlingen
  collision — one crew followed the controller, one followed TCAS — is the case
  study in what an advisory system's *credibility* is worth.
- **AEB** (automatic emergency braking, automotive): our 77 GHz FMCW front end
  (lecture 15's chip [R25]) feeding CPA/TTC logic [R26] with authority over the
  brakes. Regulators score both misses (crash not prevented) *and* false
  positives (phantom braking at highway speed) — the same two-sided table your
  homework's truth table makes you fill.

### 2.6 The capstone pipeline — the course converges (1:48–1:50)

Slide cue: the full chain — waveform (L15) → channel (L1) → front end (L10–12) →
snapshots (L13/16) → range-Doppler (L15) → CFAR (L14) → DOA (L16) → track →
decide. Every arrow is a lecture; the homework runs the last four boxes on
provided outputs of the first five. Two hours from now you will have run it.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the capstone assembled, refereed, and deliberately broken (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Run from `lab/`;
the walkthrough imports the homework toolkit — the capstone assembles the
course's own parts, and says so.

### 3.1 Setup verification (2:00–2:04)

Cell 3.1: versions, plus the one new import — pyargus, this week's independent
referee. Print the array's identity: N = 16, 77 GHz, d = λ/2 = 1.9467 mm,
HPBW = 6.35°. Anyone whose `setup_check.py` failed pre-class pairs up now.

### 3.2 Snapshots and beamscan, written live (2:04–2:12)

Cell 3.2: `sample_cov` is one line; `beamscan` is four. One drone planted at
−12°, 10 dB, 64 snapshots. The peak prints at **−12.00°** and reads **+9.91 dB**
— the spectrum reads per-element SNR, and say why (the /N² normalization).
Repeat hour 1's framing at the keyboard: this is hw13's array factor run
backwards.

### 3.3 MVDR vs beamscan — the null appears on screen (2:12–2:20)

Cell 3.3: `mvdr` is five lines (point at `np.linalg.solve` — no explicit inverse;
lecture 4's numerics hygiene). Two drones 1.5 beamwidths apart: both methods show
two peaks; MVDR's are needles. Then the jammer: drone −10°/10 dB, jammer
+25°/50 dB. Beamscan at the drone's angle: **+24.86 dB of jammer sidelobe** — the
drone is under the skirt. MVDR: **+20.92 dB** — the drone, back at full gain. Put
`hour3_spectra.png` on the projector and let the picture sit: the blue curve is
lecture 13's pattern being abused by a strong interferer; the orange curve is one
matrix inverse fixing it.

### 3.4 Monopulse refinement (2:20–2:27)

Cell 3.4: Σ and Δ as two weight vectors, slope calibrated from steering vectors
(**0.2195/deg**), then three targets: +0.90° → +0.914°, +1.70° → +1.783°,
−2.30° → −2.508°. Two beams, one division, angle to hundredths of a beamwidth —
and the −2.3° row is the caveat in numbers (the discriminant's linear region has
edges). Lecture 7's comparator, closed.

### 3.5 The capstone pipeline, one scene end to end (2:27–2:35)

Cell 3.5: the fast-intruder scene. Toolkit frames carry (R, v) — hw15's output
conventions, receding positive — and snapshots; beamscan appends θ; the α-β
filter turns positions into a state; four lines of CPA; the rule decides.
Printout: `fixed_wing: CPA in +1.17 s at 14.71 m -> ALERT` (closed-form truth:
+1.16 s, 14.60 m) and `leaving_drone … no alert`. Say the sentence on the slide
out loud: *waveform → channel → snapshots → (R, v) → θ → track → decision: every
arrow is a lecture.*

### 3.6 The pyargus cross-check (2:35–2:39)

Cell 3.6: same snapshots into pyargus — with the convention mapping done in two
visible lines (their angles run from the array *axis*, cos θ; ours from
broadside, sin θ; feed 90° − θ. Their covariance eats snapshots-by-rows;
transpose). Peak deltas print **0.000°** for Bartlett-vs-beamscan and
Capon-vs-MVDR. Moral, one sentence: agreement to the grid step between two
independently coded implementations is the referee principle's last appearance —
and the two lines of convention mapping are half of real interoperability work.

### 3.7 Deliberate bug — the beamformer that nulls its own target (2:39–2:44)

Cell 3.7, the syllabus-mandated finale bug: MVDR with K = 8 snapshots of a
16-element array. Target at +8°, 15 dB; honest reading db(1 + N·p) = 27.05 dB.
The bugged spectrum reads **−114.45 dB at the target** — the adaptive beamformer
nulled the one real thing in the data — and 29% of the "power" spectrum is
*negative*, because a rank-8 R̂ is not a covariance and MVDR trusted it anyway.
Beamscan on the same 8 snapshots: +16.4 dB, unbothered. The fix, one term:
diagonal loading, R̂ + 10 dB·I → **+27.74 dB**, peak +8.04°. Close with the
hour-1 sentence: adaptivity is a loan against the covariance estimate; K pays it
back; loading is collateral.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. The story: the corridor guard — two crossing drones,
a fast fixed-wing, and a jammed afternoon; five verdicts including two correct
*non*-alerts. Module 1 is the core (spectra + the resolution study); module 2
plugs your θ into the provided (R, v); module 3 is CPA and the decision.
**Predictions first**: Q1 (1.5 beamwidths — who resolves, and where it flips)
and Q2 (what the jammer does to each spectrum) are answered before running.
Referees: pyargus at 0.5°, closed-form CPA at 5 m, and the truth table at 5/5.
Budget ≤ 3 hours. AI use assumed and welcome — predictions and reconciliations
must be yours.

### Wrap-up — the course (2:48–2:50)

Slide cue: lecture 1's block diagram, reprised — every box now stamped *opened*.

Sixteen weeks ago you priced this machine from the outside: a radar equation, an
R⁴, and three detection ranges. Then you opened every box: lines and the Smith
chart taught you what a cable really is; S-parameters gave you the language;
microstrip, couplers, and filters built the plumbing; noise, amplifiers, and
mixers built the receiver; antennas, detection statistics, FMCW, and today's
beamforming built the sensor. And the drone thread ran the whole way: lecture 1
**priced** it (4.11 km), lecture 14 **detected** it honestly (P_d, P_fa, CFAR),
lecture 15 **classified** it (the HERM comb that separates a drone from a bird),
and today you **located** it through a jammer and **decided** — correctly, all
five verdicts — what to do about it.

The last sentence of the course: every block in that diagram is now a thing you
have computed, broken on purpose, and verified against a referee — which is the
only definition of "understood" this course ever used. Go build the seventeenth
lecture yourselves.

---

## References

- [R4] Orfanidis, *Electromagnetic Waves and Antennas*, chs. 22–23 (arrays, DOA)
  — free: https://www.ece.rutgers.edu/~orfanidi/ewa/
- [R25] Hasch et al., "Millimeter-Wave Technology for Automotive Radar Sensors in
  the 77 GHz Frequency Band," *IEEE Trans. MTT*, 2012.
- [R26] Patole, Torlak, Wang, Ali, "Automotive Radars: A review of signal
  processing techniques," *IEEE Signal Processing Magazine*, 2017.
- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems* (RES.LL-001),
  tracking lecture — free: https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
- [R29] arXiv survey on UAV detection and classification (the drone-detection
  landscape; course pack).
- [R17] Mailloux, *Phased Array Antenna Handbook* (reference).
- Capon, "High-Resolution Frequency-Wavenumber Spectrum Analysis," *Proc. IEEE*,
  1969 (the MVDR original — three pages of the derivation we did today).
