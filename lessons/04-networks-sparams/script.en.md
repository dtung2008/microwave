# Lecture 4 — Microwave Network Theory: S-Parameters

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course venv from lecture 1: numpy 1.26.4, scipy,
matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1–3 (dB fluency; Γ, SWR, Z_in(ℓ) from lecture 2; the
Smith chart as the map of Γ from lecture 3); linear algebra at the "transpose,
inverse, eigenvalue" level.
**Pre-class setup:** the lecture-1 environment unchanged; run `lab/setup_check.py` —
it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: when voltage dies, waves take over (0:00–0:50)

### 1.1 Why this lecture is the hinge of the course (0:00–0:08)

Slide cue: the course map from lecture 1 with the L4 box lit up, and every following
box re-labeled "…described by S-parameters."

Open with the claim: this is the week the course changes languages, permanently. From
lecture 5 onward, every object we design — microstrip line, Wilkinson divider,
filter, transistor, antenna port — will be *represented* the same way: a matrix of
scattering parameters at each frequency. Datasheets are S-parameters. Simulator
output is S-parameters. The `.s2p` files you will download from Mini-Circuits in
lecture 11 are S-parameters. Learn to read, convert, cascade, and — above all —
*distrust* them this week, and the rest of the course is downhill.

Three claims for today — write them on the board and leave them up:

1. **At microwave frequencies, voltage and current stop being good coordinates.**
   Not wrong — *ambiguous*. The traveling-wave amplitudes of lecture 2 are what a
   real instrument measures, and the S-matrix is their transfer function.
2. **Representations are interchangeable; algebra is not.** S, Z, ABCD describe the
   same hardware and convert freely — but each has one operation it makes trivial,
   and cascading with the wrong one produces confident nonsense. Today ends with a
   cascade computed two ways, one of them non-physical.
3. **Physics referees every S-matrix.** Reciprocity (S = Sᵀ), losslessness
   (SᴴS = I), passivity (no singular value above 1) are one-number tests any honest
   file must pass. This week you build them; lectures 7 and 11 reuse them verbatim.
   The homework aims them at three files, at least one of which is lying.

Pre-empt the circuits students' question: *"we had two-port Z and h parameters in
circuits class — why a new formalism?"* Honest answer: nothing is wrong with Z — on
paper. The problem is operational: to *measure* Z₁₁ you must open-circuit port 2,
and at 10 GHz there is no such thing as an open circuit — a bare connector is a
capacitor and an antenna, and many transistors oscillate the moment they see one.
S-parameters are the two-port language rebuilt around the one thing we can actually
do well at microwave: terminate everything in 50 Ω and measure waves. Same network,
measurable coordinates.

### 1.2 Why voltage loses its meaning (0:08–0:18)

Board work. Recall lecture 2's terminated line: V(z) = V⁺(e^{−jβz} + Γe^{+jβz}).
Now ask the innocent question: *what is "the" voltage at the input of this
component?* Walk one wavelength of the standing wave: |V| swings between
|V⁺|(1+|Γ|) and |V⁺|(1−|Γ|) — at SWR 3, a 3:1 disagreement depending on where you
put the probe. On a PCB at 10 GHz, "where you put the probe" moves the answer every
few millimeters. Voltage still exists; it has just stopped being a *property of the
port* and become a property of the position.

Second blow, the operational one: the classical matrices are defined by boundary
conditions you cannot build. Z-parameters need open circuits (I = 0), Y-parameters
need shorts (V = 0). At microwave, an "open" radiates and looks capacitive; a
"short" is a via with inductance; and an active device asked to drive an open at
its resonant frequency will answer with an oscillation. War story, 60 seconds: a
student bench, a 6 GHz transistor "characterized" with a dangling SMA for the open
standard — beautiful smooth curves, none of them of the transistor; the dangling
connector was a quarter-wave stub that turned the intended open into a near-short,
and the device under test spent the whole sweep two ohms away from oscillating.

What *is* well-defined on a line, everywhere, uniquely? The two traveling waves.
Lecture 2 already split V and I into V⁺ and V⁻; the ratio V⁻/V⁺ was Γ and the whole
of lecture 3 lived on it. Today we normalize them properly and let them be the
coordinates.

### 1.3 Wave amplitudes a and b — derived twice (0:18–0:30)

**Level 1 — the fast version (definitions).** At a port with reference impedance
Z₀ (real, 50 Ω all course):

