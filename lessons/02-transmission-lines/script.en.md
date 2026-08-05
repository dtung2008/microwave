# Lecture 2 — Transmission-Line Theory

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course env from lecture 1: numpy 1.26.4, scipy,
matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**; nothing new to install)
**Prerequisites:** lecture 1 (dB grammar, the λ/10 rule); circuits (phasors,
complex arithmetic); a nodding acquaintance with ∂/∂z.
**Pre-class setup:** course env installed; run `lab/setup_check.py` — it must
print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the cell, the waves, and the reflection (0:00–0:50)

### 1.1 The promise lecture 1 made (0:00–0:08)

Slide cue: last week's λ table with the 2.4 GHz row highlighted — the 3 cm trace
that crossed the λ/10 line.

Open by collecting last week's debt. Lecture 1 ended with a threat: past ~λ/10,
Kirchhoff stops being the truth and *this lecture* becomes the truth. Today we
pay it off. The homework's test article makes the stakes concrete: a 10 m run of
coax feeding a 2.4 GHz antenna. At 2.4 GHz in that cable, λ = 83 mm — the feed
is **120 wavelengths** long. Calling it "a wire" is off by four orders of
magnitude in the only unit that matters.

Three claims for today — board, leave them up:

1. **A transmission line is a ladder of infinitesimal circuits, and two numbers
   summarize the whole ladder.** From four per-meter quantities (R′, L′, G′, C′)
   fall a characteristic impedance Z₀ and a propagation constant γ = α + jβ.
   Everything else today is those two numbers doing consequences.
2. **The line enforces a ratio, and loads that refuse it cause reflections.**
   Z₀ is not a resistor — it is the V/I ratio a traveling wave *must* carry.
   A load with any other opinion sends part of the wave back: Γ, the reflection
   coefficient, the single most-measured quantity in this industry.
3. **A length of line transforms impedance — and that is a feature.** Z_in
   depends on ℓ through a tangent; at λ/4 a line *inverts* impedance, which is
   the first matching tool you will ever own. Today ends with a feed line lying
   about its antenna by 19 dB, and with the λ/4 fix — measured, |Γ| ≈ 10⁻¹⁶.

Pre-empt the digital designers in the room, who are already thinking *"we call
this signal integrity"*: yes. Same physics, different vocabulary — your
"ringing" and "reflections on the bus" are today's |Γ| with a clock attached,
and hour 3 builds your textbook's bounce diagram from our formulas. By the end
of today the two dialects should merge.

### 1.2 The RLGC cell and the telegrapher's equations — derived twice (0:08–0:20)

Slide cue: the ladder — series R′dz and L′dz, shunt G′dz and C′dz, repeated.

Why does a wire pair *become* this ladder? Physics first, then algebra. Any two
parallel conductors carry: magnetic flux around current → series inductance per
meter L′; charge storage between them → shunt capacitance per meter C′; finite
conductor conductivity → series resistance per meter R′; imperfect dielectric →
shunt leakage G′. At low frequency the whole cable is one lumped blob and
Kirchhoff survives. Past λ/10, voltage and current *differ from point to point
along the line*, so we must write the circuit laws on an infinitesimal slice dz
and let calculus glue the slices together.

**Level 1 — the limit process (the first-principles version).** KVL across one
slice: V(z+dz) − V(z) = −(R′ + jωL′)·dz·I(z). KCL on the shunt leg:
I(z+dz) − I(z) = −(G′ + jωC′)·dz·V(z+dz). Divide by dz, let dz → 0 (the
second-order term dies — say it, someone will ask):

> dV/dz = −(R′ + jωL′) I    dI/dz = −(G′ + jωC′) V

The **telegrapher's equations** — named for the 1850s engineers who found
undersea cables smearing Morse code and needed exactly this theory. Two coupled
first-order equations: voltage changes because series impedance eats it, current
changes because shunt admittance leaks it.

**Level 2 — the wave equation (the fast consequence).** Differentiate the first,
substitute the second:

> d²V/dz² = γ² V,  γ = √((R′ + jωL′)(G′ + jωC′)) = α + jβ

Solutions e^(∓γz): two waves, one running each way, each decaying by α
(nepers/m) and rotating phase by β (rad/m). Everything about propagation on any
uniform two-conductor line is inside γ. And the ratio V/I of each traveling
wave, from either telegrapher equation:

