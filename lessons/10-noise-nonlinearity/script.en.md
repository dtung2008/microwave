# Lecture 10 — Noise & Nonlinearity: the Receiver's Two Ceilings

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (`pip install -r requirements.txt`: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1 (dB, noise floor, the radar equation) and 4
(two-ports, cascading); basic probability (a variance is enough).
**Pre-class setup:** the course venv from lecture 1 and run
`lab/setup_check.py` — it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: noise, and how a chain shares the blame (0:00–0:50)

### 1.1 The two ceilings (0:00–0:08)

Slide cue: one vertical axis, power in dBm; a floor labeled "noise" rising from
the bottom, a ceiling labeled "distortion" descending from the top, a shrinking
gap labeled "where your receiver actually works."

Open with the claim. Lecture 1 gave the radar a noise figure — NF = 3 dB — as a
single number handed down from nowhere. Lectures 2 through 9 built plumbing:
lines, matches, couplers, filters. Today we open the box the 3 dB came from, and
we find that a receiver is squeezed between **two** limits, not one. Below, the
thermal noise floor: signals weaker than it are simply gone. Above, nonlinearity:
signals stronger than a certain level start manufacturing *false* signals —
spurs — inside your own passband. Receiver design is the art of prying those two
ceilings apart, and this lecture is where the course's systems thread and its
components thread finally collide.

Three claims for today — board, leave them up:

1. **Noise cascades by Friis's 1944 formula, and the first stage rules.** Every
   stage's noise is forgiven by the gain in front of it. Get the first meter of
   the chain wrong and no later brilliance recovers it.
2. **Nonlinearity is a Taylor series, and every spur is algebra.** Harmonics,
   compression, intermodulation — all fall out of cubing a cosine. IP3 is a
   *fiction* — an extrapolated crossing no amplifier survives to — that predicts
   *real* spur levels to fractions of a dB.
3. **Ordering, not parts, sets this radar's range.** The homework hands every
   student the same five blocks. The twenty legal orderings share identical
   gain — and span 12.9 dB of noise figure, which the radar equation's fourth
   root converts into a **factor of 2.1 in drone detection range**.

Pre-empt the question forming in the back row: *"isn't noise a random-process
course?"* Answer honestly: the statistics live one course over; what an RF
engineer needs is the *bookkeeping* — powers, temperatures, and two cascade
formulas — and that bookkeeping is exact, checkable, and short. Every formula
today lands as a number the checker prints.

### 1.2 Where noise comes from — derived twice (0:08–0:20)

Slide cue: a lone resistor at temperature T, terminals open, a fuzzy voltage
trace across it.

**Level 1 — the fast version.** Every resistor at temperature T is a noise
generator delivering **available power kTB** into a matched load: k is
Boltzmann's constant, T the physical temperature, B the bandwidth you agree to
listen in. No current flows on average; the electrons just jostle. At the IEEE
reference T₀ = 290 K this is the −173.98 dBm/Hz of lecture 1 — the number every
datasheet quotes — and 1 MHz of bandwidth puts the floor at −113.98 dBm. Johnson
measured it in 1928; Nyquist explained it the same year, in the paper directly
before Johnson's in the same journal issue.

**Level 2 — first principles: available power from a resistor.** Say where kTB
actually comes from, because the fine print matters later. Nyquist's argument:
the resistor's open-circuit noise voltage has spectral density v̄² = 4kTR per
hertz (that is the measured Johnson result; Nyquist derived it from
equipartition — thermal modes on a transmission line connecting two resistors,
each mode carrying kT, detailed balance forcing the exchange to be equal).
Now ask what *power* a matched load R extracts: the source R and load R divide
the voltage, the load sees v/2, and receives (v̄²/4)/R = (4kTR/4R)·B = **kTB**.
Two things to say slowly: the R **cancels** — a 50 Ω resistor and a 1 MΩ
resistor offer the same available noise power, which is why one number rules
all receivers; and the formula is per-bandwidth — noise is a *density*, and B
is a choice you make, not a property of nature.

Common student question, pre-empt it: *"does kTB run out at high frequency?"*
Yes — the full Planck form rolls off when hf ≈ kT, around 6 THz at 290 K. At
microwave, kTB is exact to parts in 10⁴; optics people live in the other
regime. One sentence, move on.

**Shot and flicker — one slide, honestly.** Shot noise: current is charge in
lumps; a DC current I carries fluctuation spectral density 2qI, white, and it
matters in diodes and mixers (lecture 12). Flicker: solid-state devices flicker
as 1/f below a corner frequency — irrelevant at 10 GHz, lethal after the mixer
has translated your signal to near DC, which is exactly where lecture 12's
direct-conversion demons come from. Today, thermal noise rules; file the other
two under "lecture 12 will collect."

### 1.3 Noise temperature and noise figure — and the 290 K fine print (0:20–0:30)

Two languages for the same sin, both on the board:

> **T_e** (equivalent noise temperature): pretend the receiver is noiseless and
> its own noise arrives instead from a fictitious resistor at temperature T_e
> at the input. Kelvin. No conventions attached.
>
> **F** (noise factor): F = SNR_in / SNR_out **with the source at T₀ = 290 K**.
> NF = 10·log₁₀F in dB. Conversions: F = 1 + T_e/T₀, T_e = T₀(F − 1).

The table to internalize (hour 3 prints it): NF 0.5 dB ↔ 35 K; 1.0 ↔ 75 K;
1.5 ↔ 120 K; 3.0 ↔ 289 K; 8.0 ↔ 1540 K. Point at the 3 dB row and read the
fine print aloud: **NF = 3 dB means the receiver adds almost exactly as much
noise as a 290 K source feeds it** — T_e = 288.6 K. That "almost" is the
convention showing: 3.0103 dB would be exact doubling.

Now the fine print that costs real money. F is *defined* against a 290 K
source. Point a satellite dish at cold sky and the source is 50 K, not 290 —
suddenly a receiver's "NF = 1 dB" (T_e = 75 K) is not a 1 dB penalty but a
2.4× degradation of the actual system noise. This is why satellite and
radio-astronomy people budget in T_e and kelvin, why LNA datasheets quote both,
and why section 1.5 will give you G/T. The 290 K convention is bureaucracy —
useful, universal, and slightly false everywhere.

Pre-empted misconception: *"is NF the same as loss?"* For a matched passive
attenuator at 290 K — yes, exactly: NF = its loss in dB (it attenuates the
signal and replaces the lost noise with its own thermal emission, keeping the
output noise at kT₀B). This little theorem is a workhorse: it prices every
cable and filter in today's homework, and it is the sharp end of hour 3's
deliberate bug.

### 1.4 Friis 1944 — the cascade formula, derived twice (0:30–0:42)

Slide cue: the chain SVG — five boxes, gains and F's marked, noise injected at
each seam.

The question: stages 1, 2, 3… with linear gains G₁, G₂, … and noise factors
F₁, F₂, …. What is the system F?

**Level 1 — refer everything to the front door (the fast derivation).** Stage 1
contributes its own F₁. Stage 2 adds excess noise (F₂ − 1)·kT₀B *at its own
input* — but its input sits behind gain G₁, so seen from the system input the
contribution shrinks to (F₂ − 1)/G₁. Stage 3 hides behind G₁G₂. Sum:

> **F = F₁ + (F₂ − 1)/G₁ + (F₃ − 1)/(G₁G₂) + …** — Friis, 1944 [R20].

**Level 2 — in temperature, which is why it's true.** Noise powers add in
watts, so noise temperatures add in kelvin: T_sys = T₁ + T₂/G₁ + T₃/(G₁G₂) + …
Substitute T_i = T₀(F_i − 1), divide by T₀, add the source's own 1 — and level
1 falls out. The formula is nothing but "watts add, and gain ahead of you
forgives your sins." Note what it is **not**: it is not a dB formula. Every
quantity in it is linear. Hour 3 feeds it decibels on purpose and watches it
lie plausibly.

Read from the original — put the 1944 paper on the screen [R20]; it is four
pages and assigned whole. Friis, Bell Labs, defining noise figure so that
competing receivers could be compared at all, then deriving the cascade in a
half page. Notice his worked example is a real receiving chain, his notation is
ours, and there is not one wasted sentence. Eighty years later you will apply
it unchanged tonight.

**Worked immediately, three candidate front-ends** — the homework's element
box: cable −2 dB, LNA (20 dB, NF 1.5), BPF −1.5 dB, mixer (−7 dB, NF 8), IF
amp (30 dB, NF 4). Board arithmetic, out loud, linear inside:

- **LNA on the mast** (LNA→cable→BPF→mixer→IF amp): F = 1.4125 + 0.0058 +
  0.0065 + 0.1189 + 0.1696 = 1.713 → **NF = 2.34 dB**. Read the terms: the
  cable and filter, hidden behind 20 dB, cost half a percent each.
- **LNA in the shack** (cable first): **NF = 4.04 dB**. The same cable, moved
  in front, costs its full 2 dB (the attenuator theorem) — moving it behind
  the LNA saves 1.70 of it. Why not the whole 2? Because behind 20 dB the
  cable still shaves the gain protecting the mixer and IF amp — 0.30 dB leaks
  back in. Friis's denominators are the whole story.
- **"Protect the LNA": cable→BPF→LNA**: **NF = 5.38 dB** — 3.04 dB worse than
  the mast chain. Hold this chain in memory; hour 2 gives the honest argument
  *for* it, and the war story is about someone who un-built it.

The design law, boxed: **everything in front of the first gain is paid at face
value; everything behind it is divided by that gain.** This is why the L in
LNA is the most fought-over letter in a receiver, and why homework module 2 is
a 20-way shootout over nothing but ordering.

### 1.5 Antenna temperature and G/T (0:42–0:48)

The source has a temperature too. An antenna pointed at the ground sees ~290 K
of thermal emission; pointed at clear sky at zenith, tens of kelvin; at the
sun, thousands. Call what it delivers **T_ant**, and the receiving system's
total noise temperature is T_sys = T_ant + T_e (referenced at the same plane —
be pedantic about the plane, every real spec sheet is).

The system figure of merit that satellite links and radars actually trade in:
**G/T**, antenna gain over system temperature, in dB/K — it is the receiver
half of the link budget in one number (lecture 1's SNR ∝ G/T once you expand
it). Course radar, mast chain, T_ant = 100 K: T_e = 290·(1.7134 − 1) = 207 K,
T_sys = 307 K, G/T = 33 − 10log₁₀307 = **8.1 dB/K**. One sentence of context:
buying 3 dB of G/T by dish is steel and wind load; buying it by T_e is one
better LNA — which is why this week's subject exists as a profession.

### 1.6 Hour recap (0:48–0:50)

Three sentences, then break: available noise power is kTB and the R cancels —
one floor for all receivers, −174 dBm/Hz with 290 K fine print; F and T_e are
the same fact in two currencies, and passives at 290 K have NF = loss; Friis
1944 says the first gain forgives everything behind it — 2.34 versus 5.38 dB
from ordering the *same five parts*. Hour 2 builds the other ceiling.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: nonlinearity, the fiction called IP3, and the squeeze (1:00–1:50)

### 2.1 Nonlinearity is a Taylor series (1:00–1:12)

Slide cue: a gain curve bending over, with its polynomial written on it.

Every amplifier is linear only as a courtesy. Model the courtesy's limits with
a memoryless Taylor series around the bias point:

> y = a₁x + a₂x² + a₃x³ + … (a₁ = the gain you paid for; a₃ < 0 in
> compression; memoryless is honest for narrowband work)

Feed it one tone, x = A·cos ωt, and expand on the board — this is two minutes
of trig identities and every RF phenomenon falls out:

- **cos²** gives a DC shift and a **second harmonic** at 2ω (amplitude
  a₂A²/2) — far away in frequency; your BPF eats them. Nuisance, not villain.
- **cos³** gives a **third harmonic** at 3ω — also far away — *and* a term at
  the fundamental: (3/4)a₃A³. With a₃ negative this *subtracts from the gain*:
  **compression**. Define **P_1dB**: the input level where gain has sagged
  1 dB. Every datasheet's first nonlinearity number.

Now feed it **two** tones, x = A(cos ω₁t + cos ω₂t) — two aircraft echoes, or
your signal plus the neighbor's uplink. The cube of the sum contains cross
terms 3·cos²ω₁t·cos ω₂t, and cos² splits into DC + 2ω₁, so products land at
**2ω₁ − ω₂ and 2ω₂ − ω₁, amplitude (3/4)a₃A³ each** — third-order
intermodulation, IMD3. Say the geometry slowly: if ω₁ and ω₂ are 100 kHz
apart, the IMD3 products sit 100 kHz *outside* them — **inside your passband,
next door to your signal, wearing your signal's clothes**. No filter removes
them, because they are born after every filter you own. Second-order products
(ω₁ + ω₂, ω₂ − ω₁) land far away — filterable, hence forgivable. Third order
is the villain of narrowband systems, and "third-order" is why this lecture's
numbers all have 3's and 2/3's in them.

### 2.2 IP3 — an extrapolated fiction that predicts real spurs (1:12–1:24)

Slide cue: the two-slope picture — fundamental slope 1, IMD3 slope 3, dashed
extrapolations crossing at a star.

Watch amplitudes as the drive rises: fundamental output ∝ A — slope 1 in
dB-vs-dB. IMD3 ∝ A³ — **slope 3**. Raise both tones 1 dB and the spurs jump
3 dB, closing the gap by 2. Two straight lines with different slopes must
cross; the crossing is the **third-order intercept point, IP3** — quoted at
the input (IIP3) or output (OIP3 = IIP3 + gain).

Say the honest part loudly: **no amplifier reaches its intercept** — it
compresses around 9.6 dB below (for the pure cubic: P_1dB ≈ IIP3 − 9.6 dB;
our −5 dBm LNA compresses at −14.6). IP3 is a *fiction* — the intersection of
two extrapolations. And it is the most useful fiction in receiver design,
because one number now predicts every small-signal spur:

> **P_spur below carrier = 2 × (IIP3 − P_in).** Tones at −30 dBm into the
> −5 dBm LNA: spurs 50 dB down. Hour 3 measures 49.9 — the 0.1 is the
> fundamental already compressing.

**Cascade IIP3 — the second cascade formula.** Where Friis divides noise by
the gain *behind* you, linearity is the mirror image: gain *ahead of* a stage
drives it harder, so its distortion referred to the system input grows by that
gain. In the worst case (voltages of spurs adding in phase — the honest
engineering default):

> **1/IP3_sys = 1/IP3₁ + G₁/IP3₂ + G₁G₂/IP3₃ + …** (all linear, input-referred;
> passives contribute 1/∞ = 0)

Note the duality on one slide: noise punishes what is **early and lossy**;
distortion punishes what is **late and driven**. The same 20 dB of LNA gain
that hides the mixer's noise *exposes* the mixer's linearity — and with our
numbers the LNA's own −5 dBm IIP3 is the biggest term anyway: the blame table
in hour 3 shows the LNA dominating *both* budgets. That tension has a name;
section 2.4 gives it.

### 2.3 SFDR — the spur-free dynamic range, derived and drawn (1:24–1:34)

Slide cue: the SFDR picture — both slopes, the noise floor, the red vertical
bar.

Put the floor and the fiction on one axis and ask the operational question:
over what range of input powers is the receiver *clean*? The bottom is the
**MDS** (minimum detectable signal): the floor itself, MDS = −174 +
10log₁₀B + NF dBm (SNR = 0 convention; add your required SNR for a detection
threshold — lecture 14 does). The top: the input level where the IMD3 spurs of
two in-band tones climb *out of the noise floor* — beyond it, the receiver
generates its own false targets. Derivation on the board, three lines: spur
power (input-referred) is P_spur = 3P_in − 2·IIP3; set P_spur = MDS; solve
P_in,max = (2·IIP3 + MDS)/3; subtract the floor:

> **SFDR = (2/3)·(IIP3 − MDS)** — the spur-free dynamic range, in dB, in the
> bandwidth that defined MDS.

The 2/3 is the 3:1 slope geometry, nothing more. Numbers for the mast chain
(IIP3 = −7.38 dBm, NF = 2.34, B = 1 MHz): MDS = −111.64 dBm, P_in,max =
−42.13 dBm, **SFDR = 69.5 dB**. And the bandwidth fine print that surprises
people: widen B by 10 dB and MDS rises 10, but SFDR falls only **6.67 dB** —
two-thirds of the floor shift survives; the checker prints 89.51 / 69.51 /
56.17 dB at 1 kHz / 1 MHz / 100 MHz. For radar: two targets in one beam — a
truck at close range and a drone at the edge — *are* the two tones; an SFDR
shortfall paints phantom targets between them. False targets from your own
receiver, indistinguishable from the real thing until you check the spur
arithmetic. (Lecture 14's CFAR inherits whatever ghosts we make here.)

### 2.4 The squeeze, the measurements, and the war story (1:34–1:46)

**The linearity–noise squeeze**, boxed, because it is the sentence that
defines receiver design: *sensitivity wants maximum gain as early as possible;
linearity wants minimum gain as late as possible; you cannot fully have both.*
Every knob pulls the two ends opposite ways: more LNA gain lowers NF and
lowers IIP3; a pad or filter in front raises IIP3 dB-for-dB and raises NF
dB-for-dB (the attenuator theorem, now seen from both sides at once). The
shootout you will run tonight makes the squeeze quantitative: the best-MDS
ordering and the best-SFDR ordering are **different chains**, 0.3 dB apart in
one currency and 0.44 dB in the other, and *choosing* is a judgment about the
threat environment, not a formula.

**How the two numbers are measured — in concept, one slide each.** NF by the
**Y-factor** method: a calibrated noise diode (its violence quoted as ENR,
excess noise ratio) is switched hot/cold at the receiver input; you record one
power ratio Y and invert F = ENR/(Y − 1). Hour 3 does it in four lines: ENR
15 dB source, our 1.5 dB LNA → Y = 13.69 dB → NF = 1.5000 recovered. No
signal generator, no absolute power calibration — a ratio thermometer. IP3 by
the **two-tone test**: two clean generators, one spectrum analyzer; confirm
the spurs ride slope 3, then extrapolate. The trap your future self should
hear once: make sure the spur you measure comes from the device under test and
not from the *analyzer's* own mixer — attenuate the analyzer input 10 dB; if
the spur drops 10 dB it's real, if it drops 30 it was the instrument
confessing. Instruments obey the same Taylor series.

**War story, ninety seconds.** A coastal-surveillance upgrade: the original
installation had the LNA in a weatherproof box at the antenna — the mast
chain, NF 2.3 dB. A maintenance modernization "improved" the front end: the
LNA moved indoors next to the rest of the receiver, where it could be serviced
without a ladder, plus the band filter moved in front of it for lightning
protection. Cable, then filter, then LNA: NF 5.4 dB. **Three dB of system
noise figure — half the radar's sensitivity — gone**, not to a failed
component but to a *rearrangement of working ones*. It surfaced as a slow
mystery: detection ranges quietly 16% short (3 dB across R⁴), blamed on
weather for a season. Nobody had changed a part number, so nobody thought to
re-run Friis. The moral, said plainly: **the block diagram is a design
document, and its *order* is load-bearing.** Tonight's homework plants this
exact chain and has your checker convict it.

### 2.5 Hour recap (1:46–1:50)

Nonlinearity is a Taylor series: cubes put spurs *next door*, at slope 3, and
IP3 is the fiction that prices them; the cascade formulas are mirror twins —
noise forgiven by gain behind, distortion aggravated by gain ahead; SFDR =
(2/3)(IIP3 − MDS) is the honest width of your receiver, 69.5 dB for the mast
chain in 1 MHz; and the squeeze means the "best" chain depends on which
ceiling your environment pushes on first. Hour 3: build the engine, watch the
3:1 slope with your own eyes, and commit one instructive felony against Friis.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the cascade engine, two tones, and one felony (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.1, matplotlib
3.10.x, scikit-rf 1.13.0 (pin-checked only — this lab is pure NumPy). Anyone
whose `setup_check.py` failed pre-class pairs up now; we do not debug installs
live.

### 3.2 The noise vocabulary (2:03–2:10)

Cell 3.2: kT₀ prints −173.98 dBm/Hz, the 1 MHz floor −113.98 dBm — lecture 1's
numbers, now with their derivation behind them. The NF↔T_e table prints, and
the 3 dB row says 288.6 K — point at it and repeat the fine print. Then the
Y-factor in four lines: plant a 1.5 dB LNA, "measure" it with a 15 dB ENR
source, Y = 23.3872 (13.69 dB), and F = ENR/(Y−1) hands back 1.5000 dB
exactly. A measurement that is just two power readings and one division —
this is why NF meters existed before computers.

### 3.3 The cascade engine — Friis in twelve lines (2:10–2:20)

Cell 3.3: the element dictionary (the homework's exact parts box), then
`cascade()`: walk the chain once, keep a running linear gain, accumulate
Friis's sum and the 1/IP3 sum in the same loop, convert to dB **only at the
return**. Twelve lines. Run the three candidate front-ends from hour 1:
mast 2.3387 / shack 4.0377 / filter-first 5.3792 dB — the board numbers,
confirmed by machine. The cable-move line prints 1.70 dB saved and the 0.30
that leaks back. Then the blame table: per-stage F contributions and 1/IP3
loadings side by side — the LNA tops **both** columns (1.4125 of F, 3.16 of
5.47 mW⁻¹). The squeeze, in two printed columns.

### 3.4 Two tones meet a cubic (2:20–2:30)

Cell 3.4: build the LNA's cubic honestly — a₃ = −42.16 V⁻² from IIP3 = −5 dBm,
50 Ω convention — and drive two tones at 5.00 and 5.10 MHz, on exact FFT bins
(no windows needed when you put tones on bins; lecture 15 pays for windows
properly). Step both tones −45 → −30 dBm in 5 dB moves and read the table:
spurs at −125, −110, −95, −80 dBm — **15 dB per 5 dB step**; measured slopes:
fundamental 0.9948 (already sagging), IM3 3.0000. Extrapolate: −5.0013 dBm —
the fiction, recovered from real spurs to a hundredth of a dB. The saved
spectrum (`two_tone.png`) shows the geography: IMD3 at 4.9/5.2 MHz *next door*,
harmonics banished to 15 MHz. Point at the gap between those clusters: *that
is why third order is the one you cannot filter.*

### 3.5 SFDR on one axis (2:30–2:35)

Cell 3.5: assemble MDS and SFDR for the mast chain at three bandwidths:
89.51 dB at 1 kHz, 69.51 at 1 MHz, 56.17 at 100 MHz — the floor moves 10 dB
per decade, SFDR only 6.67, the 2/3 doing its work. P_in,max prints −42.13
dBm: above that input, this receiver invents targets. The homework's `--plot`
draws the full picture with the red SFDR bar.

### 3.6 Deliberate bug — Friis fed decibels (2:35–2:42)

Cell 3.6, the felony: rewrite the cascade with dB numbers used *as if linear* —
`f += (nf_db − 1)/gain_db`. It runs. It prints **1.6470 dB** for the mast
chain — smaller than the truth (2.3387), *utterly plausible*, the kind of
number that survives a design review. Then the checks. The weak invariant —
"system NF ≥ first-stage NF" — **passes** on the mast chain (1.647 ≥ 1.5):
a true theorem, too blunt to catch this lie. The sharp invariant — hour 1's
attenuator theorem, *a 2 dB pad in front must add exactly 2.0000 dB* — prints
2.0000 for the honest engine and 0.5411 for the bugged one. Say the moral the
course has been building: **you do not catch subtle bugs by eyeballing
plausible outputs; you catch them with an invariant that must hold exactly.**
The homework checker runs this exact tripwire against your module 1.

### 3.7 The stakes — lecture 1's engine feels the ordering (2:42–2:45)

Cell 3.7: three lines re-state lecture 1's `radar_max_range_m`, and the drone
gets priced: NF 3.0 (lecture 1's assumption) → 4.106 km; NF 2.0378 (the best
of the 20 orderings) → **4.339 km**; NF 14.9267 (the worst) → **2.066 km**.
Same parts, same watts, same dish: ×2.10 in range, from ordering alone. Leave
that on screen while briefing the homework.

### Homework brief (2:45–2:48)

`lab/HOMEWORK.md` on screen. The story: the course radar's receive chain
arrives as five blocks and an empty rack — the order is yours. Module 1 is the
core: both cascade formulas, hand-rolled, linear inside (the toolkit carries
lecture 1's radar engine, so your hw1 needn't be finished). Module 2: the
20-ordering shootout, ranked by MDS *and* by SFDR — the two winners differ,
and one heavily-planted "obvious" chain is 3 dB of regret. Module 3: the
payoff — ranges through the radar engine, and the customer's 4.3 km spec
inverted to an NF budget (exactly one ordering clears it; find it).
**Predictions come first:** Q1 (the cable move — commit before you run) and
Q2 (the spur arithmetic) are answered before any command. `--check` prints
facts, not PASS/FAIL — hand-worked chains, the lossy-first tripwire, and a
two-tone referee that hands your cascade IIP3 back through actual measured
spurs. Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
reconciliations are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: Friis 1944, first gain forgives — and the same
five parts span 2.04 to 14.93 dB by ordering; the Taylor series put the spurs
next door at slope 3, and IP3 priced them without ever existing; the radar
sees the drone at 4.34 km or 2.07 km depending on which order you bolt the
same boxes together. Teaser: next lecture the LNA stops being a row in a table —
a real transistor's measured S-parameters, stability circles, and the
noise-match-versus-gain-match tension that decides that 1.5 dB.

---

## References

- [R20] Friis, "Noise Figures of Radio Receivers," *Proc. IRE* 32(7):419–422,
  1944 — four pages, assigned in full; the cascade formula at its source.
- [R2] Steer, *Microwave and RF Design*, Vol. 1 (*Radio Systems*) ch. 4 and
  Vol. 5 (*Amplifiers and Oscillators*) ch. 4 — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 10 (noise and nonlinear
  distortion — for owners of the book; parallels both hours).
- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems* (RES.LL-001),
  the receiver lecture — free context for where this chain sits in a radar:
  https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
