# Lecture 3 — The Smith Chart & Impedance Matching

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course env from lecture 1: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**; optional
`pip install pysmithchart`)
**Prerequisites:** lecture 2 (Γ, SWR, Z_in of a terminated line — we use all
three constantly today), complex arithmetic without fear.
**Pre-class setup:** course env installed; run `lab/setup_check.py` — it must
print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the chart (0:00–0:50)

### 1.1 Why a 1939 paper calculator still runs the industry (0:00–0:08)

Slide cue: a modern VNA screen next to Smith's 1939 original — the same
circles, eighty-seven years apart.

Open with the object, physically: hold up a printed chart. Phillip Smith drew
this at Bell Labs in 1939 [R19] because he was tired of computing complex
arctangents by hand. Every network analyzer on earth still boots up with his
picture on the screen — not out of nostalgia, but because the chart is the
*coordinate system in which microwave design is legible*. Today you learn to
read it, walk on it, and design with it.

Three claims for today — board, leave them up:

1. **The entire passive universe fits in a disk.** The map Γ = (z−1)/(z+1)
   takes every impedance with R ≥ 0 — the whole right half-plane, out to
   infinity — into a circle of radius one. Nothing legal ever leaves the
   disk. That compression is not a trick; it is what reflection physically
   *is*, and you computed it all of last week.
2. **On this chart, circuit moves are geometric moves.** A length of line
   *rotates* you. A series reactance slides you along one family of circles;
   a shunt susceptance along another. Matching — this course's first real
   design act — is choosing two moves that end at the center.
3. **A perfect match is a resonance you built, and it bills you in
   bandwidth.** Today both of our designs will be *exact* at 2.4 GHz — the
   referee will print |Γ| ≈ 10⁻¹⁶ — and the homework's whole drama is what
   they do 400 MHz away. Lecture 6 turns this into a theorem (Bode–Fano);
   today you will *watch* it.

Pre-empt the objection someone is already typing: *"isn't the chart obsolete?
Software does all this."* Backwards. Software *plots on* the chart — the
chart is the coordinate system, not the calculator. In lecture 11 you will
read amplifier stability circles, noise circles, and gain circles, all drawn
on this same disk, and decide where your design point lives; the engineer
who can't read the chart is the one the software is obsoleting. Datasheets,
VNA screens, and every matching discussion you will ever have at a
whiteboard happen here.

### 1.2 The bilinear map — derived twice (0:08–0:20)

**Level 1 — plug in and look (the fast version).** From lecture 2, with
z = Z/Z₀ normalized:

> Γ = (z − 1)/(z + 1)   ⇔   z = (1 + Γ)/(1 − Γ)

Check the landmarks, out loud, on the board:

- short, z = 0 → Γ = −1 (left edge; all of it reflected, upside down)
- open, z → ∞ → Γ = +1 (right edge; all of it back, right side up)
- matched, z = 1 → Γ = 0 (the center — the bullseye of this entire lecture)
- pure reactance z = jx → |Γ| = |jx−1|/|jx+1| = 1 (the rim: stores, never
  absorbs)
- our antenna, z_L = 0.72 − j0.42 → Γ = 0.285∠−110.0° (inside, lower left)

Passive means R ≥ 0 means |Γ| ≤ 1: hour 3 throws four thousand random
passive impedances at the map and the largest |Γ| that comes back is
0.999963. The disk holds.

**Level 2 — why circles map to circles (the first-principles version, framed
as explaining the first).** The map is bilinear (a Möbius transformation),
and bilinear maps are compositions of translations, scalings, and *one
inversion* w → 1/w. Translations and scalings obviously preserve circles;
the inversion is the only interesting step, and for it, write a circle as
α(u² + v²) + βu + γv + δ = 0 — under u + jv → 1/(u + jv) this swaps α and δ
and the equation stays the same *form*. Lines are circles with α = 0 —
circles through infinity. So the grid of the impedance plane — the vertical
lines R = const, the horizontals X = const — lands as two families of
circles:

