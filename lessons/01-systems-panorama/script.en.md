# Lecture 1 — Microwave Systems Panorama: dB, Link Budgets, and the Radar Equation

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (`pip install -r requirements.txt`: numpy 1.26.4,
scipy, matplotlib, pandas, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** one undergraduate EM course (Maxwell at a glance), circuits
(phasors), signals (Fourier), basic probability, Python.
**Pre-class setup:** install the stack and run `lab/setup_check.py` — it must print
`SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the landscape, and the language of dB (0:00–0:50)

### 1.1 Why this course exists (0:00–0:10)

Slide cue: the six-panel grid — a cell tower, a 77 GHz automotive radar chip, an
airport surveillance dish, a quadcopter, a satellite dish, a WiFi router torn open.

Open with the claim, not the definition. Every one of these systems is the same
machine: a source pushes microwave energy into space, space does what space does —
spreads it, bounces it, attenuates it — and a receiver digs the survivors out of the
thermal noise. A WiFi link and a fighter's fire-control radar differ in *numbers*,
not in kind. This course teaches the machine: the passive plumbing that steers the
energy (lectures 2–9), the receiver that survives the noise (10–12), and the systems
that turn it into detection — of aircraft, of missiles, of drones (13–16).

Three claims for today — write them on the board and leave them up:

1. **At microwave frequencies, the wire is a component.** When physical size is
   comparable to the wavelength, Kirchhoff's laws stop being the truth and lecture 2's
   transmission lines become the truth. Today you compute exactly where that line is.
2. **dB is the native language, and it has a grammar.** Link budgets are long chains
   of multiplications; in dB they become sums a tired engineer can audit at 2 a.m. —
   *if* every number carries its unit. Today ends with a 30 dB lie told by one
   unlabeled number.
3. **The radar equation is the Friis formula folded back on itself** — and its R⁴ is
   the single most consequential exponent in this course. It decides what a drone
   costs to detect, what stealth buys, and why surveillance antennas are the size of
   houses.

Pre-empt the question the wireless-comms students are already forming: *"I know link
budgets — is this course going to be review?"* Answer honestly: today's hour 1 is
your home turf on purpose — we start from Friis because you own it, and fold it into
the radar equation because most of you do not. By hour 2 the numbers are radar
numbers, and by lecture 4 the course is somewhere comms courses never go: inside the
matching networks, couplers, and low-noise front-ends that your link budgets always
abstracted into a single NF figure.

### 1.2 The frequency landscape — who lives where, and why (0:10–0:20)

Slide cue: the spectrum ruler, 300 MHz to 300 GHz, with tenants marked.

Walk the ruler with detection systems as the anchor tenants:

- **L-band (1–2 GHz):** long-range air surveillance (ARSR); wavelength ~20 cm —
  weather barely matters, antennas are huge, resolution is coarse.
- **S-band (2–4 GHz):** airport surveillance, weather radar; WiFi's 2.4 GHz squats
  at the bottom edge — the same physics that heats your leftovers.
- **X-band (8–12 GHz):** fire control, marine radar, *our course radar* — 3 cm
  wavelength, dishes are person-sized, beams are degrees wide.
- **K/Ka (18–40 GHz):** police radar, satellite uplinks.
- **W-band, 77 GHz:** automotive collision-avoidance radar — λ ≈ 4 mm, an antenna
  array fits on a chip, and lecture 15 lives here.

The trade running down the ruler, said once and reused all course: **higher frequency
buys smaller hardware and narrower beams from the same aperture, and pays in
atmospheric loss, component cost, and power.** A drone-detection radar picks its band
by exactly this trade — hold the thought, it is homework 15.

Now the λ argument, with numbers on the board. λ = c/f: at 50 Hz, 6000 km — power
grids never think about this; at 2.4 GHz, 12.5 cm; at 10 GHz, 3 cm; at 77 GHz, 4 mm.
A 3 cm PCB trace is 10⁻⁴ wavelengths at 1 MHz — a wire; a quarter wavelength at
2.4 GHz — a component with its own agenda; a full wavelength at 10 GHz — an antenna
whether you wanted one or not. Rule of thumb for the ledger: **distributed effects
matter beyond ~λ/10.** Hour 3 prints this exact table.

Common student question to pre-empt: *"where exactly does 'microwave' start?"*
Honest answer: it's a culture, not a boundary — the convention says 300 MHz–300 GHz,
but the real criterion is the λ/10 rule against *your* geometry. A 10 m antenna
tower at 30 MHz is doing microwave engineering; a 1 mm transistor at 1 GHz is not,
yet.

### 1.3 Decibels done right (0:20–0:32)

Board work — this is the course's arithmetic and it must become reflex.

Definitions, stated precisely because sloppiness here is where bugs breed:

> dB = 10·log₁₀(power ratio). Always power. Always a *ratio*.
> dBm = dB relative to 1 mW — an absolute power dressed as a ratio.
> dBi = antenna gain relative to isotropic. dBsm = RCS relative to 1 m².

The five numbers to memorize, now: ×2 = +3.01 dB; ×10 = +10 dB; ×½ = −3.01 dB;
kT₀ = **−173.98 dBm/Hz** ≈ −174 (the thermal-noise floor per hertz at the 290 K
reference — every receiver datasheet on earth quotes against this); and 0 dBm = 1 mW.
Everything else is sums: a 1 MHz bandwidth sits 60 dB above 1 Hz, so its noise floor
is −174 + 60 = −114 dBm. Hour 3 prints −113.98.

The grammar, boxed on the board:

> dBm + dB = dBm (power through a gain — legal)
> dBm − dBm = dB (two powers compared — legal, yields a ratio)
> **dBm + dBm = nonsense** (multiplying two powers — physics does not do this)

War story, 60 seconds: a satellite terminal review, a spreadsheet cell containing
`=P_tx + G_ant` where P_tx had been entered in dBW by one team and read as dBm by
another. Thirty dB — a factor of a thousand — hiding in plain sight, discovered not
by review but by the link refusing to close on the roof. Every number in this course
carries its unit in its *name*: `p_t_dbm`, `p_t_w`, `fspl_db`. You will see the same
convention enforced in the homework toolkit, and hour 3 re-enacts this exact bug.

### 1.4 The Friis transmission formula — derived twice (0:32–0:45)

The one-way question: transmit P_t through an antenna of gain G_t; what lands at a
receive antenna of gain G_r a distance R away?

**Level 1 — energy spreading (the fast derivation).** An isotropic radiator spreads
P_t over a sphere: density S = P_t/4πR². A real antenna concentrates: S = P_tG_t/4πR².
The receive antenna presents an effective aperture A_e and catches P_r = S·A_e.
Antenna theory (lecture 13 proves it) says A_e = G_rλ²/4π. Multiply:

> P_r = P_t G_t G_r λ² / (4πR)² — the Friis formula.

**Level 2 — in dB, as engineers actually write it.** Define free-space path loss
FSPL = (4πR/λ)², i.e. FSPL_dB = 20·log₁₀(4πRf/c). Then:

> P_r[dBm] = P_t[dBm] + G_t[dBi] + G_r[dBi] − FSPL[dB]

The number to anchor the formula: **FSPL(1 GHz, 1 km) = 92.45 dB.** Hour 3 prints
it; the homework checker demands it.

Pre-empt the misconception that λ² plants: *"higher frequency means space eats more
power?"* No — free space is lossless (hour 3 *measures* this with scikit-rf, and the
result surprises people). The λ² lives in the receive aperture: a fixed-gain antenna
gets physically smaller as f rises and catches less. Raise frequency at fixed *dish
size* and G_r grows as f², FSPL's λ² cancels, and the link *improves*. Where the λ²
sits — aperture, not medium — is precisely the kind of bookkeeping this course
exists to make automatic. Friis's own 1946 paper [R21] is two pages; it is assigned,
and it is a masterclass in saying exactly what you mean.

Worked example on the board (the homework's WiFi link): 2.4 GHz, P_t = 20 dBm,
G_t = 6 dBi, G_r = 2 dBi, B = 20 MHz, NF = 7 dB. At 50 m: FSPL = 74.03 dB, so
P_r = 20 + 6 + 2 − 74.03 = **−46.03 dBm**. Noise floor: −174 + 73 (20 MHz) + 7 =
−94 dBm. SNR = **47.93 dB** — luxurious. At 1 km: **21.91 dB** — still fine. The
budget's whole personality is that every term is a *named, unit-carrying* line item.

### 1.5 Hour recap (0:45–0:50)

Three sentences, then break: microwave is where geometry is measured in wavelengths,
and you now compute the boundary; dB is a grammar with two legal moves and one
felony; Friis is spreading times aperture, 92.45 dB at (1 GHz, 1 km), and the λ²
lives in the antenna, not in space. Hour 2 aims this machinery at a target that
does not want to be seen.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: noise, the radar equation, and the course map (1:00–1:50)

### 2.1 The noise floor — what the receiver is up against (1:00–1:12)

The signal has been computed; now the enemy. Every resistor at temperature T
delivers available noise power kTB — Johnson–Nyquist, stated today, derived when
lecture 10 needs its fine print. At the IEEE reference T₀ = 290 K:

> N = kT₀B = −174 dBm/Hz + 10·log₁₀(B)

Real receivers are worse than the physics floor by their **noise figure** NF (the
SNR they steal, in dB — lecture 10 spends an hour on where it comes from and how
cascades share the blame). So the operating floor is kT₀B·F, and

> SNR[dB] = P_r[dBm] − (−174 + 10log₁₀B + NF)

Two knobs to notice now because the homework turns them: **bandwidth is a tax** —
every ×10 of B raises the floor 10 dB; and NF is paid once, off the top. The
course radar carries B = 1 MHz (floor −113.98 dBm) and NF = 3 dB.

Common student question to pre-empt: *"why not shrink B to nothing and hear
everything?"* Because the signal has structure — bandwidth carries information
(comms) and resolution (radar, lecture 15: range resolution = c/2B). B is a design
variable with two masters; homework Q4 makes you defend a choice.

### 2.2 The radar equation — assembled live (1:12–1:30)

Board work, the centerpiece of the day. A monostatic radar (one dish doing both
transmit and receive) illuminates a target of **radar cross section σ** at
range R. Build P_r in five factor-steps, each one physical, writing the chain left
to right:

1. Density at the target: P_tG/4πR² (Friis's first half).
2. The target intercepts and re-radiates: σ is *defined* as the aperture that,
   re-radiating isotropically, explains the echo. Units: m². Re-radiated: P_tGσ/4πR².
3. The echo spreads back: divide by 4πR² again. **This is the moment — say it
   slowly — the R² becomes R⁴.**
4. The dish catches it with its aperture Gλ²/4π (same dish, same G — monostatic).
5. Real radars leak: divide by system losses L.

> P_r = P_t G² λ² σ / ((4π)³ R⁴ L) SNR = P_r / (kT₀B·F)

And the inverse question — the one operators actually ask — solve for R at the
minimum usable SNR:

> R_max = [ P_t G² λ² σ / ((4π)³ kT₀B·F·L·SNR_min) ]^(1/4)

**That outer ¼ exponent governs everything.** Doubling range costs 12.04 dB (hour 3
measures it against the one-way 6.02). Doubling transmit power buys 19% more range
(2^¼ = 1.189). Cutting σ by 4000× — airliner to drone — shrinks detection range
only 7.95×. Fourth roots make radar improvements brutally expensive and stealth
merely *worthwhile* rather than magical.

RCS, honestly, in ninety seconds: σ is not the target's area — it is how the target
*scatters*, and it swings wildly with aspect angle and frequency (a fighter can be
1 m² nose-on and 100 m² broadside). The ledger numbers we will use as class
standards: airliner ≈ 40 m² (+16 dBsm), fighter ≈ 1 m² (0 dBsm), small quadcopter
≈ 0.01 m² (−20 dBsm), and — the number that makes the drone problem hard — a large
bird is also about −20 dBsm. Telling them apart is lecture 15's micro-Doppler story;
today we only ask *whether we can see it at all*. Fluctuation, Swerling models, and
what "≈" hides: lecture 14.

### 2.3 The course radar meets its customers (1:30–1:40)

Introduce the instrument the course will keep upgrading — the **course radar**, a
compact X-band perimeter set: f = 10 GHz, P_t = 10 kW, G = 33 dBi, B = 1 MHz,
NF = 3 dB, L = 6 dB, detection threshold SNR_min = 13 dB (a placeholder number
today; lecture 14 replaces it with honest P_d/P_fa mathematics).

Work the three customers on the board, in dB, out loud — this is the homework's
exact computation, and hour 3 prints it:

- **Airliner, σ = 40 m²: R_max = 32.65 km.**
- **Fighter, σ = 1 m²: R_max = 12.98 km** (σ fell 16 dB; range fell 16/4 = 4 dB
  = ×0.40).
- **Drone, σ = 0.01 m²: R_max = 4.11 km.**

Then the reality-check the class will remember: *can this radar see the airliner at
400 km, like the en-route surveillance radars do?* (400/32.65)⁴ ≈ **22,500× more
power-aperture product needed.** That is why ARSR-class radars run megawatt
transmitters behind antennas the size of a house, and why nobody detects drones at
400 km. The R⁴ tyranny, in one number.

War story, 60 seconds: coastal surveillance installation, proud of a 200 km spec
against fishing vessels — commissioning week, a customer asks about jet-skis. Same
radar, σ down ~23 dB, range quietly divides by 3.8. Nobody lied; the fourth root
simply does not care about marketing. The homework's Q2 is this story with a drone
in the jet-ski's seat.

### 2.4 The course map — every block of this radar is a lecture (1:40–1:48)

Slide cue: the radar block diagram, each block stamped with a lecture number.

Walk the signal path: the transmitter feeds a **transmission line** (L2) through
**matching networks** (L3, 6) described by **S-parameters** (L4) on **microstrip
and waveguide** (L5), through **couplers** (L7) and **filters** (L8–9) to an
**antenna array** (L13); the echo returns through the **LNA and the noise budget**
(L10–11), gets **mixed down** (L12), and lands in the detector where the **radar
equation** (L14), **FMCW/Doppler processing** (L15), and **beamforming with
collision-avoidance logic** (L16) finish the job. Today you priced the whole
machine from the outside; sixteen weeks from now you will have opened every box.

Say the differentiator plainly: most microwave courses stop at the amplifier;
most radar courses assume the microwave parts arrive by mail. This course refuses
the split — the detection thread (drones, aircraft, collision avoidance) is why
the passive plumbing matters, and the plumbing is why the detection numbers are
achievable.

### 2.5 Hour recap (1:48–1:50)

The noise floor is −174 + 10logB + NF and it is not negotiable; the radar equation
is Friis twice with σ in the middle, and its fourth root prices every improvement;
the course radar sees the airliner at 32.65 km and the drone at 4.11 km — and hour 3
makes the machine that computed those numbers, then breaks it with one unlabeled
unit.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: NumPy as an RF calculator, and first contact with scikit-rf (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:05)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, pandas, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed pre-class
pairs up now — do not debug installs live. (One install note worth saying aloud:
the course pins scikit-rf 1.13.0 because 2.0.x crashes on import against our numpy
pin — version pins are load-bearing, welcome to engineering.)

### 3.2 dB warm-up (2:05–2:12)

Cell 3.2: `db()` and `undb()` as one-liners, then the five numbers: db(2) = 3.0103,
db(10) = 10, kT₀ = −173.98 dBm/Hz, the 1 MHz floor at −113.98 dBm, the 20 MHz floor
at −100.96. Close the cell by printing the grammar: dBm + dB = dBm; dBm + dBm =
nonsense. It looks trivial. Cell 3.7 is waiting.

### 3.3 The λ table (2:12–2:17)

Cell 3.3: one 3 cm trace, six frequencies. At 1 MHz it is 10⁻⁴ λ — a wire. At
2.4 GHz, 0.24 λ — past the λ/10 line, a component. At 10 GHz, 1.0 λ — an antenna.
At 77 GHz, 7.7 λ — a distributed system. Point at the 2.4 GHz row: *this is why
your laptop's WiFi section looks like plumbing, not wiring.* Lecture 2 starts at
this table's implication.

### 3.4 Friis two ways — the referee principle, demonstrated (2:17–2:25)

Cell 3.4: the WiFi link computed twice — once as the dB chain from the board, once
as a watts chain that walks the physics (density, aperture, kTBF) with no dB
anywhere. Both print P_r = −46.03 dBm, SNR = 47.93 dB at 50 m; agreement 0.0e+00 dB.
Say the moral out loud, because it is the homework's design: *two independent
implementations, one answer — when they disagree, one of you mixed units, and the
disagreement is loud.* This is what "the library is the referee, not the player"
looks like when the referee is just physics in different clothes.

### 3.5 The radar equation runs (2:25–2:33)

Cell 3.5: the course radar meets its customers — 32.65, 12.98, 4.11 km print in
three lines. Then the two exponent measurements: doubling range 10→20 km costs
12.04 dB (the one-way 6.02 printed beside it), and the 400 km question: 22,524×.
Invite predictions before running the σ×2 line in the homework — the class that
just watched 2^¼ = 1.189 will still be surprised how *little* doubling the power
moves the range.

### 3.6 First contact with scikit-rf — and one honest lesson (2:33–2:40)

Cell 3.6: load `skrf.data.ring_slot` — a real 2-port S-parameter dataset, 75–110
GHz. Plot |S11|, |S21| in dB (lecture 4 will teach you to read them) and the Smith
chart (lecture 3 will teach you the chart). The point today is only: *this is the
file format and the object model the entire industry lives in, and it is three
lines of Python.*

Then the honest lesson: build `skrf.media.Freespace`, run 1 km of it, print |S21| =
0 dB. **Free space is lossless.** The "path loss" of 1.4's formula was never a loss
in the medium — it is spreading plus aperture bookkeeping, which is why it lives in
antenna terms. A library that quietly agreed with the colloquial "space eats
signal" would referee nothing; skrf just refereed a *concept*. (This is also your
warning that tools model what is, not what is loosely said.)

### 3.7 Deliberate bug — the 30 dB lie (2:40–2:44)

Cell 3.7, the re-enactment hour 1 promised: `db(10e3)` = 40.0 — a perfectly true
number, in dBW — typed into the budget slot that wanted dBm (70.0). Every
downstream term is "just decibels," nothing crashes, and the drone's detection
range prints as 23.09 km instead of 4.11 — ×5.62, because 30 dB spread over a
fourth root is 10^(30/40). Point at the two numbers: *both look like radar ranges.
That is what makes unit bugs lethal — they produce reasonable wrong answers.* The
fix is not vigilance, it is naming: `p_t_dbm` cannot receive `db(p_t_w)` without
the reader flinching. The homework toolkit enforces this everywhere.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. Walk the story — the airfield radar, three aircraft,
one question — then the modules and the two commands:

- Module 1 is the dB machinery on your home turf (the WiFi link); module 2 is the
  core — the radar equation forward *and inverted, closed-form*; module 3 is the
  three-customer verdict.
- **Predictions come first.** Q1 (six versus twelve) and Q2 (what stealth buys) are
  answered *before* running — committing to a number is the assignment.
- `--check` prints facts, not PASS/FAIL — the watts-referee deltas, the round trip,
  the 2^¼. The two plots are Q2's material.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: the λ/10 boundary, computed; the dB grammar, plus
one felony committed and caught; the radar equation, Friis folded double, fourth
root and all — 32.65 km for the airliner, 4.11 for the drone, and now you know why
both numbers are what they are. Teaser: next lecture we stop treating the cable as
a wire — the telegrapher's equations, reflection, and the moment a length of coax
becomes an impedance transformer.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 1 (*Radio Systems*), chs. 1–2 — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R21] Friis, "A Note on a Simple Transmission Formula," *Proc. IRE* 1946 — two
  pages, assigned in full.
- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems* (RES.LL-001),
  lectures 1–2 — free: https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
- [R32] O'Donnell, *Radar Systems Engineering* (IEEE AESS) — free: http://radar-course.org/
- [R1] Pozar, *Microwave Engineering* 4e, ch. 14 (for owners of the book — the
  wireless-systems chapter this lecture parallels).
