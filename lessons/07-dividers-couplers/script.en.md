# Lecture 7 — Power Dividers & Couplers

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (the lecture-1 environment unchanged: numpy
1.26.4, scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1–6 — this lecture leans hardest on lecture 2's
quarter-wave transformer, lecture 4's S-parameters and the invariant suite
(`is_reciprocal`, `unitarity_residual`, `passivity_residual` — they referee
this week's homework), and lecture 6's comfort with cascaded sweeps.
**Pre-class setup:** run `lab/setup_check.py` — it must print `SETUP OK` (the
smoke test assembles a small Wilkinson in `skrf.Circuit`; nothing new to install).

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: three-ports, an impossibility theorem, and the Wilkinson (0:00–0:50)

### 1.1 One transmitter, four antennas (0:00–0:08)

Slide cue: the corporate-feed picture — one transmitter at the root, three
splitters, four antenna elements.

Open with the problem, not the parts list. Lecture 13 will hand you a
four-element array and say: feed it. Equal amplitude, equal phase, all four
elements — because every dB of imbalance and every degree of phase error goes
straight into the array pattern as sidelobe. And one more demand that sounds
paranoid until you price it: the four outputs must be **isolated** from each
other. Antennas reflect — ice, radomes, a neighbor's coupling — and element 2's
reflection must not ride back down the tree and re-emerge as a change in
element 3's drive.

So the component we need this week is embarrassingly humble: a box that splits
one signal into two. The entire lecture is about why that humble box is
*provably impossible* to build perfectly with three ports, and about the two
families of escapes — a resistor in exactly the right place (the Wilkinson),
and a fourth port (the couplers and hybrids that fill the rest of the hour).

Three claims for today — on the board, left up all lecture:

1. **A three-port cannot be matched, reciprocal, and lossless at once.** Pick
   two. The proof is three lines of lecture-4 algebra, and hour 3 prints its
   fingerprint as the number 1.000000.
2. **Even/odd analysis is the technique of the week** — it dissolves the
   Wilkinson in four lines and the branch-line in six, and it returns in
   lecture 9 wearing coupled-line clothes. Learn the technique, not the
   answers.
3. **Four-port couplers are specified by three numbers — C, D, I — and two of
   them are routinely confused.** Isolation is *not* directivity; they differ
   by exactly the coupling, and the confusion has a price tag hour 2 computes.

Pre-empt the question forming in the back: *"can't I just solder three lines
together?"* You can — a tee junction. It splits. It is also, as we prove in
about four minutes, necessarily mismatched or leaky, and its outputs talk to
each other freely. The whole week is the difference between "it splits" and
"it feeds an array."

### 1.2 The impossibility theorem — proved twice (0:08–0:20)

Board work. This is the cleanest theorem in the course, and it earns its keep
for sixteen weeks: when a vendor claims a matched, lossless, reciprocal
three-way splitter, one of those three words is marketing.

Setup, in lecture-4 language. A three-port has a 3×3 S-matrix. Assume all
three properties at once:

> matched at every port: S₁₁ = S₂₂ = S₃₃ = 0
> reciprocal: S = Sᵀ — three independent numbers S₁₂, S₁₃, S₂₃
> lossless: SᴴS = I — every column has unit norm, distinct columns are orthogonal

**Level 1 — the fast proof.** Write the three column-orthogonality conditions
(zeros on the diagonal do most of the work):

> columns 1·2: S₁₃*S₂₃ = 0 columns 1·3: S₁₂*S₂₃ = 0 columns 2·3: S₁₂*S₁₃ = 0

At least two of S₁₂, S₁₃, S₂₃ must vanish. But the unit-norm conditions read
|S₁₂|² + |S₁₃|² = 1 (and cyclic) — with two entries dead, some column norm is
0 ≠ 1. Contradiction. No such device. Three lines, as promised.

**Level 2 — the slow proof, which is the same proof said physically.** Column
1 having unit norm says: power into port 1 all comes out somewhere — that is
losslessness. Columns 1 and 2 being orthogonal says: the outputs produced by
driving port 1 and the outputs produced by driving port 2 cannot overlap
constructively — that is also losslessness, applied to driving both ports at
once (superposition must conserve power for *every* excitation, not just the
ones in the test plan — hold that phrase, it returns in Q3 of the homework).
The match assumption deleted the diagonal, so orthogonality has too few
degrees of freedom left, and the device is over-constrained. The theorem is
not about cleverness of topology — no arrangement of lossless plumbing behind
three matched ports can dodge it, because we never assumed a topology.

Expect and welcome the objection: *"but a resistive splitter exists, I own
one."* Yes — it picks match + reciprocity and pays with loss. That is the next
section: the theorem is a menu, not a wall.

### 1.3 Pick two — the escape map (0:20–0:28)

Slide cue: the triangle — matched / reciprocal / lossless — with a device
living on each edge.

- **Give up lossless: the matched resistive star.** Three 16.7 Ω resistors to
  a common node (Z₀/3 each). Matched everywhere, reciprocal, S₁₂ = S₁₃ = S₂₃
  = ½: every through-path loses 6.02 dB, of which 3 dB is the honest split and
  3 dB is heat. Worse: the outputs hear each other at −6 dB — **no isolation**.
  Fine for lab dividers and DC-coupled test jigs; disqualified as an array
  feed twice over (loss *and* crosstalk).
- **Give up reciprocity: the circulator.** Ferrite biased by a magnet; power
  walks 1→2→3→1. Matched, lossless (ideally), and S ≠ Sᵀ. It is how one
  antenna serves both a transmitter and a receiver — the radar front-ends of
  lecture 12 own one. Not a splitter, but the third corner of the menu, and
  proof the theorem's assumptions are each load-bearing.
- **Give up match: the lossless tee.** Solder three 50 Ω lines together: the
  junction sees 25 Ω, |Γ| = ⅓, and nothing isolates anything. This is the
  "just solder it" answer priced honestly.

Then say the quiet part: **none of these feeds an array.** The star leaks
between outputs, the tee reflects, the circulator does not split. What we
actually want is a *fourth option* the theorem seems to forbid: matched
everywhere, reciprocal, outputs isolated, and lossless *along the paths we
use*. That exact fine print — "along the paths we use" — is the Wilkinson.

### 1.4 The Wilkinson, dissolved by even/odd analysis (0:28–0:45)

Slide cue: the Wilkinson schematic — input tee, two λ/4 arms of √2·Z₀ =
70.7 Ω, a single 100 Ω resistor bridging the outputs.

First, the circuit, as Ernest Wilkinson published it in 1960: split the input
into two quarter-wave lines of impedance √2 Z₀, then hang one resistor of
2Z₀ = 100 Ω *between* the two outputs. No resistor to ground. The whole
miracle is the placement.

Now **the technique of the week**, developed carefully because lecture 9
builds coupled-line filters on it. The circuit is symmetric about a horizontal
mirror line. Any excitation of the two output ports decomposes into an
**even** part (both driven +V, +V) and an **odd** part (+V, −V) — that is just
vector arithmetic: (a₂, a₃) = ½(a₂+a₃)(1,1) + ½(a₂−a₃)(1,−1). The payoff:

> **Even excitation:** no current crosses the mirror — cut it and leave an
> *open* (a magnetic wall). Every crossing element splits: the resistor
> becomes two dangling R/2 stubs (carrying no current!), the input port
> becomes two ports of 2Z₀ in series-parallel bookkeeping.
> **Odd excitation:** the mirror is at zero volts — cut it and *ground* it
> (an electric wall). The input junction becomes a short; the resistor's
> midpoint grounds, leaving R/2 to ground at each output.

Solve two *half-sized* one-port problems, then superpose: S₂₂ = ½(Γₑ + Γₒ),
S₂₃ = ½(Γₑ − Γₒ). That sum-and-difference line is the whole method. Memorize
the walls — even = open, odd = short — and you can take apart any symmetric
network in the catalog.

**Even mode, worked** (numbers on the board). From output 2, the even half is
a quarter-wave line of 70.7 Ω terminated in 2Z₀ = 100 Ω (the input port,
shared between the two halves). Lecture 2's inverter: Z_in = 70.7²/100 =
50 Ω. **Matched.** Γₑ = 0. The R/2 stub dangles — both of its ends ride at the
same potential, so the resistor is *invisible to the even mode*. File that
sentence; it is the answer to hour 3's sabotage.

**Odd mode, worked.** The shorted quarter-wave arm transforms to an open at
the output — gone. All that remains is R/2 to ground. Match demands R/2 = Z₀:

> **R = 2Z₀ = 100 Ω.** The resistor value is not a tweak; it is the odd-mode
> match, full stop.

Γₒ = 0 too, so S₂₂ = 0 and — the punchline — S₂₃ = ½(Γₑ − Γₒ) = 0:
**isolated outputs.** And from the input: two parallel branches, each a
quarter-wave 70.7 Ω into 50 Ω → 100 Ω each, in parallel 50 Ω. S₁₁ = 0.
Transmission: a quarter-wave line hands over everything with a 90° tag,
S₂₁ = S₃₁ = −j/√2 — a 3.01 dB split at −90°. Hour 3 prints this matrix to six
decimals.

Keep the general formulas — the homework's module 1 *is* this board work for
arbitrary arm impedance Z₂ and resistor R (at f₀, tangents already sent to
infinity by hand):

> Γₑ = (Z₂² − 2Z₀²)/(Z₂² + 2Z₀²) Γₒ = (R − 2Z₀)/(R + 2Z₀)
> S₁₁ = Γₑ S₂₁ = −2j·Z₀Z₂/(Z₂² + 2Z₀²) S₂₂ = ½(Γₑ+Γₒ) S₂₃ = ½(Γₑ−Γₒ)

Now confront the theorem, because the Wilkinson looks like it violates it:
matched at all three ports, reciprocal, isolated. The theorem says it must be
lossy — and it is, *selectively*. Drive port 1 with matched loads everywhere:
pure even mode, no resistor current, **zero dissipation** — the split is
lossless in the direction you care about. Drive an *output* port: half the
power crosses to port 1, the other half — the odd-mode half — dies in the
resistor. ‖SᴴS − I‖ = 1.000000 exactly at f₀; hour 3 prints it. The Wilkinson
does not cheat the theorem; it *aims the mandatory loss at the excitations you
never use* — imbalance and reflections. The resistor is not in the signal
path; it is a bouncer standing where only trouble walks.

Pre-empt the misconception before someone budgets wrong: *"so the resistor
burns 3 dB of my transmit power?"* No. Balanced, matched operation dissipates
**nothing** in it. It is insurance — priced only when things go wrong. And
that is exactly when it matters —

War story, 90 seconds. A two-way combined solid-state transmitter: two 100 W
amplifiers into a Wilkinson-style combiner. Design review, a cost engineer
spots the isolation resistor: "rated 2 W? It measures zero watts in every
test. Delete it?" It stayed, rated 2 W, because "it never dissipates
anything." Commissioning week, one PA's supply breaker trips. The survivor
keeps driving — now *hopelessly imbalanced*, half its 100 W is odd mode, and
**50 watts** arrives at a 2 W resistor. It opens, the combiner degenerates
into an unisolated tee, the mismatch pulls the surviving PA's load line, and
the station is dark for a week over a part that "never dissipates anything."
Rate the bouncer for the fight, not for the quiet nights. (Homework Q1 prices
the quieter version of imbalance: 0.1 dB errors climbing a corporate tree.)

### 1.5 Hour recap (0:45–0:50)

Three sentences, then break. A matched, reciprocal, lossless three-port is a
theorem-level impossibility — pick two, and know which two your vendor picked.
Even/odd analysis is mirror-plus-superposition: even sees an open, odd sees a
short, S-entries are half-sums and half-differences. The Wilkinson picks
match + reciprocity, hides the mandatory loss in a resistor only the odd mode
can see — R = 2Z₀ *is* the odd-mode match — and hands you −j/√2 to each
output. Hour 2: buy a fourth port instead, and the theorem changes sides.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: four-ports — couplers, hybrids, and where they live (1:00–1:50)

### 2.1 The directional coupler, and C/D/I said honestly (1:00–1:12)

Slide cue: the four-port box — input, through, coupled, isolated — with the
three defining ratios.

First the theorem's sequel, stated because it flips the story: **a matched,
reciprocal, lossless four-port is possible** — the orthogonality conditions
that strangled the three-port now have enough room, and the solution they
force is precisely a *directional coupler*: every matched lossless reciprocal
four-port is one, with two isolated port pairs. What was forbidden with three
ports becomes *mandatory structure* with four. (The proof is Pozar §7.1; we
take the result and spend our minutes on the numbers engineers actually trade.)

Name the ports: 1 input, 2 through, 3 coupled, 4 isolated. Three dB-numbers
define the device, all referenced to the input:

> **Coupling C = −20·log|S₃₁|** — how much comes out the coupled port. The
> design value: 3 dB, 10 dB, 20 dB.
> **Isolation I = −20·log|S₄₁|** — how much leaks to the port that should
> hear nothing.
> **Directivity D = 20·log|S₃₁/S₄₁| = I − C** — how well the coupler tells
> *forward* from *backward*.

Box the identity: **I = C + D.** Isolation is a *product* of two causes — the
tap being weak (C) and the tap being direction-blind (D). Only D measures the
coupler's quality; C is just its size.

Pre-empt the classic confusion now, in its natural habitat: *"the datasheet
says 20 dB isolation, so it can measure a 20 dB return loss."* No — for a
10 dB coupler that isolation is only D = 10 dB of directivity, and directivity
is the number that caps a reflection measurement. Set up the reflectometer
picture: the coupled port is supposed to sample the *reflected* wave (via C);
the forward wave leaks into the same port suppressed only by I. The
wanted-to-leakage ratio at the coupled port is (RL suppressed by C) versus
(forward suppressed by C + D): the leakage equals the echo when **RL = D**.
Beyond that, the reading is fiction.

War story, 60 seconds: site acceptance, an antenna reflectometer built on a
12-dB-directivity coupler reads a magnificent 26 dB return loss. The antenna
later fails in rain; a proper bridge measures 14 dB. Nobody falsified
anything — at RL ≈ D the leakage and the echo are the same size, and their
phasor sum can read *anything*, including "magnificent." The instrument's
directivity is the ceiling of what it can ever certify. Hour 3 prints a C/D/I
table where you watch D collapse off-frequency while C barely moves —
the two numbers are different *kinds* of thing, and the table makes that
visceral.

Real numbers to carry: machined waveguide couplers ship D ≈ 30–40 dB;
stripline, ~20–30; ordinary edge-coupled **microstrip, 10–15 dB** — hold that
low number, §2.4 explains where it comes from and lecture 9 pays for it.

### 2.2 The branch-line hybrid — even/odd, second performance (1:12–1:24)

Slide cue: the branch-line square — series arms Z₀/√2 top and bottom, shunt
arms Z₀ left and right, all λ/4.

The workhorse 3 dB coupler in planar circuits: a square ring of quarter-wave
lines — series arms of Z₀/√2 = 35.4 Ω, shunt arms of Z₀ — ports at the four
corners: 1 in, 2 through, 3 coupled, 4 isolated.

Run **the same technique** — say it as a ritual now: symmetric circuit, so
bisect; even gets an open (each shunt λ/4 arm becomes a dangling λ/8 *open*
stub, admittance +jY₀ at f₀), odd gets a short (λ/8 *shorted* stub, −jY₀);
each half is stub–(λ/4 series line, 35.4 Ω)–stub, a two-port this time, so
carry Γ and T for each half and superpose:

> S₁₁ = ½(Γₑ+Γₒ) S₂₁ = ½(Tₑ+Tₒ) S₃₁ = ½(Tₑ−Tₒ) S₄₁ = ½(Γₑ−Γₒ)

Multiply the three ABCD factors per half (board, fast — students have done
six of these by lecture 7): both halves come out reflectionless, Γₑ = Γₒ = 0,
with Tₑ = −(1+j)/√2 and Tₒ = (1−j)/√2. Superpose:

> S₁₁ = 0 S₂₁ = −j/√2 S₃₁ = −1/√2 S₄₁ = 0

Equal 3 dB split, but the two outputs differ by **90°** — a *quadrature*
hybrid, the fingerprint of the whole 90° family. Feed it backwards from two
ports and that 90° decides what combines where — hour 3's monopulse cell
turns exactly that screw, and homework Q2 asks you to predict which way it
turns *before* the code answers.

The price of the loveliness: everything above leaned on "λ/4 *at f₀*." Walk
one octave away and every length is wrong. Hour 3 measures it: amplitude
balance within 0.5 dB holds over 9.10–10.90 GHz — **18% fractional
bandwidth** — and directivity is already down to 17.6 dB half a gigahertz out.
Hybrids are narrowband creatures; multisection versions (lecture 6's Chebyshev
instinct, applied to couplers) buy octaves the same way multisection
transformers did.

### 2.3 The 180° family — rat-race, and Σ/Δ born (1:24–1:32)

Slide cue: the rat-race ring — 1.5λ circumference, impedance √2·Z₀, four
ports at 0, λ/4, λ/2, 3λ/4.

Stretch one arm of the square to 3λ/4 and the hybrid changes species: the
**rat-race**, whose two outputs differ by 0° or 180° depending on the input
port. The S-matrix worth writing (Pozar's port order — 1 and 3 are the two
inputs of interest here):

> S = (−j/√2)·[[0, 1, 1, 0], [1, 0, 0, −1], [1, 0, 0, 1], [0, −1, 1, 0]]

Read the two magic rows. Drive ports 2 and 3 with signals a and b (two
antenna elements, say):

> port 1 emits (a + b)/√2 — the **sum port, Σ**
> port 4 emits (b − a)/√2 — the **difference port, Δ**

Two equal in-phase inputs: Σ takes everything, Δ takes *exactly nothing* —
the difference of equals. That null is the most valuable zero in radar, and
§2.5 spends it. The waveguide twin — the magic tee — does the same job with
its E-arm and H-arm; same algebra, different plumbing.

Say the taxonomy plainly, because the homework hinges on it: **90° hybrids
(branch-line, coupled-line) and 180° hybrids (rat-race, magic tee) are
different tools.** Both split 3 dB; what differs is the phase the two paths
carry, and therefore *which input condition produces the null*. Hold that
thought seven minutes; it becomes a prediction question you answer in ink.

### 2.4 Coupled lines — the even/odd payoff (1:32–1:40)

Slide cue: two microstrip traces running side by side; the even and odd field
crosssections underneath.

Run two lines close together for a quarter wavelength and they whisper to
each other — that *is* a coupler, no junctions at all. The analysis is the
hour's third performance of the same ritual, with a twist that makes it the
bridge to lecture 9: the symmetric pair supports an **even mode** (both lines
+V — fields mostly between the pair and ground) and an **odd mode** (+V/−V —
fields crowding the gap), and because the field pictures differ, the two
modes see **different characteristic impedances**, Z₀ₑ > Z₀ₒ. That pair of
numbers is the entire design space.

Two formulas govern (backward coupler, quarter-wave at f₀; derivation is
Pozar §7.6, we take the two lines that matter):

> match at all ports ⇔ **Z₀ₑ·Z₀ₒ = Z₀²**
> mid-band coupling **C₀ = (Z₀ₑ − Z₀ₒ)/(Z₀ₑ + Z₀ₒ)** ⇒
> Z₀ₑ = Z₀·√((1+C₀)/(1−C₀)), Z₀ₒ = Z₀·√((1−C₀)/(1+C₀))

Numbers on the board. A 20 dB coupler: C₀ = 0.1 → Z₀ₑ = 55.3 Ω, Z₀ₒ =
45.2 Ω — a gentle whisper, easy geometry. A 10 dB coupler: 69.4/36.0 Ω —
getting intimate. A 3 dB coupler: C₀ = 0.707 → **120.7/20.7 Ω** — an
edge-coupled microstrip gap of microns; unbuildable, which is why tight
couplers become Lange's interdigitated fingers or cascades of loose sections.
The formula prices the whisper.

And the honest footnote §2.1 promised: in microstrip the even and odd modes
travel at *different speeds* (the odd mode lives more in air), the two
quarter-waves cannot both be λ/4 at f₀, and the imperfect cancellation is
exactly the **10–15 dB directivity** of ordinary microstrip couplers.
Stripline, fully TEM, does not have the problem. Lecture 9 inherits both the
gift (Z₀ₑ/Z₀ₒ as design variables → coupled-line filters) and the bill
(velocity mismatch → the simulated-vs-fabricated gap).

### 2.5 Where they live — feeds, balanced amps, monopulse (1:40–1:48)

Slide cue: three application panels; the monopulse comparator gets the big one.

- **Corporate array feeds** — the homework. Three Wilkinsons in a tree feed
  four elements through equal path lengths; isolation contains each element's
  reflections; and errors accumulate with tree *depth* (log₂N), not element
  count — Q1 makes you predict exactly how before the instrument shows you.
- **Balanced amplifiers** — two copies of an amplifier between two quadrature
  hybrids. The 90°-out-and-90°-back trick sends each amplifier's *reflection*
  to the terminated port instead of the input: the pair is matched even though
  each half is not, and one hybrid's isolation resistor quietly eats the
  difference. Lecture 11 uses this to unglue the gain-match/noise-match knot.
- **The monopulse comparator** — the radar tie-in, and lecture 16's opening
  act. Four antenna quadrants, four 180° hybrids: form Σ = A+B+C+D,
  Δ_az = (A+B)−(C+D), Δ_el = (A+C)−(B+D). On boresight both Δ ports are
  *nulls*; a target drifting off axis un-cancels the subtraction, and the
  ratio Δ/Σ reads the angle error — sign and size — **from a single pulse**.
  That is how a fire-control radar tracks to a fraction of a beamwidth while
  lecture 13's beamwidth formula says it shouldn't be able to point that
  well: the null is sharper than the beam. One caution the homework turns
  into a prediction: the comparator wants the **180°** family; build it from
  90° hybrids and the null moves somewhere instructive. No spoiler — Q2 wants
  your prediction in ink first.

### 2.6 Hour recap (1:48–1:50)

Four-ports legalize what three-ports forbid, and the legal device is exactly
the directional coupler: C says how big the tap is, D says how honest it is,
I = C + D, and never let a datasheet blur the last two. The 90° family
(branch-line, coupled-line) and the 180° family (rat-race, magic tee) split
identically and null differently. Coupled lines put the week's technique in
its final form — even/odd *impedances* as design variables — and hand
lecture 9 its filters. Hour 3: we build the Wilkinson in nine lines of
scikit-rf, referee our own board work to sixteen decimals, and then sabotage
the resistor.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: skrf Circuit, the hand analysis refereed, and a sabotaged resistor (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:04)

Run cell 3.1: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib 3.10.x,
scikit-rf 1.13.0. Anyone whose `setup_check.py` failed pre-class pairs up now —
do not debug installs live.

### 3.2 skrf Circuit anatomy — a Wilkinson from lines and one resistor (2:04–2:14)

Cell 3.2, the week's new tool. Until today every network was a chain — lecture
4's `**` cascade was enough. A Wilkinson has a *junction*, and junctions need
`skrf.Circuit`: media make elements, `Circuit` wires them. Say the three facts
we verified against the installed wheel, because tutorials get them wrong:
every network needs a unique non-empty `.name`; a connection listing three
nodes *is* an ideal tee (that's our input junction — no separate tee network);
and external ports come out **in the order their `Port` objects first appear
in the connections list** — not alphabetically. Assemble: two `tem_line`s of
70.7 Ω cut for 90° at 10 GHz, one `media.resistor(100)`, three ports, three
connection rows. Print S(f₀): zeros on the diagonal, −j·0.707107 to each
output, −0.000000j between outputs. The board matrix from 1.4, to six
decimals, out of a library that never saw our algebra.

### 3.3 The hand analysis meets the model (2:14–2:20)

Cell 3.3: type the four closed-form lines from the board — Γₑ, Γₒ, S₂₁, the
superposition — as `wilkinson_s0_hand(z2, r)`, and compare against the
assembled circuit for three designs: the ideal (70.7 Ω, 100 Ω), thin arms
(60 Ω), and a doubled resistor (200 Ω). Max deviation: **~2e-16** on all
three. Pause on what just happened: the algebra and the numerical model agree
*for broken designs too* — the referee certifies that two independent
descriptions name the same circuit, healthy or not. (Cell 3.7 weaponizes that
distinction.) This is the homework's module 1, minus the fourth test case.

### 3.4 The Wilkinson swept — and the theorem's fingerprint (2:20–2:28)

Cell 3.4: sweep 5–15 GHz. Match and isolation both hold ≤ −20 dB over
**8.20–11.80 GHz — 36% fractional bandwidth** (the quarter-wave arms are the
narrowband culprits, same physics as lecture 2's transformer), and the split
sags only to −3.27 dB at the 5 GHz edge. Then the number the theorem
promised: `‖SᴴS − I‖` at f₀ = **1.000000**. Not 0.99, not "small" — exactly
one, the impossibility theorem showing up as a measured residual in a
matched, reciprocal, isolated three-port. Say where the deficit lives (rows 2
and 3 — output-side drive) and where it doesn't (column 1 — the balanced
split is lossless). Figure saved: `wilkinson_sweep.png`.

### 3.5 The branch-line — 90°, verified; C/D/I, tabulated (2:28–2:36)

Cell 3.5: assemble the square — 35.4 Ω series arms, 50 Ω shunts, four ports
in list order. At f₀: |S₂₁| = |S₃₁| = **−3.0103 dB**, phase difference
**90.0°** exactly — the quadrature fingerprint. Then the C/D/I table, read
like a datasheet: at 9.5 GHz C = 3.01, D = 17.56, I = 20.58; at 9.0, D =
11.85; at 8.0, D = 6.81, I = 10.17 — every row obeys **I = C + D**, and D is
the column that dies first as you leave f₀ (at f₀ itself the ideal model's D
hits the float floor; real microstrip ships 10–15 dB, as promised in 2.1).
Balance within 0.5 dB: 9.10–10.90 GHz, **18%** — half the Wilkinson's band;
hybrids pay for their phase magic in bandwidth.

### 3.6 The monopulse teaser (2:36–2:42)

Cell 3.6, the radar minute. Hang two "antenna elements" on ports 2 and 3 —
equal amplitudes, relative phase ψ standing in for angle of arrival — and
read port 1 as Σ, port 4 as Δ. At boresight, ψ = 0: **both ports read
−3.0103 dB.** Let the room react — half expected a null at boresight, because
§2.5's comparator had one. Sweep ψ: the Δ null sits at **ψ = 90°**, depth
−313 dB (the float floor), and at the null the two paths into Δ arrive at
amplitudes 0.5000 and 0.5000, **180.000000° apart** — a null is equal
amplitudes plus π, manufactured here by the hybrid's internal quarter-wave
asymmetry *plus* 90° of input phase. This is a **90°** hybrid; the rat-race
would put the null at ψ = 0. The homework's module 3 re-runs this experiment
with your code, and Q2 wants your prediction written down before you run it —
tonight's room reaction is exactly the reaction the question is built to
collect. Figure saved: `monopulse_psi.png`.

### 3.7 Deliberate bug — the resistor that doubled (2:42–2:46)

Cell 3.7, the sabotage. A well-meaning tech "upgrades" the isolation resistor
to 200 Ω — bigger handles more power, no? Rebuild, print the report card next
to the healthy one: input match **unchanged at the float floor** — S₁₁ is
pure even mode and the even mode cannot see the resistor at all; split
unchanged at −3.01 dB. But output match and isolation both collapse to
**−15.56 dB** = 20·log₁₀(1/6): Γₒ = (200−100)/(200+100) = ⅓, halved once by
the superposition into S₂₂ and once into S₂₃. The kicker, said slowly: *a
one-port sweep at the input — the lazy bench check — reads this part as
perfect.* The failure lives entirely in the odd-mode entries, and only a
report card that measures S₂₂ and S₂₃ catches it. That is why the homework's
`feed_facts` measures isolation explicitly, and why 1.4's bouncer metaphor
was load-bearing: check the bouncer, not just the front door.

### Homework brief (2:46–2:49)

`lab/HOMEWORK.md` on screen. The story: feed four antennas — a corporate tree
of three Wilkinsons, then a branch-line monopulse teaser.

- Module 1 is the core: the even/odd closed form at f₀ for *arbitrary*
  (Z_line, R) — the board work of 1.4, refereed by the assembled circuit to
  1e-6 (the reference lands at 2e-16). The checker feeds it broken designs;
  the formulas must carry the failure modes.
- Module 2 assembles the tree in `skrf.Circuit` — tonight's cell 3.2 is your
  template; port order and unique names are the traps, and both are surfaced
  in the hints. Balance bar: 0.01 dB; isolation bar: 30 dB.
- Module 3 is cell 3.6 with your hands on it: Σ, Δ, the null, and the 180°
  check.
- **Predictions first.** Q1 (imbalance vs tree depth — 0.1 dB per Wilkinson,
  how does it grow?) and Q2 (where the 90° hybrid's null sits) are answered
  *before* running — committing is the assignment.
- `--check` prints facts, not PASS/FAIL; lecture 4's invariant suite referees
  the tree, and the unitarity residuals — 1.0, √3, ~1e-15 — are Q3's essay
  material. Budget ≤ 3 hours; AI use assumed and welcome — the predictions
  and reconciliations must be yours.

### Wrap-up (2:49–2:50)

Recap against the three claims: the three-port theorem, proved and then
*measured* — 1.000000; even/odd run three times — Wilkinson, branch-line,
coupled lines — until it is a reflex aimed at lecture 9; C, D, I with
I = C + D, and a doubled resistor that a one-port check would have shipped.
Teaser: next lecture the receiver's front door — filters — where lecture 6's
g-values stop being abstract and start being inductors.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 4 (*Modules*), chs. 5–6
  (dividers, hybrids, coupled lines) — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 7 (for owners — this lecture
  parallels §7.1–7.6, and the impossibility proof is §7.1 verbatim).
- E. J. Wilkinson, "An N-Way Hybrid Power Divider," *IRE Trans. Microwave
  Theory Tech.*, 1960 — two pages; the original N-way version is more general
  than the two-way everyone builds.
- [R37] scikit-rf documentation, `skrf.circuit.Circuit` — free:
  https://scikit-rf.readthedocs.io/