> constant r: circles centered (r/(1+r), 0), radius 1/(1+r) — all tangent at
> Γ = 1
> constant x: arcs centered (1, 1/x), radius 1/|x| — also tangent at Γ = 1

That tangency point Γ = 1 is the open circuit — the image of infinity, where
all the grid lines of the far half-plane crowd together. Sixty seconds of
staring at this and the chart stops being a mandala and becomes graph paper.

Common student question, pre-empt it: *"why does the whole infinite
half-plane fit?"* Because Γ is a *ratio of waves*, and a passive load can at
most reflect everything (|Γ| = 1). Impedance is unbounded; reflection isn't.
The chart is the honest currency — this is also why your VNA measures Γ and
computes Z, never the reverse (lecture 4 makes that precise).

### 1.3 Reading the chart — a guided walk (0:20–0:32)

Slide cue: the hand-drawn chart, large; then the same chart with z_L plotted.

Document-camera time (the way it will appear in every datasheet forever).
Plot the course antenna — Z_L = 36 − j21 Ω, the patient from homework 2 — in
four slow steps:

1. normalize: z_L = 0.72 − j0.42;
2. find the r = 0.72 circle (between the 0.5 and 1.0 printed circles);
3. find the x = −0.42 arc (lower half — capacitive; inductive is upper);
4. the intersection is the point. One point, both coordinates, no algebra.

Now read *off* the chart what lecture 2 computed: the distance from center
is |Γ| = 0.285; the radial scale at the bottom of a paper chart converts it
to SWR = 1.80 and return loss 10.9 dB without a calculator — that is the
chart's original job, arctangents for free. Say the translations aloud once
more (they must be reflexes by lecture 6): |Γ| 0.285 ⇔ SWR 1.80 ⇔ RL
10.9 dB ⇔ 91.9% delivered.

Draw the **SWR circle**: center at the origin through z_L. Every impedance
on that circle reflects exactly as hard as our antenna; every point a
lossless line can ever take us also lives on it — which is the next section.
The circle is the budget; the match is the escape from it.

War story, 90 seconds: a 2.4 GHz product team measures their antenna
*through 30 cm of test cable* and designs a beautiful L-section for the
measured impedance. Built, it made things worse. Nothing was miscomputed:
the cable had rotated the point nearly a full turn around the SWR circle,
so they matched an impedance that existed only at the far end of a cable
that would not ship with the product. On the chart the error is one glance —
right circle, wrong angle. Reference planes get their formal treatment in
lecture 4 (de-embedding); today's lesson is cheaper: *know which plane your
point lives at before you move a millimeter.*

### 1.4 Motion — lines rotate you, and the admittance chart (0:32–0:46)

The chart earns its keep the moment things move. From lecture 2:

> Γ_in(ℓ) = Γ_L e^(−j2βℓ)

Magnitude untouched; phase reduced by 2βℓ. On the chart: **moving toward the
generator rotates you clockwise around the center along the SWR circle**,
at two electrical degrees per degree of line — a full lap every half
wavelength. That factor of two, and its direction, are the two things
everyone gets wrong once; pre-empt the direction now: the phase of Γ
*decreases* going toward the generator because the reflected wave has
farther to travel back — e^(−j2βℓ), minus sign, clockwise. Print it on your
retina.

Numbers on the board, verified in hour 3 (`zin_line` — lecture 2's tangent
transformation, now with a geometric soul):

- ℓ = λ/8: z rotates 90° → Z_in = 28.4 + j6.0 Ω
- ℓ = λ/4: 180° — *point inversion through the center* → Z_in = 51.8 +
  j30.2 Ω = Z₀²/Z_L. The quarter-wave inverter of lecture 2 is just
  "diametrically opposite" — that is the entire proof, and it is one
  sentence long on this chart.
