# Lecture 12 — Mixers, Detectors & Receiver Architectures

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course venv: numpy 1.26.4, scipy, matplotlib,
scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1 (dB, the course radar), 8 (filter specs and the
Chebyshev order estimate), 10 (noise, nonlinearity as a Taylor series), 11 (the LNA
that sits in front of everything this week).
**Pre-class setup:** course venv + run `lab/setup_check.py` — it must print
`SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: frequency conversion, and the mirror it creates (0:00–0:50)

### 1.1 Why frequency conversion exists (0:00–0:10)

Slide cue: the receiver chain from lecture 10's homework, with a question mark where
the mixer sits.

Open with the embarrassing question: your LNA (lecture 11) hands you a beautiful
10 GHz echo. Now what? Everything you want to do next — pile on 100 dB of gain,
filter one 10 MHz channel out of the band, digitize — is somewhere between painful
and impossible *at 10 GHz*. Gain at 10 GHz costs milliwatts per dB and threatens to
oscillate through every stray coupling (lecture 11's stability lecture was the
warning). A 10 MHz channel filter at 10 GHz is a 0.1% fractional bandwidth — lecture
8's order formula laughs at you. And a 10 GHz ADC (analog-to-digital converter) is a
research budget, while a 100 MS/s ADC is lunch money. **Gain, filtering, and ADCs
live at low frequency.** So we move the signal — without disturbing the information
riding on it. That operation is frequency conversion, the mixer does it, and this
lecture is about what the mixer gives and what it quietly takes.

Three claims for today — on the board, left up all lecture:

1. **Mixing is multiplication, and multiplication needs nonlinearity.** A linear
   time-invariant network can *never* create a new frequency — that is what
   eigenfunction means. Every mixer is a nonlinearity or a switch wearing a suit.
2. **The mixer is a perfect mirror.** Two RF frequencies — f_LO + IF and
   f_LO − IF — land on the *same* IF, indistinguishably. Nothing downstream can
   separate them; the only defenses act *before* the mixer. Frequency planning is
   the discipline of never needing the defense you don't have.
3. **The oscillator's skirt is a system parameter.** Phase noise, read in dBc/Hz,
   decides — through the mixer — how slow a drone your Doppler radar can see. Today
   ends with that number: 2.5 m/s for the course radar's oscillator.

Pre-empt the question the sharp students are forming: *"why not amplify at RF and
sample directly? ADCs keep getting faster."* Honest answer: direct RF sampling
exists (modern base stations do it below ~6 GHz), and it just relocates the same
problems — the sampler is itself a mixer (hour 3 shows a spectral line aliasing,
live), the jitter spec becomes the phase-noise spec, and the anti-alias filter
inherits the preselector's job. The architecture changes; this lecture's physics is
the part that doesn't.

### 1.2 Mixing is multiplication — the trig identity (0:10–0:20)

Board work, the fast derivation — one line of high-school trig that runs the entire
receiver industry:

> cos(ω₁t)·cos(ω₂t) = ½·cos((ω₁−ω₂)t) + ½·cos((ω₁+ω₂)t)

Multiply the RF (radio frequency) signal by a clean LO (local oscillator) tone and
the spectrum moves: a copy at the difference frequency, a copy at the sum. Keep the
difference — that is downconversion; the sum is filtered off. Notice what the ½
costs: the difference-frequency copy carries amplitude ½, power ¼ — an ideal
multiplier "loses" 6.02 dB into the arithmetic, half of it to the sum product you
discard. Hour 3 measures exactly −6.02 dB from an FFT, and the amplitude and phase
of the RF ride through untouched — which is the whole point: the information moved;
nothing about it changed.

Say claim 1 again, slowly, because it is the conceptual gate: a linear circuit fed a
sinusoid returns a sinusoid at the *same* frequency — sinusoids are eigenfunctions
of linear time-invariant systems; that was lecture 2's phasor bargain. To get
ω₁ ± ω₂ you must multiply signals, and multiplication is nonlinear (or
time-varying — a switch — which is the same escape hatch). So every mixer datasheet
is really answering one question: *what nonlinearity, driven how hard, multiplies
cleanly?*

### 1.3 The diode detector, and the diode promoted to mixer (0:20–0:33)

The simplest nonlinearity we own is the diode: i = I_s(e^(v/nV_T) − 1). Taylor it
(lecture 10 did): i ≈ a₁v + a₂v² + a₃v³ + …

**The square-law detector first**, because it is the mixer's ancestor and it still
ships in every power meter. Feed the a₂v² term a modulated carrier
v = A(t)·cos(ωt): squaring gives A²(t)/2 · (1 + cos 2ωt) — a baseband term
proportional to A², plus a 2ω term the capacitor eats. The diode hands you the
*envelope*, carrier discarded: the crystal radio, the diode power sensor. It is
called square-law because the output is proportional to input *power* — true only
while the signal is small (below roughly −20 dBm for a typical Schottky detector);
drive it harder and it slides into linear (peak) detection. No LO, no tuning — and
no frequency selectivity and brutal sensitivity limits, which is why lecture 1's
radar does not detect drones with a crystal radio.

**Now pump the same diode with an LO.** The a₂v² term applied to
v = v_RF + v_LO contains the cross-term 2a₂·v_RF·v_LO — there is the
multiplication of 1.2, manufactured by a nonlinearity. That is the single-diode
mixer: LO pumps the diode, RF leaks through the same junction, the cross-term is
the IF (intermediate frequency). But the same Taylor series that gave you the
cross-term gives you *everything else*: a₃ makes products with 2ω terms, a₄ makes
more, and in general the output contains **every |m·f_LO ± n·f_RF|**. That grid is
not a nuisance footnote — it is the homework's module 1 and the reason frequency
planning is a discipline. Hour 3 builds a behavioral diode and shows all 24
products to order 3, each in its exact predicted FFT bin.

**The first-principles view: real mixers are switches.** A diode pumped hard by the
LO is not multiplying gently — it is ON half the LO cycle and OFF the other half.
Model it honestly: the RF is multiplied by a ±1 square wave at the LO rate. Fourier
gives the square wave as (4/π)[cos ω_LO t − ⅓cos 3ω_LO t + ⅕cos 5ω_LO t − …], so
the products sit at (odd m)·f_LO ± f_RF, and the wanted line carries amplitude 2/π:
**conversion loss 20·log₁₀(π/2) = 3.92 dB** — the floor for any switching mixer.
Real single-diode and diode-ring mixers measure 6–8 dB; the missing few dB go to
diode series resistance, mismatch, and power re-converted from products you didn't
keep. Hour 3 measures the 3.92 to the second decimal. This switching view is why
mixer datasheets talk about LO *drive level* (+7, +13, +17 dBm rings): the LO isn't
a signal, it is the power supply of a switch, and a starved switch multiplies
badly — conversion loss rises and the spur grid blooms.

Pre-empt the balanced-mixer question now, one breath: *"my datasheet says
double-balanced — what does balance buy?"* Symmetry. A balanced ring cancels the
even-order half of the grid (and LO/RF leak-through) by subtraction — typically
50–60 dB of suppression for (2,2)-type products — but cancels nothing about the
image, which is odd-order, order (1,1), and perfectly legal. Balance cleans the
grid; it does not un-mirror the mirror. Hold that; the homework's audit makes the
distinction concrete with a severity column.

### 1.4 The image — the mirror, derived and drawn (0:33–0:45)

The centerpiece derivation, twice, both short.

**Fast version, pure algebra.** The receiver keeps |f_LO − f_RF| = f_IF. Solve for
f_RF: there are two solutions, f_LO + f_IF and f_LO − f_IF. Both are *exactly* IF
away from the LO, one on each side; the mixer maps both onto f_IF with equal
conversion gain. If your signal is at f_LO + f_IF, then f_LO − f_IF is the **image
frequency** — 2·IF below the signal — and anything living there arrives on your IF
in perfect disguise.

**Slower version, on the spectrum picture** (slide: the frequency axis with LO in
the middle, signal right, image left, both arrows folding onto IF). The mixer
translates the whole axis by f_LO and *folds* it at zero — negative frequencies land
on positive. The fold is the mirror. Draw it once with the signal high-side, once
low-side: choosing the LO side chooses which neighborhood of spectrum becomes your
image. One consequence worth thirty seconds now because it bites in lecture 15: a
**high-side LO inverts the IF spectrum** (the fold reverses frequency order), so a
positive Doppler shift arrives as a negative IF offset — your processing must know
which side the LO sat on, or every velocity in the radar has the wrong sign.

And the noise fine print, because lecture 10 trained you to ask: the mixer folds
the *noise* at the image onto your IF too. A receiver with no image filtering pays
up to 3 dB of noise figure just for the fold — that is the difference between SSB
(single-sideband) and DSB (double-sideband) noise figure on every mixer datasheet,
and a classic way to be disappointed by a component that met its spec.

War story, 90 seconds: a campus perimeter radar, S-band, 2.9 GHz, low-side LO at
2.65 GHz with a 250 MHz IF — a clean design on paper. Commissioning week it
detected every airport shuttle bus at extraordinary range, and only shuttle buses.
Nobody could find the fault because there wasn't one: 2.9 − 2·0.25 = **2.4 GHz.
The image band was the parking lot's Wi-Fi.** Every bus carried an access point.
The radar was working perfectly — as a Wi-Fi detector. The fix was a frequency
plan, not a repair; the homework hands you the same trap at X-band with a 9.6 GHz
airfield radar in the Wi-Fi's seat, and hour 3 re-enacts the discovery.

Common student question, pre-empted: *"can't I just filter the image out?"* Yes —
that is exactly the preselector's job, and it works **if the image is far enough
away to filter**. The image sits 2·IF from the signal, so the *IF choice* sets the
filter difficulty. That trade is hour 2's opening act, and the homework's core.

### 1.5 Hour recap (0:45–0:50)

Four sentences, then break: conversion exists because gain, filtering, and ADCs
live low. Mixing is multiplication, multiplication needs nonlinearity or switching,
and the full m·f_LO ± n·f_RF grid always comes with it — the switch's floor is
3.92 dB. The image is the perfect mirror at 2·IF away, folded noise included, and
no downstream cleverness unfolds it. A radar once detected shuttle buses because
nobody asked who transmits in the image band — hour 2 is how you ask.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: architectures, the plan, and the skirt (1:00–1:50)

### 2.1 The superheterodyne, and frequency planning (1:00–1:18)

Slide cue: the superhet block diagram — preselector → LNA → mixer (LO below) → IF
filter → IF gain → ADC, every stage stamped with its frequency.

Armstrong's 1918 idea, still the default a century later: convert the tunable RF
problem to a **fixed IF** where gain is cheap, filters are sharp, and the ADC is
happy; tune by moving the LO, not the filters. Walk the blocks with our numbers —
the course radar's receiver, RF 10.0–10.4 GHz, one 10 MHz channel at a time:
preselector passes the whole 400 MHz tuning band; LNA sets the noise figure
(lecture 10's Friis says so); the mixer translates the tuned channel to the IF; the
IF filter — *fixed*, sharp, cheap — does the real selectivity; the ADC digitizes.

Now the planning question, worked on the board exactly as the homework will demand
it. **Choosing the IF is a two-sided squeeze:**

- **Image rejection wants IF high.** The image sits 2·IF from the signal. Our
  preselector must pass 10.0–10.4 GHz — so if 2·IF < 400 MHz, the image of one tune
  lands *inside the band the preselector must pass*. No filter order fixes that; it
  is architectural. First hard rule: **IF > 200 MHz.**
- **Everything else wants IF low.** Filters at low frequency are low-order
  (lecture 8's ω_s grows with offset/f₀); IF gain is cheap; and the ADC's analog
  input bandwidth (500 MHz for our part) caps how high the IF may ride.

Candidate 1, the classic 60 MHz IF (lecture 8's homework filter!): image 120 MHz
from the signal, inside our own tuning band. Dead on arrival — not by a filter
spec, by architecture. Candidate 2: a catalog 321.4 MHz IF filter (a real catalog
number — spectrum analyzers have used it for decades). Image band 2 × 321.4 =
642.8 MHz away. Which side? Now the **emitter table** enters — the site survey:
marine radars 9.30–9.50, the airfield's own radar at 9.60 (2 km away), police and
amateur activity 10.50–10.55, a backhaul link 11.20–11.70 GHz on our own mast.
Low-side LO: image band 9.357–9.757 GHz — *contains the airfield radar and half
the marine band*. High-side LO: image band 10.643–11.043 GHz — clear of everything.
Verdict on the board: **high-side LO, IF = 321.4 MHz**, and the general lesson
above it: *the algebra had two solutions; the emitter table voted.* The homework's
module 2 turns this vote into an audit over every product to order 3, and finds the
one collision that survives — a (2,2) product of the police band. The IF filter
cannot even see it (the product arrives *at* the IF), and the preselector's spec
point is the image, not the police band — whatever rejection it happens to give at
10.5 GHz is luck, not design. The dependable number must come from mixer balance
(that is ANSWERS Q3).

Close the loop with the ADC, because the syllabus put a 100 MS/s part in the spec
and 321.4 MHz is comfortably above 50 MHz: the sampler *is* a mixer — claim 1 with
a clock. Sampling at f_s folds the spectrum at every multiple of f_s/2 (hour 3
already caught a line aliasing in the switching-mixer cell); each interval
[k·f_s/2, (k+1)·f_s/2] is a **Nyquist zone**, and an IF band that fits entirely
inside one zone lands intact — inverted in odd cases, but intact — at baseband.
321.4 MHz sits mid-zone-6 of a 100 MS/s converter. Undersampling is standard
practice, the IF filter doubles as the anti-alias filter, and the plan's real ADC
constraints are the zone fit and the 500 MHz input bandwidth. The filter specs this
plan implies, in lecture 8's language, land in the homework: preselector n = 7
Chebyshev for 60 dB at the image edge; IF filter n = 4 for 60 dB at the zone
edges. Two numbers that *are* the sentence "filtering lives low."

### 2.2 Direct conversion — the demons, one slide (1:18–1:23)

One slide, honestly. Set f_IF = 0: the LO sits *on* the signal, image = the signal's
own other sideband, no image band to plan around, no IF filter to buy — every
smartphone does this. The price, listed fast: **DC offset** (LO leaks into its own
mixer, self-mixes to a rock-solid zero-frequency error sitting exactly on your
signal), **flicker noise** (1/f corner of the transistors sits in mid-channel),
**IQ imbalance** (the two mixers of the quadrature pair never quite match, the
constellation smears), and even-order distortion (a₂, harmless in a superhet,
lands at DC here). Fixable — with per-chip calibration and DSP, at smartphone
volumes. A radar that wants to see *slow things near zero Doppler* — our drone —
should think very hard before parking its most precious octave of spectrum on top
of its own DC offset and flicker corner. The course radar stays superhet.

### 2.3 Phase noise — the skirt that buries the slow drone (1:23–1:38)

Slide cue: the phase-noise plot — L(f) in dBc/Hz vs offset, log-log, with the
course LO's profile drawn.

A real oscillator is not a line; it is a line wearing a skirt. Write the signal as
cos(2πf₀t + φ(t)) — φ(t) is phase noise, and its one-sided spectrum, quoted as
**L(f) in dBc/Hz** (dB relative to the carrier, per hertz, at offset f from it), is
the second most important plot on any oscillator datasheet after the price. Read
our course LO's profile from the slide, out loud, because reading this plot is the
skill: −40 dBc/Hz flat inside the 10 Hz PLL (phase-locked loop) bandwidth, then
−30 dB/decade to −70 at 100 Hz (the 1/f³ flicker-FM region), then −20 dB/decade —
−90 at 1 kHz, −110 at 10 kHz. Integrated, this LO carries barely 3° RMS of jitter
(hour 3 prints 3.13°) — a *superb* number. Hold that thought.

**Leeson, qualitatively** — where skirts come from, no derivation, one idea: an
oscillator is an amplifier whose noise circulates through a resonator forever. The
resonator's Q shapes how fast the loop forgets a phase kick: inside the half
bandwidth f₀/2Q, noise integrates into a 1/f² skirt (plus the transistor's flicker
making 1/f³ close in); outside, the amplifier's plain noise floor. So the levers
are exactly three — resonator Q, power through the loop, device flicker — and that
is why a 10 GHz oscillator built on a microstrip resonator (Q ≈ 100, lecture 6)
wears a wide skirt while a sapphire or crystal-derived source wears a narrow one,
and why you cannot "just buy a cleaner oscillator" without buying a better
resonator.

**Why a radar cares — through the mixer.** Every echo the mixer downconverts
carries the LO's skirt as a sideband suit. For most echoes, who cares — the skirt
is 70+ dB down. But radar has one special echo: **clutter**. The ground return is
huge — lecture 14 will hand you 60 dB over the drone as the standard number — and
it sits at zero Doppler wearing the full skirt. The drone's Doppler line lives at
f_d = 2v/λ ≈ 68 Hz per m/s of speed (10.2 GHz carrier). A slow drone's line must
out-shout not the thermal floor but *the clutter's phase-noise skirt at its own
offset*.

Work it, on the board, to a number — this is the homework's module 3 and the slide
does it in four lines. Visibility needs the line to clear the local skirt by the
course's 13 dB in the Doppler bin (1.5 Hz ENBW — equivalent noise bandwidth — for
our 1 s Hann frame). Condition: L(f_d) ≤ −60 − 13 − 10log₁₀(1.5) = **−74.8 dBc/Hz**.
Read the profile backwards: −74.8 sits on the −20 dB/decade segment at
f = 100·10^(4.76/20) = **173 Hz**, i.e. v_min = 173/68 = **2.54 m/s**. A drone
crossing at jogging speed: visible. The same drone *hovering into a drift*:
gone — not for lack of transmit power, not for RCS, but because the oscillator's
skirt is standing on it. Say the punchline while it hurts: **you can lose a target
to a component that consumed zero dB of your link budget.** And the slope is the
consolation prize: in the −20 dB/decade region, every halving of speed costs
6.02 dB of margin — the homework's Q2 makes you predict exactly this before
running it.

Pre-empt the fair objection: *"the TX and LO are the same oscillator — doesn't the
echo's noise correlate away when they mix?"* Sharp, and yes: for short delays the
skirt partially cancels (range correlation); our worked number is the honest
long-range worst case, and the effect only helps close-in clutter. The homework
states the assumption; lecture 15's short-range FMCW world is where the
cancellation genuinely earns its keep.

### 2.4 The FMCW dechirp receiver — the mixer is the ranging engine (1:38–1:46)

Slide cue: the f–t diagram — transmit ramp, delayed echo ramp, constant vertical
gap between them; below it, the dechirp receiver: TX chirp → (coupler) → mixer ←
echo, → low-pass → ADC.

Bridge to lecture 15, hardware insight now, derivation then. FMCW
(frequency-modulated continuous wave) transmits a chirp — frequency ramping B hertz
in T_c seconds, slope α = B/T_c — and mixes the received echo *with the transmit
chirp itself*: the LO is the waveform. An echo delayed by τ = 2R/c is the same
ramp shifted right; at every instant the two ramps differ by a **constant**
frequency f_b = α·τ = 2Rα/c. The mixer — the very cos·cos identity from 1.2 —
turns that constant difference into a constant **beat tone**: range became a
frequency, and the receiver became "a mixer plus an FFT."

Numbers, because this closes today's ADC story with a flourish: give the course
radar its lecture-15 waveform — the full 400 MHz band chirped in 1 ms,
α = 4×10¹¹ Hz/s. Beat rate: 2α/c = 2668.5 Hz per meter of range. The drone at
3 km: f_b = 8.01 MHz. The 100 MS/s ADC's first Nyquist zone reaches 18.74 km of
range. Stand back from that: a **400 MHz-wide** transmitted problem arrived at the
ADC as a single-digit-MHz tone — the mixer performed the compression, analog, for
free. That is why every automotive radar on earth (TI's white paper [R34] is the
readable industrial account) is an FMCW dechirp machine. What the dechirp receiver
does to images, and why its beat spectrum is one-sided until Doppler complicates
it — that is ANSWERS Q5's teaser and lecture 15's opening.

### 2.5 Hour recap (1:46–1:50)

The superhet converts a tunable problem into a fixed-IF problem, and the IF choice
is a squeeze: image rejection pushes it up, everything else pushes it down — our
plan: high-side LO, IF = 321.4 MHz, preselector n = 7, IF filter n = 4, and the
emitter table cast the deciding vote. Direct conversion trades the image for DC
demons; radar declines. Phase noise is the LO's skirt, Leeson says Q and power set
it, and through the mixer it prices the slowest visible drone: 2.54 m/s for our
profile. And FMCW is the mixer promoted to ranging engine — 400 MHz of problem,
8 MHz of ADC. Hour 3 builds every one of these as ten lines of NumPy each, breaks
one frequency plan the way the shuttle-bus radar broke, and briefs the homework.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: behavioral mixers in NumPy, the plan calculator, and the skirt (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Audio-rate
stand-ins throughout — f_LO = 800 Hz, f_RF = 530 Hz, 1 Hz FFT bins — because the
physics is scale-free and an 8192-point FFT is instant.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.1, matplotlib
3.10.x, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed pre-class pairs up
now — do not debug installs live.

### 3.2 Mixing is multiplication, measured (2:03–2:09)

Cell 3.2: multiply two unit cosines, FFT. Exactly two lines — 270 Hz and 1330 Hz,
amplitude 0.5000 each; the next-largest bin is 1.5×10⁻¹⁴. Point at the printout:
the trig identity is not an approximation, and the −6.02 dB conversion is the ½
made audible. *This is the cleanest referee we will ever own: high-school trig,
checked to machine precision by an FFT.*

### 3.3 The switching mixer (2:09–2:15)

Cell 3.3: replace the LO cosine with `sign(cos)` — the ±1 switch. The odd-m comb
appears: 270 and 1330 (amp 0.6367 = 2/π), 1870 and 2930 (the 3·LO pair, one third),
3470… and one impostor at 3662 Hz. Ask the class before explaining: the 5·LO sum
at 4530 Hz is beyond Nyquist and has **aliased** — sampling folded it, because
sampling is a mixer too. Conversion loss prints −3.92 dB against theory −3.92.
This one cell contains the whole hour-2 undersampling slide in miniature.

### 3.4 The image, by construction (2:15–2:21)

Cell 3.4: LO at 1000 Hz, IF 270. A signal at 1270 Hz: IF line, amp 0.5000. An
interferer at 730 Hz: IF line, amp 0.2500, *same bin*. Both together: one line,
amp 0.7500 — one bin, two owners, inseparable. Let the silence land, then say it:
every algorithm you will ever write lives downstream of this bin. The defense was
before the mixer or nowhere.

### 3.5 The full grid — the behavioral diode (2:21–2:27)

Cell 3.5: `i = exp(1.2·cos ω_LO t + 0.9·cos ω_RF t)` — a diode in one line, every
power of its argument included. FFT, overlay the 24 predicted |m·f_LO ± n·f_RF|
lines to order 3: **24/24 peaks land in their exact bins** — (2,2) at −31.9 dBc,
(3,3) at −62.8 dBc, and beyond the grid 4·f_LO at −41.8 dBc, because the grid does
not stop where the homework's order-3 audit stops. Saves `mixer_grid.png`. This
cell is the homework's module-1 referee, previewed: your closed-form table and this
FFT must agree bin-for-bin.

### 3.6 The frequency-plan calculator (2:27–2:33)

Cell 3.6: scale up to the course radar — RF 10.0–10.4 GHz, 10 MHz channels,
100 MS/s ADC, the four-emitter site survey typed in as data. Build `image_band()`
and a three-check `audit()` in a dozen lines. Then evaluate an innocent plan:
**low-side LO, IF = 321.4 MHz** — the catalog filter. The checks stream by: IF sits
in ADC Nyquist zone 6, fits: True. Image band 9.3572–9.7572 GHz, outside our own
band: True. "Every self-consistency check passes. Ship it?" — leave the ellipsis
on screen and go to the next cell.

### 3.7 Deliberate bug — the plan that works until you consult the table (2:33–2:39)

Cell 3.7: same plan, one more call — the emitter audit. Two collisions print:
marine radars 9.300–9.500, and **the airfield radar 9.595–9.605 — inside the image
band, full conversion gain, zero rejection available.** Tuned to 10.2428 GHz, the
9.6 GHz radar *is* the image. Nothing in cell 3.6 was wrong; the plan was
internally consistent and externally doomed — exactly the shuttle-bus radar, and
exactly why "works" is not a property of a frequency plan, only "audited" is. Then
one line flips the LO high-side: image band 10.6428–11.0428 GHz, collisions: 0.
Same IF filter, same ADC. The fix cost one wire; finding it after installation
costs a site visit.

### 3.8 Phase noise meets the slow drone (2:39–2:45)

Cell 3.8: synthesize the LO from the dBc/Hz profile (the homework toolkit's exact
method, fixed seed), verify the synthesis — measured L(100 Hz) = −70.6 vs profile
−70, L(1 kHz) = −90.5 vs −90 — and print the integrated jitter: 3.13° RMS,
*tiny*, say it again, because the next lines are the point. Put 60 dB of clutter
on the LO and two drones in the scene: 3 m/s → line-over-skirt 14.4 dB, visible;
1 m/s → 2.5 dB, **buried**. Same RCS, same range, same transmit power — only the
oscillator decided which drone exists. The homework's module 3 measures the exact
crossover and checks it against the analytic bound (2.542 m/s) to within 5%.

### 3.9 The dechirp teaser (2:45–2:47)

Cell 3.9: a 2 kHz audio chirp, a 50 ms delayed copy, one multiply, one FFT: beat
measured 100.0 Hz against α·τ = 100.0. Then the printed scale-up: at the course
radar's lecture-15 waveform, 2668.5 Hz of beat per meter, the 3 km drone lands at
8.01 MHz, and the 100 MS/s ADC covers 18.74 km. The mixer is the ranging engine;
lecture 15 takes it from here.

### Homework brief (2:47–2:50, run over the wrap-up if needed)

`lab/HOMEWORK.md` on screen. The story: plan the course radar's receiver —
RF 10.0–10.4 GHz, the four-emitter survey, the 100 MS/s ADC — then find the
slowest visible drone. Module 1 is the m,n grid and the image bands (two referees:
closed form and the diode FFT); module 2 is **the core** — the audit and the
filter specs, in lecture 8's language; module 3 is the skirt-limited Doppler
floor. **Predictions come first:** Q1 (which LO side survives the 9.6 GHz
emitter) and Q2 (the price of hovering — predict v_min from the profile) are
answered *before* running. `--check` prints facts, not PASS/FAIL; `--plot` draws
the feasibility chart and the skirt picture that Q1 and Q2 discuss. Budget
≤ 3 hours. AI use assumed and welcome — the predictions and reconciliations must
be yours.

### Wrap-up (2:50)

Recap against the three claims: multiplication needs nonlinearity — you built
three mixers in twelve lines and measured −6.02 and −3.92; the mirror is perfect —
two owners of one bin, and a plan audit is the only defense that works before
installation; the skirt is a system parameter — 3° of jitter still erased the
1 m/s drone. Teaser: next lecture the receiver finally gets its antenna — arrays,
beamwidth, and why the drone-hunting radar's aperture is a wavelength argument
wearing hardware.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 5 (*Amplifiers and Oscillators*),
  chs. 5–6 (mixers; oscillators and phase noise) — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 13 (for owners of the book — diode
  detectors, mixers, and the receiver-architecture sections this lecture parallels).
- [R34] Iovescu & Rao, "The Fundamentals of Millimeter Wave Radar Sensors," TI
  white paper SPYY005 — free: https://www.ti.com/lit/spyy005 (the FMCW dechirp
  receiver, drawn the way industry draws it).
- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems* (RES.LL-001),
  receiver lecture — free:
  https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