> a = (V + Z₀I) / (2√Z₀)  b = (V − Z₀I) / (2√Z₀)

a is the incident (inward) wave amplitude, b the outgoing. Invert: V = √Z₀(a + b),
I = (a − b)/√Z₀. On a matched line, b = 0 and V/I = Z₀ — the wave picture and the
circuit picture agree exactly where they should.

**Level 2 — first principles (why the √Z₀).** We *want* variables whose squared
magnitude is power, so that scattering coefficients compare energies, not volts.
Compute P into the port with RMS phasors: P = Re(V I*) = |a|² − |b|². There it is:
|a|² is the incident power in watts, |b|² the outgoing power, and their difference
is what the network keeps. The √Z₀ in the denominator is not decoration — it is the
exact factor that converts a voltage bookkeeping into an energy bookkeeping. (With
peak-amplitude phasors both terms carry a ½; the convention washes out of every
ratio. Pozar ch. 4 [R1] keeps the fine print.)

Connect backwards, out loud: at a one-port, b/a = (Z_L − Z₀)/(Z_L + Z₀) = Γ — the
reflection coefficient of lecture 2, rediscovered as a scattering parameter. The
Smith chart you learned last week is the complex plane of b/a. Nothing is new; it
has only been promoted.

Pre-empt the sign-convention question: *"incident into which end?"* Every port gets
its own a pointing INTO the network and b pointing OUT. A two-port therefore has
four numbers per frequency, and the matrix is next.

### 1.4 The S-matrix — what a VNA measures (0:30–0:40)

Definition, boxed:

> b₁ = S₁₁a₁ + S₁₂a₂  b₂ = S₂₁a₁ + S₂₂a₂  i.e. **b = S a**
> S₁₁ = b₁/a₁ with a₂ = 0 — and a₂ = 0 means **port 2 terminated in Z₀**,
> not open. Setting a wave to zero is done with a matched load.

Say the misconception before a student can own it: S₁₁ is *not* "the input
reflection of the device" in general — it is the input reflection **when port 2 is
matched**. Terminate port 2 in anything else and the input reflection moves to
Γ_in = S₁₁ + S₁₂S₂₁Γ_L/(1 − S₂₂Γ_L) — hour 2 derives it. Reading S₁₁ as "the"
match is the most common datasheet misreading in the field.

The interpretation table, spoken with feeling: S₁₁ — match at port 1 (lecture 3's
whole subject, now one matrix entry). S₂₁ — transmission, the gain or loss of the
thing. S₁₂ — reverse transmission: isolation when small, feedback when it matters
(lecture 11 shows S₁₂ is where amplifier instability lives). S₂₂ — output match.

The VNA (vector network analyzer), one slide, demystified: a swept source, and at
each port a **directional coupler** — a component (lecture 7 builds it) that
physically separates the wave going in from the wave coming out; ratio the two
phasors and you have measured S₁₁ directly, no opens, no shorts, everything
terminated in 50 Ω the whole time. Calibration (one sentence, honesty): the VNA
measures at *its* connectors; standards (short/open/load/thru) move the reference
plane to yours — hour 2 returns to reference planes, because they are the one thing
the invariants cannot check for you.

### 1.5 Three two-ports you now own forever (0:40–0:48)

Worked on the board, numbers the class will watch print in hour 3:

- **The matched ×½ attenuator (6.02 dB pad):** S₁₁ = S₂₂ = 0, S₁₂ = S₂₁ = ½.
  Power in 1, power out ¼, power reflected 0 — so |S₁₁|² + |S₂₁|² = 0.25 and the
  missing ¾ is *dissipated*. Keep this number; it calibrates the unitarity residual
  in twenty minutes.
- **A 75 Ω quarter-wave line in a 50 Ω world:** lossless, yet at f₀ it prints
  |S₁₁| = 0.3846, |S₂₁| = 0.9231 = −0.695 dB. Check: 0.3846² + 0.9231² = 1.0000.
  Nothing was dissipated — the missing power went *backwards*. Mismatch loss is not
  dissipation, and |S₂₁| < 1 does not mean heat.
- **The ideal 1:2 transformer:** ABCD = [[½, 0], [0, 2]] gives S₁₁ = −0.6,
  S₂₁ = +0.8 in 50 Ω. Again 0.36 + 0.64 = 1. And note what did *not* happen: the
  transformer doubles voltage, yet S₂₁ = 0.8 < 1 — because S compares powers, and
  a passive device has no power to add. Hold that thought; it is the homework's Q1
  and people get it wrong in industry weekly.