- the SWR circle crosses the real axis twice per lap: at ℓ = 0.097λ,
  Z_in = 27.8 Ω = Z₀/SWR (a voltage minimum), and at ℓ = 0.347λ,
  Z_in = 89.9 Ω = Z₀·SWR (a voltage maximum). Lecture 2's standing-wave
  anatomy, collapsed to two axis crossings.

**The admittance chart.** The second move-family in matching is *shunt*
elements, and shunt elements add admittances: y = 1/z, and in Γ-terms
y's point is z's point **reflected through the origin** — because inverting
z is a 180° rotation (the λ/4 fact again, frequency-free this time). So the
same disk serves both currencies: read impedance normally, or flip to
admittance by taking the diametrically opposite point (or overlay the
rotated grid, as printed combo charts do). Our antenna: y_L = 1.036 +
j0.605 — and say the sign discipline out loud, because it flips between
currencies: a capacitive load has *negative* reactance but *positive*
susceptance; +j means capacitive in admittance country. This
currency-and-sign discipline is exactly what hour 3's deliberate bug
violates, with a result you will enjoy watching.

Series element: slides you along a **constant-r circle** (r frozen, x
moves). Shunt element: slides you along a **constant-g circle** (g frozen,
b moves). Line: rotates. Three moves — that is the complete instruction set.
Matching is a two-instruction program.

### 1.5 Hour recap (0:46–0:50)

Three sentences, then break: the chart is the bilinear image of every
passive impedance, circles to circles, rim is reactance, center is home;
lines rotate you clockwise toward the generator at 2βℓ with λ/2 per lap, and
λ/4 is inversion — which is also why admittance lives diametrically
opposite; series moves ride r-circles, shunt moves ride g-circles. Hour 2
uses exactly these three moves to put our antenna in the center of the disk
— twice.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: matching, two ways (1:00–1:50)

### 2.1 Why match, and the two-move principle (1:00–1:12)

What does matching buy? Be honest with the numbers, because they are more
interesting than the folklore. Our antenna unmatched delivers 91.9% of
incident power — the match recovers only 0.37 dB. If 0.37 dB were the whole
story nobody would bother. The real purchases: the feed line stops carrying
standing waves (SWR 1.80 → 1.00 — homework 2 showed what those do over 10 m
of real cable); the transmitter sees 50 Ω resistive instead of a load that
wanders with every centimeter of cable length (lecture 11: an amplifier's
gain, noise, and even stability are functions of what it sees); and
downstream components get the impedance they were characterized at.
Matching is less about power than about *making the system composable*.

One honest distinction before we design, because it prevents a confusion
that surfaces every year: today we match the load *to the line* — drive
Γ = 0, kill the reflection. That is not automatically the same as conjugate
matching a *source* for maximum power transfer; the two coincide when the
source is itself 50 Ω resistive, which is the standing assumption of this
course until lecture 11 reopens the question for amplifiers. If you have
heard "maximum power transfer needs Z_s*" — correct, different problem,
parked until then.

**The two-move principle.** The target is the center, y = 1 + j0 (or
z = 1 + j0 — same point). Whatever element you apply *last* determines the
rail you must be standing on just before: a final **shunt** element can only
change b, sliding along a constant-g circle — so the move before it must end
on the **g = 1 circle**. A final series element rides constant-r — its rail
is the **r = 1 circle**. Every matching topology in this course — today's
L-section and stub, lecture 6's multisections — is a path built backwards
from the center along legal rails. Say it as a slogan: *last move picks the
rail; first move gets you to the rail.*

### 2.2 The L-section — closed forms from chart geometry (1:12–1:26)

Slide cue: the two topologies side by side, with the region rule.