> Z₀ = √((R′ + jωL′)/(G′ + jωC′))

Common student question, pre-empt it: *"real cables aren't ladders of discrete
parts — is this a model or the truth?"* For any line supporting a TEM
(transverse electromagnetic) wave — coax, twin-lead, and to a good approximation
next lecture's microstrip — it is exact in the dz → 0 limit; the RLGC values are
computable from the cross-section geometry (lecture 5 does this for microstrip).
The ladder is not an approximation of the field theory; it is the field theory,
projected onto circuit language.

### 1.3 Z₀ and γ — the two numbers, with numbers (0:20–0:34)

Introduce the course's cable, because every formula today lands on it: an
RG-58-class coax described by its per-meter cell at 2.4 GHz — R′ = 10 Ω/m,
L′ = 250 nH/m, G′ = 0.45 mS/m, C′ = 100 pF/m. (R′ and G′ frozen at their
2.4 GHz values; a real cable's R′ grows as √f with skin effect — lecture 5's
fine print. Modeling choice, stated out loud.)

Lossless skeleton first, because the numbers are clean:

> Z₀ = √(L′/C′) = √(250 nH / 100 pF) = √2500 = **50 Ω** (that's where 50 lives!)
> v_p = 1/√(L′C′) = **2×10⁸ m/s = 0.667c**  β = ω/v_p  λ = v_p/f = **83.33 mm**

With loss, hour 3 prints the honest versions: Z₀ = 50.0001 − j0.0589 Ω (the
imaginary part is loss's fingerprint — tiny here), γ = 0.1112 + j75.40 per
meter. The low-loss approximation, worth deriving on the board because it says
*where dB/m comes from*:

> α ≈ R′/2Z₀ + G′Z₀/2 = 0.100 + 0.011 = 0.111 Np/m

Two loss mechanisms, weighted by Z₀ in opposite directions — conductor loss
divides by Z₀ (higher impedance means less current for the same power), a fact
that matters in ninety seconds. Convert nepers: 1 Np = 20/ln10 = 8.686 dB, so
**0.966 dB/m**, and the homework's 10 m feed eats **9.66 dB one way**. Lecture
1's dB grammar, now with a physical source.

**What Z₀ actually is** — say this carefully, it is the lecture's most
misunderstood object. Z₀ is the V/I ratio that one traveling wave carries.
It is not a resistance you can measure with an ohmmeter: at DC the ohmmeter
sees R′ℓ plus whatever terminates the far end, and 50 Ω appears nowhere. Z₀
dissipates nothing — it is a *ratio the line enforces*, the exchange rate
between the wave's voltage and its current. A 50 Ω resistor and a 50 Ω line
agree only on this: if you terminate the line in that resistor, the arriving
wave finds its ratio already satisfied and nothing reflects. That sentence is
section 1.4.

Pre-empt the "why 50 Ω?" question — it comes every year: for air-dielectric
coax, power handling peaks near 30 Ω and loss bottoms near 77 Ω; 50 is the
committee-shaped compromise (and 75 Ω survives in broadcast, where loss wins
because nobody transmits kilowatts down a TV drop cable). Nothing sacred —
just frozen history you now have to match.

And pre-empt the relativity worry: *"0.667c — are the electrons doing that?"*
No — electrons drift at mm/s; the *energy* travels in the fields between the
conductors, and 0.667c = 1/√ε_r for polyethylene's ε_r ≈ 2.25. The conductors
are rails; the payload is the field. (This is why next lecture's "move along
the line" operations are phase operations, not particle transport.)

### 1.4 Reflection — Γ, and the reflected-power picture (0:34–0:46)

The setup: a wave arrives at the end of the line and finds Z_L. The wave
carries V/I = Z₀; the load demands V/I = Z_L. Both must hold at the same
terminals — contradiction, unless Z_L = Z₀. Physics resolves it the only way
it can: a second, backward wave appears, with amplitude ratio Γ chosen so the
*totals* satisfy the load. Write the boundary condition — total V over total I
equals Z_L:

> (V⁺ + V⁻)/(V⁺/Z₀ − V⁻/Z₀) = Z_L  ⇒  **Γ = V⁻/V⁺ = (Z_L − Z₀)/(Z_L + Z₀)**

The minus sign in the current line is the one students trip on: the backward
wave's current flows backward, so it *subtracts*. Landmarks, on the board, each
with its one-word physics:

- short, Z_L = 0: Γ = −1 — everything back, voltage flipped (the short pins
  V = 0);
- open, Z_L → ∞: Γ = +1 — everything back, upright (the open pins I = 0);
- matched, Z_L = Z₀: Γ = 0 — the ratio is satisfied, nothing returns;
- pure reactance, Z_L = jX: |Γ| = 1 — stores energy, dissipates none, so all
  power must eventually come back. A capacitor is a mirror with a phase shift.

Now the course's patient, the number the next three lectures keep meeting: an
antenna measuring **Z_L = 36 − j21 Ω at 2.4 GHz**. Compute it out loud:

> Γ = (−14 − j21)/(86 − j21) = **0.285∠−110.0°**

Power: the reflected wave carries |Γ|² = 8.1% of incident power; the load keeps
1 − |Γ|² = **91.9%**. The three dialects of the same number, which must become
reflexes (hour 3 prints all four):

> |Γ| = 0.285 ⇔ **SWR** (standing wave ratio) = (1+|Γ|)/(1−|Γ|) = 1.80
> ⇔ **return loss** RL = −20 log₁₀|Γ| = 10.90 dB
> ⇔ **mismatch loss** = −10 log₁₀(1−|Γ|²) = 0.37 dB

Return loss is a *big-is-good* number (the reflection is far down); mismatch
loss is a *small-is-good* number (little is missing). Sign conventions kill:
a datasheet's "S11 = −10.9 dB" and "RL = 10.9 dB" are the same fact — say it
now, spare them the confusion in lecture 4.

Where does the reflected power *go*? Pre-empt it: back down the line toward the
generator. If the generator is matched (a 50 Ω source — this course's standing
assumption until stated otherwise), the source resistance absorbs it: heat.
If the generator is *not* matched, the wave reflects again — and again — and
that multiple-bounce story is hour 3's bounce diagram and, run to steady state,
*is exactly* where the standing-wave formulas come from. One physics, two views.

A note on the ledger before the break, because two gammas now live on your
page: **γ = α + jβ is the propagation constant; Γ is the reflection
coefficient.** Same Greek letter by miserable historical accident. The homework
code refuses the ambiguity by name: `gamma_per_m` for the first, `refl` for the
second. Adopt the same hygiene on paper — subscript yours if you must.

### 1.5 Hour recap (0:46–0:50)

Three sentences, then break: a line is the dz → 0 limit of an RLGC ladder, and
the telegrapher's equations compress it into γ and Z₀ — for our cable, 50 Ω,
0.667c, 0.97 dB/m; Z₀ is an enforced ratio, not a resistor, and a load that
disagrees reflects Γ = (Z_L−Z₀)/(Z_L+Z₀) — our antenna sends back 8.1%; the
four dialects (|Γ|, SWR, RL, mismatch loss) are one number wearing four suits.
Hour 2: what the two counter-running waves do to the line between them — and
the moment a piece of cable becomes a circuit element.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: standing waves, the transformer, and the lie (1:00–1:50)

### 2.1 Standing-wave anatomy — and the crank diagram (1:00–1:14)

Slide cue: the envelope plot — hour 3 animates this exact figure.

Two waves now share the line: V⁺e^(−jβz) forward, ΓV⁺e^(+jβz) backward
(lossless for clarity; loss returns in 2.3). Total voltage at distance ℓ
*from the load* (the RF convention — we measure from where the action is):

> V(ℓ) = V⁺e^(jβℓ)(1 + Γe^(−2jβℓ))

The magnitude of the parenthesis is the **standing-wave envelope**. Where the
two waves agree in phase: |V|max = |V⁺|(1+|Γ|). Where they oppose:
|V|min = |V⁺|(1−|Γ|). The wave *inside* the envelope travels; the envelope
itself stands still — hour 3 shows seven time-snapshots inside the frozen
envelope, and the name "standing wave" explains itself. The ratio of extremes
is the SWR of hour 1 — measured for our antenna: envelope max/min =
1.2851/0.7149 = **1.7976**, and SWR from |Γ| said 1.7976. Same number, two
routes — the referee principle without a library.

This is also why SWR survives as a word: the first RF instrument was a slotted
line — a probe sliding along a cut in the cable, reading |V(ℓ)|. You could not
measure Γ in 1940; you could measure the envelope's max, min, and minimum
positions, and that is |Γ| and its phase, re-dressed. (It also still matters
operationally: |V|max is what arcs your connectors, (1+|Γ|)× current is what
heats your final transistor — SWR is the *stress* dialect of Γ.)

**The crank diagram** — the picture that becomes the Smith chart next week.
Draw the complex number 1 + Γe^(−2jβℓ): a unit phasor plus a smaller one of
length |Γ| whose angle *decreases* as ℓ grows — a crank arm sweeping clockwise
around the tip of 1. The envelope is the crank's total length: maximum when the
arm points along +1, minimum when it points against. Full crank revolution =
2βℓ advancing by 2π = **ℓ advancing by λ/2**: the entire standing-wave pattern
repeats every half wavelength. Two consequences, said now, harvested next week:
(1) everything a lossless line can do to an impedance is a *rotation* of Γ;
(2) the pattern's period is λ/2, not λ — the factor of 2 that trips everyone
exactly once.

Where are the minima? The crank opposes 1 when angle(Γ) − 2βℓ = ±π. For our
antenna (angle −109.97°): first minimum at ℓ/λ = (180 − 109.97)/720 =
**0.0973** — hour 3's sampled envelope reads 0.0976λ (8.13 mm; the fourth digit
is the plot's grid step, not physics). Hold that number; it is about to matter.

### 2.2 Z_in(ℓ) — the tangent transformation, and λ/4 celebrated (1:14–1:32)

The centerpiece. Stand at distance ℓ from the load and ask: what impedance does
the rest of the line-plus-load present? Total V over total I:

> Z_in = Z₀ (1 + Γe^(−2jβℓ))/(1 − Γe^(−2jβℓ))

Substitute Γ and grind (one line of algebra on the board — make them watch the
Z₀ cancellations):

> **Z_in = Z₀ (Z_L + jZ₀ tan βℓ)/(Z₀ + jZ_L tan βℓ)**

The tangent transformation. Read its personality before plugging in numbers:
tan has period π, so Z_in repeats when βℓ advances by π — every **λ/2**, the
crank's period, as it must be. And tan passes through 0 and ∞ each period, so
between any load and λ/2 farther back, Z_in visits an entire menagerie —
capacitive, inductive, resistive-small, resistive-large. *A length of cable is
an impedance transformer whether you asked for one or not.* Change a jumper's
length by 3 cm at 2.4 GHz and you have redesigned the input network.

The special cases, each a tool:

- **ℓ = λ/2: Z_in = Z_L.** The line repeats the load. A half-wave jumper is
  electrically invisible — *at the one frequency where it is a half wave*
  (the war story below turns this footnote into a career lesson).
- **ℓ = λ/4: tan → ∞, and Z_in = Z₀²/Z_L.** The quarter-wave **inverter**.
  Large becomes small, capacitive becomes inductive — and, the money case: a
  *real* R becomes another real. To match a real load R to a system Z₀, build
  the quarter wave from line of Z_T = √(Z₀R): then Z_in = Z_T²/R = Z₀,
  exactly. Two lines of algebra, one of the most-built structures in microwave
  engineering.
- **Shorted stub: Z_in = jZ₀ tan βℓ** — any reactance you want, from a piece
  of shorted line. Open stub: −jZ₀ cot βℓ. These become lecture 3's matching
  components; today just notice the catalog exists.

Numbers for the λ/4 story, because the homework builds exactly this: our
antenna is complex, and a λ/4 transformer only matches *real* impedances —
√(Z₀·Z_L) with complex Z_L is a complex Z_T, which no cable has. The fix:
*walk back to a purely-real plane first.* Where is Z_in purely real? Exactly
where the crank crosses the real axis — the envelope's minima and maxima, twice
per half wavelength, alternating:

> at a voltage minimum: Z_in = Z₀/SWR (for us: 50/1.7976 = **27.8 Ω**)
> at a voltage maximum: Z_in = Z₀·SWR (for us: **89.9 Ω**)

So: spacer of plain 50 Ω line to the first minimum — 0.0973λ = **8.11 mm** —
then a quarter wave (20.83 mm) of Z_T = √(50 × 27.8) = **37.29 Ω**. At f₀ the
match is *exact by construction*: the homework's checker prints |Γ(f₀)| ≈
7×10⁻¹⁷ — machine epsilon, because the algebra is exact and the referee merely
confirms arithmetic. (Homework hint, free of charge: design the spacer with the
*ideal* line's β, not the lossy cable's γ — they differ in the sixth digit and
a 10⁻¹⁰ criterion notices sixth digits.)

Common question, pre-empt: *"why celebrate λ/4 if it only works at one
frequency?"* Because "one frequency" is a caricature — the homework measures
the honest version: the fix holds 10-dB return loss over **2.33 GHz of
bandwidth** (97% of f₀) and 20-dB over 577 MHz (24%). Narrowband is a number,
not a slur — and lecture 6 spends a whole hour making it wider.

### 2.3 Loss — and the feed line that lies (1:32–1:40)

Put α back. Every meter multiplies the wave amplitude by e^(−αℓ); power by
e^(−2αℓ). Our 10 m feed: 9.66 dB one way. Now the trap this homework is named
for. You stand at the transmitter end of 10 m of cable with a VNA (vector
network analyzer — lecture 4 tours one) and measure return loss, hoping to
learn about the antenna. The reflection you measure made *three trips through
attenuation*: down (−9.66 dB), bounce (−10.90 dB of it reflects), back
(−9.66 dB):

> RL_in ≈ RL_antenna + 2 × (line loss) = 10.90 + 19.33 ≈ 30.2 dB

Hour 3 measures **30.09 dB** (the 0.1 dB gap is the cable's slightly complex
Z₀ — the rule of thumb is a rule of thumb). Read the lie out loud: the antenna
is *mediocre* — SWR 1.8 — and the instrument says *excellent* — 30 dB! The
cable launders the reflection. Every dB of cable flatters the load by two dB,
and a long-enough lossy cable makes *any* load, even an open circuit, look
matched. The corollary every field engineer learns once: return loss must be
measured at the plane you care about, or corrected for the cable — and "the
antenna measures great from the shack" is the most expensive sentence in
amateur radio.

The power ledger closes the hour's physics (homework module 2 makes it exact):
of 1 W incident at the transmitter end, 99.3 mW reaches-and-stays in the
antenna, 0.95 mW makes it back out, and **899.7 mW heats the cable**. Delivered
sits 10.03 dB below incident = 9.66 (line) + 0.37 (mismatch) — the two taxes
add in dB because they multiply in watts. And the invariant that referees
module 2: switch the loss off, and |Γ|² + delivered = 1 to 1×10⁻¹⁶ — energy
conservation, the physics certifying your code, no library required.

### 2.4 Time domain — the bounce diagram (1:40–1:48)

Take away the sine wave; send a step. This is the digital engineers' home game
and the promised dialect merge. A 1 V step from a 25 Ω source into 10 m of
50 Ω line terminated in 150 Ω:

- t = 0: the step launches. The line *enforces its ratio* — the source sees
  50 Ω (it cannot know about the load yet — causality!), so the launch is the
  divider 50/(25+50) = **0.667 V**.
- 50 ns later (10 m at 2×10⁸ m/s) the edge hits the load: Γ_L = +1/2. The load
  voltage jumps to 0.667×(1+½) = **1.00 V**.
- The reflected 0.333 V runs back; at the source, Γ_s = (25−50)/75 = −1/3;
  re-reflects; each round trip multiplies by Γ_LΓ_s = −1/6.
- The load staircase: 1.000 → 0.833 → 0.861 → 0.857 → … converging on the DC
  divider 150/175 = **0.857 V**, geometrically, ratio −1/6.

The first edge *overshoots the final value by 16.7%*. On a scope this is called
ringing and blamed on ghosts; its true name is |Γ|, and its period is the round
trip 2ℓ/v_p. Two morals: (1) "electrically long" has a time-domain meaning —
the line is long when the edge's rise time is shorter than the round trip, the
digital twin of λ/10; (2) run the staircase to t → ∞ and you recover exactly
the phasor answers of 2.1 — the frequency domain is the time domain's
steady-state ledger, not a different universe.

War story, 90 seconds — the half-wavelength jumper. A dual-band installation:
the low band at f₀, a second band at 1.5f₀. A tech replaces a damaged 50 Ω
jumper with a 75 Ω video-grade cable of the same length — which happens to be
exactly λ/2 at f₀. Bench check at f₀: nothing changes. Of course not — a
half-wave line repeats its load *regardless of its own Z₀*; the jumper's 75 Ω
is invisible at exactly that frequency, so the check certified nothing. At the
other band, 1.5f₀, the same jumper is **3λ/4 — an odd quarter wave** — a full
inverter through 75 Ω: the 50 Ω system becomes 75²/50 = 112.5 Ω, SWR 2.25,
return loss 8.3 dB, and the high band's margin quietly evaporated. Nobody
mismeasured; the measurement was simply taken at the one frequency where the
tangent hides. Moral, and it is also hour 3's deliberate bug: **the tangent is
periodic — a line's behavior at one frequency certifies that frequency only.**

### 2.5 Hour recap (1:48–1:50)

Standing waves are two counter-running waves interfering — the envelope's
max/min ratio is SWR, the crank diagram is next week's Smith chart in embryo,
and the pattern repeats every λ/2; Z_in is the tangent transformation — λ/2
repeats, λ/4 inverts, and spacer-plus-λ/4 matches our antenna exactly at f₀;
loss makes feed lines lie by twice their attenuation, and the power ledger
(99.3 mW delivered of 1 W — the cable ate 900) is checkable physics; a step on
a line bounces geometrically, and ringing is |Γ| speaking the time domain.
Hour 3 builds all of it in twelve lines of NumPy, referees it with scikit-rf,
and then designs a transformer that is wrong in a way the bench would love.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the line engine, the referee, and one seductive bug (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:05)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, scikit-rf 1.13.0 — the lecture-1 environment; nothing new. Anyone whose
`setup_check.py` failed pre-class pairs up now — we do not debug installs live.
(This lecture's `setup_check.py` smoke-tests the two skrf media we referee
with — `DistributedCircuit` and `DefinedGammaZ0` — so a green check already
proves today's referee works.)

### 3.2 The line engine — the whole lecture in twelve lines (2:05–2:14)

Cell 3.2: `propagation()` is four lines — form R′+jωL′ and G′+jωC′, take the
two square roots; `z_in()` is three more — the *tanh* form, because loss is a
first-class citizen (and because `np.tan` explodes at the λ/4 pole while
`np.tanh` shrugs — the homework README's first troubleshooting entry). Run it
on the cable and read hour 1 off the screen: Z₀ = 50.0001 − j0.0589 Ω — *the
ratio the line enforces, plus loss's tiny imaginary fingerprint*; α = 0.9663
dB/m; v_p = 2×10⁸ = 0.667c; λ = 83.33 mm; **the 10 m feed is 120 wavelengths**.
Then the antenna: |Γ| = 0.2851 at −110.0°, SWR 1.798, RL 10.90 dB, mismatch
loss 0.368 dB — the antenna keeps 92% of what *reaches* it. Every number from
the board, now output.

### 3.3 The referee — skrf solves the same cell (2:14–2:22)

Cell 3.3, the course's referee principle in its lecture-2 costume. scikit-rf's
`DistributedCircuit` takes the same four RLGC numbers and computes γ and Z₀ by
its own code path: agreement to **0.0** — identically, both implement the
closed form. More interesting: Z_in of the 10 m feed two independent ways —
our tanh engine vs skrf's γ/Z₀ pushed through the *reflection-rotation*
identity (Γ_L propagated by e^(−2γℓ), no tanh anywhere): max relative error
**5.4×10⁻¹⁶** across the 2.0–2.8 GHz band. Two derivations, one answer,
machine precision — when the homework's checker prints this line about *your*
engine, the criterion is 10⁻⁶ and a correct engine beats it by ten orders.

Close the cell with the homework's headline, previewed in one line: return loss
at the antenna 10.90 dB; measured through 10 m of cable, **30.09 dB**. Point at
it: *that number is a lie, and homework module 2 dissects it.*

### 3.4 Standing waves, animated (2:22–2:30)

Cell 3.4: freeze the envelope |1 + Γe^(−2jβℓ)|, then draw seven time-snapshots
of the actual voltage inside it. The wave moves; the envelope does not — that
is "standing." Measured: max/min = 1.2851/0.7149, ratio **1.7976** — and the
SWR formula from |Γ| said 1.7976. Two routes, same number, zero libraries.
First minimum at **0.0976λ from the load** (8.13 mm) — the purely-real plane
where hour 2 parked the λ/4 transformer, and where homework Q1 asks you to
*predict* before you compute. `standing_wave.png` saved for the homework's
side-by-side.

### 3.5 The bounce diagram (2:30–2:38)

Cell 3.5: hour 2's step, coded as an eight-line while-loop. Watch the printout
match the board: 50 ns one-way, 0.6667 V launch, Γ_s = −1/3, Γ_L = +1/2; load
staircase 1.0000 → 0.8333 → 0.8611 → 0.8565 → … → 0.8571 V, the DC divider;
**+16.7% overshoot** on the first edge. Say it while the plot renders: on a
scope this is called ringing; its true name is |Γ|. `bounce.png` saved. Digital
students: this *is* your signal-integrity textbook's lattice diagram, and you
just wrote it from telegrapher first-principles in eight lines.

### 3.6 Deliberate bug — the 3λ/4 transformer that "also works" (2:38–2:44)

Cell 3.6, today's planted betrayal. The tangent has period π — so if λ/4
inverts, 3λ/4 inverts too. Design both, lossless: spacer 8.106 mm to the
27.815 Ω plane, Z_T = 37.293 Ω, and the referee prints |Γ(f₀)| = 7×10⁻¹⁷ for
λ/4 and 3×10⁻¹⁷ for 3λ/4. *Both perfect.* The junior engineer's conclusion:
"3λ/4 is the same device, and mine is easier to fabricate." Now hand the
transformer the cable's own α and re-measure: λ/4 gives RL 55.8 dB, 3λ/4 gives
51.97 dB — still fine, loss barely dents the null. So it *does* also work?
Sweep it. The 20-dB-RL bandwidth: **λ/4: 576.8 MHz. 3λ/4: 275.6 MHz.** Same
performance at f₀, *half* the bandwidth, three times the copper, three times
the loss. The tangent's period is not a free lunch: every extra half-wave of
line adds stored energy, and stored energy steepens the frequency response —
the same physics that made the war story's jumper a trap. (Lecture 3 gives
this "stored energy ⇒ narrowband" instinct a chart to live on; lecture 6 makes
it a theorem.)

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. The story: a 10 m feed to a mismatched antenna —
first the truth (module 1), then the money (module 2), then the fix (module 3).

- Module 1 is the core: the line engine — `propagation`, `reflection`, `swr`,
  `z_in` — *your* twelve lines, refereed by skrf's `DistributedCircuit` to
  10⁻⁶ (a correct engine lands near 10⁻¹⁶). Module 2 is the power ledger —
  where every milliwatt of 1 W goes, with the lossless energy-conservation
  invariant as its referee. Module 3 is the λ/4 fix: spacer to the real plane,
  transformer sized, |Γ(f₀)| < 10⁻¹⁰ *by construction*, then the honest
  bandwidth measurement.
- **Predictions come first.** Q1 (where is Z_in purely real, how often per
  wavelength) and Q2 (which way the cable lies, and by how much) are answered
  *before* running — committing to a number is the assignment.
- `--check` prints facts, not PASS/FAIL — referee deltas, the energy residual,
  the band edges. `--sweep` draws the two pictures Q2 and Q3 are about.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: the RLGC cell gave up its two numbers — 50 Ω
and 0.111 + j75.4, printed; the enforced ratio explained Γ — and our antenna's
8.1% came home through a cable that lied about it by 19 dB; and a length of
line became a component — the λ/4 inverter matched the antenna to machine
epsilon, while its 3λ/4 twin quietly cost half the bandwidth. Teaser: the fix
we built today needed a spacer, a special-impedance line, and luck that the
plane came out real. Next lecture, the Smith chart turns all of this rotation
into geometry you can *see* — and this same antenna, 36 − j21 Ω, gets matched
properly: two ways, with nothing but standard 50 Ω parts.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 2 (*Transmission Lines*),
  chs. 2–3 — free: https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 2 (for owners of the book — the
  transmission-line chapter this lecture parallels).
- [R4] Orfanidis, *Electromagnetic Waves and Antennas*, chs. 10–11
  (transmission lines; impedance matching preview) — free:
  https://www.ece.rutgers.edu/~orfanidi/ewa/
- [R37] scikit-rf documentation (media: `DistributedCircuit`,
  `DefinedGammaZ0`) — https://scikit-rf.readthedocs.io/