### 1.6 Hour recap (0:48–0:50)

Three sentences, then break: voltage on a line is a function of position, so ports
speak in waves — a in, b out, |·|² in watts. The S-matrix is b = S a with every
"zero" enforced by a matched load, which is why a VNA can actually measure it. A
lossless network can still have |S₂₁| well below 1 — reflection is not dissipation —
and whether |S₂₁| can ever exceed 1 is a question you will answer for keeps tonight.
Hour 2: the other matrices, the cascade algebra, and the three invariants that
referee every file.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: the matrix zoo, the cascade, and the invariants (1:00–1:50)

### 2.1 Z, Y, ABCD — where each representation shines (1:00–1:12)

The same two-port, four languages. Board table, kept terse:

- **Z (impedance):** V = Z I. Shines when networks stack in **series** (Z's add).
  Open-circuit definitions — hard to measure, easy to derive with.
- **Y (admittance):** I = Y V. Shines for **shunt** connections (Y's add). Duals of
  Z everywhere.
- **ABCD (chain):** (V₁, I₁) = [A B; C D](V₂, I₂) with I₂ defined *out of* port 2
  precisely so that chains link. Shines for **cascades**: the ABCD of a chain is
  the ordered matrix product. Lecture 2's line slots in as
  [cos βℓ, jZ_c sin βℓ; j sin βℓ/Z_c, cos βℓ]; a series impedance is [1, Z; 0, 1];
  a shunt admittance is [1, 0; Y, 1]. Three stamps, and you can build every ladder
  network in this course — the homework's planted filters are exactly such stacks.
- **S (scattering):** b = S a. Shines for **measurement** and for meaning at
  microwave; the only one an instrument gives you directly.

Conversions, stated not ground through (the slide has both; the homework has you
implement them and scikit-rf referees to 1e-10 — measured this week at 1.6e-12):

> Z = Z₀(I − S)⁻¹(I + S), S = (Z − Z₀I)(Z + Z₀I)⁻¹ — matrix forms, any N ports.
> S ↔ ABCD: the 2-port formulas with the 2S₂₁ denominators — on the slide, in the
> starter's docstrings, and in Pozar Table 4.2 [R1]; transcribing them correctly
> *once* is exactly the kind of work you delegate to an AI and then verify against
> the referee.

Pre-empt: *"why does ABCD get to multiply when S does not?"* Because ABCD's output
variables (V₂, I₂) are the next stage's input variables — the representation was
*designed* so the connection equation is the identity. S's variables are waves
sorted by direction, not by stage — which is the next section.

### 2.2 Cascading — the algebra that looks right and isn't (1:12–1:22)

Draw two boxes in a chain, waves labeled. Stage 1's outgoing wave at its port 2 —
b₂ — *is* stage 2's incident wave a₁'. Fine. But stage 1's S-matrix wants to know
its own a₂, which is stage 2's b₁' — the two networks feed each other in **both
directions**, and the composite response is the sum of an infinite bounce series
between them (lecture 2's bounce diagram, matrix-flavored). Multiplying S₁ by S₂
answers a different, unphysical question: it wires b of one to b of the other —
outputs to outputs.

Two correct routes, said plainly:

1. **Through ABCD** (or the T/wave-cascading matrix): convert, multiply in chain
   order, convert back. This is the homework's `cascade`, and skrf's `**` operator
   is its referee — agreement measured at 1.0e-15 across six mismatched sections.
2. **Through the bounce series summed:** for two stages,
   S₂₁,tot = S₂₁'S₂₁/(1 − S₂₂S₁₁') — the 1/(1−x) is the geometric series of
   inter-stage reflections. Same answer, and it *shows* why matched interfaces make
   cascades simple: S₂₂S₁₁' → 0 kills the bounces.

Numbers now, so hour 3's demo lands twice: naive S@S on two ×½ pads predicts
S₂₁ = 0 — two attenuators in a row "transmit nothing" because the product wired the
ports backwards. And on an L-section + line pair the naive product prints a
plausible-looking −7.44 dB where the truth is −0.35 dB — *plausible* is the
operative word; the third invariant of this hour is what catches it.

### 2.3 The invariants — reciprocity, losslessness, passivity (1:22–1:38)

The centerpiece. Physics makes three promises about broad classes of networks, each
promise is one line of linear algebra, and each line becomes a function the course
reuses for twelve more weeks.

**Reciprocity: S = Sᵀ.** From Lorentz reciprocity: any network of linear, isotropic
materials — metal, dielectric, any losses — transmits identically in both
directions: S₂₁ = S₁₂, always, regardless of how asymmetric the layout looks. What
breaks it: magnetized ferrites (isolators, circulators), plasmas, and *active
devices* — a transistor's whole job is S₂₁ ≫ S₁₂. So a reciprocity check is also an
activity detector. Residual: max |S − Sᵀ| over the band; plain transpose, no
conjugate — say it now, because mixing the transposes is the homework's classic bug.

**Losslessness: SᴴS = I — derived twice.** Fast: power in = |a|², power out = |b|²
summed over ports; lossless means ‖b‖² = ‖a‖² for *every* excitation; ‖Sa‖² = ‖a‖²
for all a is the definition of unitary. First-principles, because "for every
excitation" is the point students skate over: ‖a‖² − ‖Sa‖² = aᴴ(I − SᴴS)a is a
quadratic form; if it vanishes for all a, the Hermitian matrix I − SᴴS is zero —
term by term. Column by column that says |S₁₁|² + |S₂₁|² = 1: our λ/4 line
(0.3846² + 0.9231² = 1.0000) and transformer (0.36 + 0.64) pass on the board.
Turn it into an instrument: **unitarity residual = max over frequency of
‖SᴴS − I‖ (Frobenius)**. The pad scores 3/(2√2) = 1.06066 — compute it live:
SᴴS = ¼I, so the residual matrix is −¾I, norm ¾√2. A lossless line scores 1e-16.
One number, and "lossless" stops being a marketing word.

**Passivity: no singular value above 1.** Weaker claim, wider net: a passive
network may dissipate but may not *emit*. Power absorbed = ‖a‖² − ‖Sa‖² ≥ 0 for
every a ⇔ I − SᴴS ⪰ 0 (positive semidefinite) ⇔ every singular value σ of S obeys
σ ≤ 1. Singular values, not eigenvalues — S is not Hermitian, and the eigenvalues
of a non-normal matrix can sit innocently inside the unit circle while the network
pumps power. Residual: max over frequency of max(σ_max² − 1, 0). Zero for every
honest passive file; positive means active hardware or broken data — no third
option.

And now ask the class the homework's Q1, and make them vote: *can a passive
network show |S₂₁| > 1 at some frequency — some resonance, some clever mismatch?*
Collect the votes, then point at the algebra just written: σ_max ≤ 1 bounds every
matrix entry, so **no** — not in a real reference impedance, not at resonance, not
ever. The λ/4-line-doubles-the-voltage intuition is real physics but it is *voltage*
gain; the √Z₀ in a and b already converted the books to energy, and passive devices
have no energy to add. What can legitimately exceed 1: voltage transfer functions,
and pseudo-wave S-parameters referenced to complex Z₀ — neither of which is in a
50 Ω file. Tonight one of the three planted files shows |S₂₁| = +8 dB; the class
that voted "yes, resonance can do it" would have acquitted an amplifier.

Tolerances, the honest coda: real measured data carries noise, so the residuals are
never zero. The homework's planted "VNA" adds ~1e-4 per entry, flooring the
residuals near 1e-3; the course tolerances sit ~5× above the floor, and the
tolerance *rationale* is written next to the constants — because a tolerance nobody
can defend is a tolerance somebody will quietly widen.

### 2.4 Reference planes, flow graphs, and reading datasheets with suspicion (1:38–1:48)

**Reference planes.** S-parameters are defined *at* planes. Move the plane out by a
length ℓ of line and every wave picks up e^{−jβℓ}: S′ = diag(e^{−jβℓ₁}, e^{−jβℓ₂})
· S · diag(e^{−jβℓ₁}, e^{−jβℓ₂}). De-embedding is choosing ℓ to strip the fixture.
Two consequences, one comforting, one not: phases are meaningless until you know
where the planes are; and the shift matrix is unitary — so **the invariants cannot
see a plane error**. A file can pass reciprocity, unitarity, and passivity and
still have its phases referenced to the wrong connector. The suite convicts
liars, not sloppy bookkeepers; know which enemy you are hunting.

**Signal-flow graphs, Mason lite.** Nodes a₁,b₁,a₂,b₂; branches are S entries; a
load on port 2 is a branch Γ_L from b₂ back to a₂. One loop: S₂₂Γ_L. The one-loop
rule (all of Mason this course needs): divide the path gain by (1 − loop):

> Γ_in = S₁₁ + S₁₂S₂₁Γ_L / (1 − S₂₂Γ_L)

Sanity-limit it live: Γ_L = 0 gives S₁₁ (the matched-termination definition,
recovered); S₁₂ = 0 gives S₁₁ (no feedback path, output invisible). Lecture 11
runs this same graph with a transistor in the box to derive every gain formula it
needs — this ten minutes is an investment.

**Datasheet suspicion, the habit.** The pre-empted misconception, promised in the
syllabus: *"S₂₁ is the gain, always."* Only into matched terminations. Between
mismatched stages the transducer gain G_T involves S₁₁, S₂₂, and both Γ's — the
flow graph just showed the mechanism (those 1/(1−x) denominators), and lecture 11
makes the distinction quantitative. Second suspicion, tonight's homework in one
line: a datasheet that says "lossless" is making a *checkable* claim — 0.1 dB of
hidden loss is invisible on a 60 dB plot axis and glaring in ‖SᴴS − I‖. Files
claim; residuals testify.

### 2.5 Hour recap (1:48–1:50)

Four languages, one network: Z adds in series, Y in shunt, ABCD multiplies in
cascade, S is what the instrument speaks. S-matrices do not multiply — route
cascades through ABCD or sum the bounce series, and remember −7.44 versus −0.35 dB.
Three invariants, three one-liners: S = Sᵀ or something is active or ferrite;
SᴴS = I or something dissipates; σ_max ≤ 1 or the file is emitting power it was
never given — and no passive network prints |S₂₁| > 1 in a 50 Ω file. Hour 3 turns
all of it into running code, wrecks one cascade, and hands you three suspects.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: skrf Network, the conversions, and the invariant suite (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:05)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, scikit-rf 1.13.0. Same environment as lectures 1–3; anyone whose
`setup_check.py` failed pre-class pairs up now — do not debug installs live. (Worth
one sentence again: the pins are load-bearing; skrf 2.0.x does not import against
our numpy.)

### 3.2 The worked two-ports, printed (2:05–2:12)

Cell 3.2: three ABCD stamps (`abcd_series`, `abcd_shunt`, `abcd_line`) and the
ABCD→S formula typed once — then the board's three networks print: the pad at
−6.02 dB with power sum 0.2500 (dissipated), the 75 Ω λ/4 line at |S₁₁| = 0.3846 /
|S₂₁| = 0.9231 with power sum 1.0000 (reflected), the transformer at −0.6/+0.8.
Point at the two "1.0000"s: *lossless devices, |S₂₁| < 1, no contradiction — and
neither can go above 1, which is Q1 of your homework.* Note the array shape while
the code is on screen: everything is (nf, 2, 2), and `@` multiplies stacks
per-frequency — the whole lab has no loops.

### 3.3 A real file, read with this week's eyes (2:12–2:18)

Cell 3.3: `skrf.data.ring_slot`, the same object lecture 1 flashed as "the industry
file format." Now we can interrogate it: reciprocity residual 0.00e+00 (a
simulation — symmetric to machine zero; measured hardware never is), σ_max between
0.99922 and 0.99947 (passive with 0.05% of margin — this is what "barely passive"
looks like, and lecture 11's vendor files will look the same), unitarity residual
0.0777 (not lossless: the slot radiates — which for an antenna is the *job*).
Three numbers and the file has told us its physics before we plotted anything.

### 3.4 Conversions against the referee (2:18–2:25)

Cell 3.4: `s_to_abcd` and `s_to_z` typed from the slide formulas, then measured
against `skrf.network.s2a` / `s2z` on all 201 ring_slot frequencies: worst deltas
7.7e-15 and 4.0e-12, round trip 4.5e-16. Say the moral again, because it is the
homework's design: *same algebra, two authors, machine-precision agreement — when
your version disagrees with the library, you found a bug in seconds instead of a
mystery in week 9.* This is module 1 of the homework, verbatim.

### 3.5 Cascading done right (2:25–2:30)

Cell 3.5: three mismatched sections — a 75 Ω λ/4 line, a lossy series inductor, a
shunt capacitor — cascaded by ABCD product, then the same three as skrf `Network`
objects chained with `**`: worst delta 6.8e-16, chain |S₂₁| at 1 GHz = −1.182 dB.
One operator, one matrix product, one answer.

### 3.6 The invariant suite, built live (2:30–2:37)

Cell 3.6: the three functions of homework module 2, typed in under ten lines total
— `is_reciprocal` (plain transpose), `unitarity_residual` (conjugate transpose,
Frobenius, worst frequency), `passivity_residual` (SVD, worst σ_max² − 1). Run the
table: 50 Ω line True / 7.0e-16 / 8.9e-16; pad True / 1.06 / 0; isolator False /
1.0 / 0; ring_slot True / 7.8e-02 / 0. Four networks, twelve numbers, every one
predicted by hours 1–2 before it printed. *These three functions are course
infrastructure from tonight on — lecture 7 audits your Wilkinson with them,
lecture 11 audits a vendor's transistor file.*

### 3.7 Deliberate bug — cascading S by matrix multiplication (2:37–2:43)

Cell 3.7, promised in hour 2. First the cartoon wreck: two ×½ pads, `S @ S`, and
the product says S₂₁ = 0 — two attenuators in a row "transmit nothing," because the
product wired outputs to outputs. Everyone laughs; nobody would ship that. Then the
dangerous version: L-section + 75 Ω line. Naive: −7.44 dB. Correct: −0.35 dB. The
naive number is *plausible* — it would sail through a design review. Now run
`is_reciprocal` on it: **False**, |S₁₂ − S₂₁| = 1.651 — a cascade of two reciprocal
passive parts claiming to be non-reciprocal, which no hardware made of copper can
be. The invariant convicted the *algebra*. And the honest footnote, on the slide
and in the code: the naive product of two lossless S-matrices is still unitary
(products of unitary matrices are unitary), so the unitarity check alone would have
missed this bug — you need the whole suite, which is why the homework builds the
whole suite.

### Homework brief (2:43–2:48)

`lab/HOMEWORK.md` on screen. The story: three "measured" two-port files with claims
attached — a passive filter admitting some loss, a "LOSSLESS" filter, a "passive"
two-port. At least one is lying. Walk the modules and the two commands:

- Module 1 is the conversion library + `cascade` — refereed by skrf's `s2a`/`a2s`/
  `s2z`/`z2s` and `**` to 1e-10 (the reference solution measures ~1e-12).
- Module 2 is the core: the invariant suite you just watched me write — refereed by
  planted analytic values (the pad's 1.06066 among them). These three function
  names are permanent course vocabulary.
- Module 3: `verdict` — classify all three files, then defend the verdicts in
  ANSWERS.md with residuals quoted.
- **Predictions come first.** Q1 (can a passive |S₂₁| exceed 1 — commit to the
  power argument before you look at network C) and Q2 (predict the unitarity
  residual of a "lossless" file with 0.1 dB of hidden loss) are answered *before*
  running — committing is the assignment.
- The generator that minted the three files is in the toolkit under a SEALED
  ENVELOPE banner, ground truth included. Verdicts first, envelope after — it will
  tell you the planted Q values once you have already convicted.
- `--check` prints facts, not PASS/FAIL; `--plot` draws the two pictures Q1 and Q2
  argue about. Budget ≤ 3 hours. AI use assumed and welcome — you state the
  contracts, the AI types, the referee and the invariants keep everyone honest,
  and the verdicts carry your signature.

### Wrap-up (2:48–2:50)

Recap against the three claims: voltage died of ambiguity and waves took over — a,
b, |·|² in watts, S the matrix between them, measured by terminating everything in
50 Ω. Representations convert freely (your code now matches skrf at 1e-15) but only
ABCD multiplies — S@S produced −7.44 dB of confident nonsense and the reciprocity
check caught it. And three one-number invariants now referee every S-matrix you
will ever be handed — including tonight's three suspects, one of which is an
amplifier in a filter's clothing. Teaser: next lecture the S-parameters get a
physical home — microstrip and waveguide, where a "50 Ω trace" is a geometry
problem and the wavelength itself needs a correction factor.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 3 (*Networks*), chs. 2–3 — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 4 (for owners of the book — wave
  variables, the S/Z/ABCD tables, reciprocity and losslessness proofs this lecture
  parallels).
- [R37] scikit-rf documentation — the `Network` object and `skrf.network`
  conversion functions (`s2a`, `a2s`, `s2z`, `z2s`), this week's referee:
  https://scikit-rf.readthedocs.io/
- [R6] Collin, *Foundations for Microwave Engineering*, 2e, ch. 4 — the rigorous
  treatment of network reciprocity and realizability, for the students who want
  the field-theory roots.