Two components, one series and one shunt; the only question is the order,
and the chart answers it. If the load sits **inside the 1 + jx circle**
(that's r > 1 territory — R_L > Z₀), a shunt element at the load can reach
the r = 1 rail, so shunt comes first (at the load) and series finishes. If
the load sits **outside** (R_L < Z₀ — our antenna, 36 Ω), it is the other
way: **series first at the load** to reach the g = 1 rail, shunt to finish.
One topology per region — the other one's square root goes negative, which
is the algebra's way of saying "you can't get there on that rail." The
homework's designer must *discover* the region, not assume it; the checker
feeds it a 120 + j90 Ω load to make sure.

**Level 1 — the derivation as chart geometry (fast, and it is the real
one).** For our region: after the series element x, we are at
z = r_L + j(x_L + x); demand that this lands on the g = 1 circle:
Re{1/z} = 1... one line of algebra:

> r_L² + (x_L + x)² = r_L   (normalized; that IS the g = 1 circle)
> ⇒ x = ± √(r_L(1 − r_L)) − x_L, then b = ∓ √((1 − r_L)/r_L)

**Level 2 — the same thing un-normalized (the formulas you'll see in
Pozar 5.1),** stated so the homework has its contract:

> X = ± √(R_L(Z₀ − R_L)) − X_L    B = ± √((Z₀ − R_L)/R_L) / Z₀

Two sign choices, two designs — both legal, both exact. Work our antenna,
out loud, every number to the board (hour 3 prints them all):

- √(36 · 14) = 22.45 Ω. Solution 1: X = +22.45 + 21 = **+43.45 Ω** — an
  inductor, 43.45/(2π·2.4 GHz) = **2.881 nH**; B = **+12.47 mS** — a
  capacitor, **0.827 pF**.
- Solution 2: X = −22.45 + 21 = **−1.45 Ω** — a 45.7 pF series capacitor
  (basically a wire with paperwork); B = −12.47 mS — a **5.32 nH** shunt
  inductor.
- Both intermediate points: y = 1 ∓ j0.624, *exactly* on the g = 1 rail —
  the checker prints Re(y) = 1.000000000, nine digits, because the algebra
  is the geometry.

And the number that predicts hour 3's bandwidth measurements before we make
them: this match's loaded Q is √(Z₀/R_L − 1) = **0.62** — a lazy, forgiving
resonance, because 36 Ω is not far from 50. Matching 5 Ω would cost Q = 3
and the band would show it. Hold that thought for 2.4.

Where L-sections live: lumped L and C with usable self-resonance run out
roughly around 2–6 GHz depending on how honest your parasitics are — which
is why the phone in your pocket (sub-6 GHz) is full of L-sections and the
radar bench upstairs (10 GHz) is not. Above that, copper geometry *is* the
component — next section.

### 2.3 Single-stub matching — the distributed way (1:26–1:40)

Slide cue: the stub tuner topology; then both solutions on the chart.

No components at all: a length **d** of the same 50 Ω line, then a **shunt
stub** — an open- or short-ended spur of line, length **ℓ**, whose input is
a pure susceptance (rim of the chart, rotated to wherever you need). Two
lengths of copper, printed for free on any PCB; this is *the* microwave
match.

The design in chart language — it is the same two-move program: the line d
is the free rotation (move 1), the shunt stub is the susceptance cancel
(move 2). Because the last move is **shunt**, everything happens in
**admittance**: rotate the load's y clockwise along the SWR circle until it
crosses the **g = 1 circle** — it must cross, every SWR circle does, twice
per half-lap — read the leftover b there, and cut the stub to add −b.
Arrive at y = 1. Done. On the document camera, walk it: y_L at 1.036 +
j0.605... rotate... the circle crosses g = 1 at y = 1 + j0.595 and again at
y = 1 − j0.595. Two crossings, two designs, exactly like the L-section's ±.

The analytic version (Pozar 5.2 — the homework's contract; derivation is
lecture-2 algebra plus patience): with t = tan βd,

> t = [X_L ± √(R_L((Z₀−R_L)² + X_L²)/Z₀)] / (R_L − Z₀)
> then d/λ = arctan(t)/2π (+ λ/2 if negative), and the stub cancels the
> susceptance B at that plane: open stub ℓ = −arctan(B Z₀)/2π, short stub
> ℓ = arctan(1/(B Z₀))/2π, + λ/2 into [0, λ/2) as needed.

Our antenna's two solutions, on the board (hour 3 verifies each at 10⁻¹⁶):

- **Solution 2 (take this one): d = 0.1993 λ = 24.9 mm, open stub
  ℓ = 0.0854 λ = 10.7 mm.** Lands at y = 1 − j0.595, stub adds +j0.595.
- Solution 1: d = 0.4953 λ = 61.9 mm, open stub ℓ = 0.4146 λ = 51.8 mm.
  Lands at y = 1 + j0.595. Note d is nearly a *full lap* — 0.9 λ of total
  copper against solution 2's 0.28 λ. Both are perfect at f₀. They are not
  the same product — the homework makes you measure why, and "take the
  short one" will stop being folklore and become a number.

Why prefer the open stub on a PCB (microstrip): a short needs a via, and
vias are lecture 5's parasitics; in coax and waveguide the short is the
clean one. Both closed forms are in the homework toolkit's contract; the
checker exercises `kind="short"` once to keep you honest.

The discipline that this design runs on — underline it, hour 3 will attack
it: **a shunt element speaks admittance, so the rotation must stop on the
g = 1 circle of the admittance chart.** Stop where the *impedance* reads
1 + jx — a perfectly natural-looking move, the r = 1 circle looks exactly
like a rail — and you have stopped at the point diametrically opposite the
right one. The two planes are λ/4 apart; the algebra will even hand you a
plausible stub length. Everything looks fine until the referee measures it.
Hour 3, cell 3.7.

### 2.4 The quarter-wave rejoined, forbidden regions, and the price (1:40–1:48)

**λ/4, revisited from above.** Lecture 2's transformer matches only *real*
loads — now you can see why at a glance: Z₀' = √(Z₀ R) needs a real R, i.e.
a point on the chart's real axis. But the axis is two rotations away for
anyone: every SWR circle crosses it twice per lap (our antenna: 27.8 Ω at
0.097 λ, 89.9 Ω at 0.347 λ — section 1.4's numbers). So "λ/4 can't match
complex loads" is folklore with a footnote: *pre-rotate, then transform* —
line + λ/4 section is a two-move program too. Homework 2 already built this
without the geometry; now the geometry is yours.

**Forbidden regions.** Each topology reaches only part of the disk, and the
chart shows which part with no algebra: a series-first L-section can only
leave the load along its constant-r circle — if that circle never crosses
g = 1 (it happens exactly when R_L > Z₀), the topology is dead for that
load, which is the region rule of 2.2 seen from the other side. Same
argument kills shunt-first for R_L < Z₀, and draws the reach of any
fixed-topology tuner. When lecture 11 hands you a transistor whose optimum
noise source sits in an awkward corner of the disk, this is how you will
pick the network that can actually get there.

**The price.** Both of today's designs are *exact* at one frequency —
because both are resonances: energy sloshing between a + jX and a − jB that
cancel only where they were tuned to. Q counts the sloshing. The L-section
stores energy in two small elements, Q = 0.62; the stub designs store it in
line lengths — and a line's electrical angle 2πd·f/f₀ drifts *in proportion
to d*, so solution 1's 0.91 λ of copper unwinds three times faster than
solution 2's 0.28 λ. Prediction on the board before hour 3 measures it:
worst in-band return loss over 2.0–2.8 GHz should rank L-section, then
stub 2, then stub 1 — and stub 1 will actually be *worse than the bare
antenna* at the band edges. A perfect match at f₀ that is a liability at
f₀ ± 400 MHz: that sentence is the Bode–Fano criterion (lecture 6) spoken
casually — match depth × bandwidth is a budget set by the load's own Q, and
every network only chooses how to spend it.

War story, 60 seconds: an IoT design matched its antenna gorgeously —
28 dB return loss, dead center of channel 7 — and failed regulatory conducted
tests on channels 1 and 13. The "fix" that shipped was a *worse* match at
center (14 dB) that held 12 dB across the band: the golden sample was a
resonance, the product was a bandwidth. You will make exactly this trade in
the homework, with numbers.

### 2.5 Hour recap (1:48–1:50)

The two-move principle: last move picks the rail (shunt → g = 1, series →
r = 1), first move gets you there; the L-section is closed-form chart
geometry, 2.88 nH + 0.83 pF for our antenna, region rule included; the stub
match is rotate-and-cancel in admittance, 24.9 mm + 10.7 mm of bare copper,
two solutions that are not the same product; and every exact match is a
resonance billing you in bandwidth. Hour 3 builds all of it in scikit-rf,
then commits hour 2's one deadly sin on purpose.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the chart in scikit-rf, and both matches built live (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate
while typing; every claim from hours 1–2 becomes a printed number or a
plotted point.

### 3.1 Setup verification (2:00–2:05)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x,
matplotlib 3.10.x, scikit-rf 1.13.0, plus a pysmithchart line (present or
"optional — skrf draws our charts"; either is fine, nothing today needs
it). Anyone whose `setup_check.py` failed pre-class pairs up now — we do
not debug installs live.

### 3.2 The map itself (2:05–2:12)

Cell 3.2: `gamma = lambda z: (z - Z0)/(z + Z0)` — the whole chart is one
lambda. Feed it the antenna: Γ = −0.0974 − j0.2680 = 0.2851∠−109.97°, and
the lecture-2 numbers fall out: SWR 1.7976, RL 10.90 dB, 91.9% delivered.
Then the sales pitch, empirically: 4000 random passive impedances, max |Γ|
= 0.999963 — *the disk holds*. Close with y_L = 1.0363 + j0.6045: same
point, admittance glasses.

### 3.3 Rotation, watched (2:12–2:20)

Cell 3.3: `zin_line` at λ/8, λ/4, 3λ/8 — three different impedances, |Γ| =
0.285098 all three times, printed to six digits: *a lossless line cannot
change how much reflects, only the phase you catch it at.* The λ/4 line
prints 51.81 + j30.22 and so does Z₀²/Z_L next to it — inversion, verified.
The v-min and v-max land at 27.82 Ω and 89.88 Ω — Z₀/SWR and Z₀·SWR on the
real axis, lecture 2's standing waves as two axis crossings. Then the
first chart of the day: `skrf.plotting.smith`, the SWR circle walked from
d = 0 to λ/2, one full clockwise lap, waypoints tagged (`hour3_chart.png`).
Point at it: *this is the picture every design in the next 80 minutes lives
on.*

### 3.4 The L-section, designed live and refereed (2:20–2:28)

Cell 3.4: hour 2's closed form in six lines. Both solutions print: X =
43.4499 Ω → 2.8814 nH with B = 12.4722 mS → 0.8271 pF; and the C-first
twin, 45.7359 pF with 5.3170 nH. Both intermediate points print y = 1 ∓
j0.6236 — *on the rail, nine digits.* Then the referee principle, same as
homework 1's watts-vs-dB but now circuits-vs-algebra: build solution 1 in
scikit-rf (`DefinedGammaZ0`, ideal 50 Ω medium → `shunt_capacitor` **
`inductor` ** load) and ask the cascade for Γ at f₀:
**|Γ(f₀)| = 2.69 × 10⁻¹⁶.** Machine epsilon. Say the moral: the algebra
*is* the geometry, and the library built the circuit and agreed — matched
by construction, not by optimization. The homework demands < 10⁻⁸; if you
see 10⁻⁵, you rounded a value on the way in.

### 3.5 The stub, designed live and refereed (2:28–2:35)

Cell 3.5: the t-quadratic, both roots: d = 0.495274 λ (61.87 mm) landing at
y = 1 + j0.5949, and d = 0.199260 λ (24.89 mm) landing at y = 1 − j0.5949;
open stubs 0.414589 λ (51.79 mm) and 0.085411 λ (10.67 mm). The skrf
cascade (`shunt_delay_open` ** `line` ** load): **1.78 × 10⁻¹⁶ and
1.67 × 10⁻¹⁶.** Two perfect matches, zero components, ten and fifty-two
millimeters of copper. Invite the class to notice how *unequal* the twins
are before the next cell measures it.

### 3.6 Two products, one antenna — the band (2:35–2:40)

Cell 3.6: sweep 2.0–2.8 GHz, 801 points, all through the skrf cascades.
Worst in-band return loss prints: **L-section 20.16 dB, stub 2 15.34 dB,
stub 1 4.21 dB** — and the raw antenna never leaves 10.90 dB. Put the
ranking next to hour 2's prediction (Q = 0.62 lumped vs 0.28 λ vs 0.91 λ of
copper): stored energy called the order exactly. Stub 1 at the band edge is
*worse than no match at all* — the resonance you built can turn on you.
`hour3_band.png` is the homework's Q1 picture; leave it on screen.

### 3.7 Deliberate bug — matching the impedance instead of the admittance (2:40–2:44)

Cell 3.7, the sin hour 2 warned about, committed with a straight face:
rotate the line until the *impedance* reads z = 1.0000 + j0.5949 — "r = 1!
we're on the rail!" — then size an open stub to cancel the 0.5949.
Every line of that code looks like the correct design. The referee:
**|Γ(f₀)| = 0.5273, SWR 3.23** — the unmatched antenna was 0.2851, SWR
1.80. *The matching network made the antenna worse than leaving it alone.*
Then show `hour3_bug.png`: the g = 1 rail in green, the r = 1 imposter in
red, and the bug's stopping point sitting *diametrically opposite* the
correct one — because z and y live λ/4 apart, always. Nothing crashed;
every formula was correct; only the chart was wrong. The fix is not
vigilance, it is the discipline: *the next element is shunt → you are in
admittance country → the rail is g = 1.* The homework's module 2 is this
discipline, made muscle memory.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. The story: last week's antenna, matched twice
— an L-section product and a stub product — then compared as products.

- Module 1: the L-section designer — both topologies, chosen by load
  region; the checker feeds it a 120 + j90 Ω load to keep the region logic
  honest. Module 2 is the core: the stub designer, both solutions, in
  admittance — cell 3.7's discipline. Module 3: the bandwidth measurer that
  turns the sweep into quotable numbers — and returns `None` for an edge
  that never crosses, *which will happen*, and Q5 asks why.
- **Predictions come first.** Q1 (which product survives the band — count
  stored-energy elements) and Q2 (the two stub twins — factor between their
  bandwidths) are answered *before* running. Commit to numbers.
- `--check` prints facts, not PASS/FAIL: cascade residuals near 10⁻¹⁶,
  edges, worst in-band RL, a planted analytic |Γ(f)| with closed-form
  edges to calibrate your measurer. `--smith` draws your trajectories over
  the g = 1 rail — the TA reads that picture, so make it pass through the
  intermediate points.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: the disk held (0.999963); the three moves —
rotate, ride r, ride g — built two exact matches, 10⁻¹⁶ twice; and the
price printed in dB across the band, with the bug showing what happens when
you ride the wrong rail. Teaser: next lecture the chart's home network gets
formalized — S-parameters, the language every component speaks from here to
the end of the course, and the invariants (reciprocity, losslessness,
passivity) that let you catch a datasheet lying.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 3 (*Networks*), ch. 6
  (impedance matching) — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 5 (for owners of the book —
  the L-section and stub closed forms this lecture derives).
- [R19] P. H. Smith, "Transmission Line Calculator," *Electronics*, Jan
  1939; "An Improved Transmission Line Calculator," *Electronics*, Jan 1944
  — assigned for history and for the joy of watching the chart get invented.
- [R4] Orfanidis, *Electromagnetic Waves and Antennas*, ch. 13 (impedance
  matching) — free: https://www.ece.rutgers.edu/~orfanidi/ewa/
