# Lecture 5 — Planar Lines & Waveguides: Where Transmission Lines Physically Live

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course venv: numpy 1.26.4, scipy, matplotlib,
scikit-rf 1.13.0; **Python 3.12, exactly**; optional `pip install fdtd` for hour 3's
field demo)
**Prerequisites:** lectures 1–4 — especially lecture 2's Z₀ and γ = α + jβ, and
lecture 3's λ/4 transformer, both of which get physical bodies today.
**Pre-class setup:** run `lab/setup_check.py` — it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the board (0:00–0:50)

### 1.1 Where the lines live (0:00–0:08)

Slide cue: three photographs — a bare RF PCB with its plumbing-like traces, a
teardown of a 77 GHz radar module, a brass rectangular waveguide run bolted to a
radar dish.

Open with the debt we owe. For four lectures the transmission line has been a
mathematical object — a Z₀, a γ, a length in degrees. Lecture 2 never said what the
line was *made of*. Lecture 3 designed a quarter-wave transformer and never said how
long it was *in millimeters*. Today the abstraction gets a body, and the body has
opinions.

Three claims for today — on the board, left up all lecture:

1. **A "50 Ω trace" is a geometry problem.** Impedance is not a property you order
   from a catalog; it is width over height over permittivity. Today you compute the
   width — 1.11 mm on this course's board — and after today you can read any
   stackup like an RF engineer.
2. **The wavelength on a board is set by a permittivity that does not exist.**
   Microstrip fields live half in the substrate, half in the air; the wave moves at
   a speed governed by a weighted average ε_eff that is the property of neither.
   Use the substrate's ε_r instead — the single most common planar-design bug — and
   every stub you cut this semester lands 13% short. Hour 3 commits this bug on
   purpose.
3. **At 10 GHz, a hollow metal pipe out-performs every cable you own — but only
   above a cutoff frequency, and near that cutoff it turns on you.** The waveguide
   is the lowest-loss, highest-power transmission medium in the radar world, and it
   is also the course's first *dispersive* line: different frequencies travel at
   different speeds, and we will price exactly what that costs a 200 MHz signal.

Pre-empt the question forming in the back row: *"CAD tools do all of this — why
hand formulas?"* Honest answer: because the hand formula is how you know the CAD
tool is wrong. Today's formulas are accurate to a couple of percent; the tool is
accurate to the model somebody configured into it. When they disagree — and hour 3
measures the disagreement — the engineer who owns the formula wins the argument.
That is this course's referee principle pointed at geometry.

### 1.2 The microstrip and its compromise (0:08–0:20)

Slide cue: the microstrip cross-section — strip of width w, thickness t, on a
substrate of height h over a ground plane, field lines arcing through both air and
dielectric.

The microstrip is the workhorse: a copper strip on top of a grounded dielectric
slab. Cheap — it is printed, not machined; open — you can solder to it, which is
why every MMIC, filter, and bias network in a modern front-end sits on one.

Now the compromise that defines it. Draw the E-field lines: they leave the strip,
and some dive straight down through the dielectric to ground while others arc
through the *air* before coming home. The wave straddles two media. It cannot
travel at c/√ε_r (the dielectric's speed) and it cannot travel at c (air's speed);
it settles on a compromise:

> v = c/√ε_eff, with (ε_r+1)/2 ≤ ε_eff ≤ ε_r

**Level 1 — the capacitance average (the fast version).** At low frequency the
line is just L and C per meter (lecture 2's cell). The C is set by electrostatics:
a capacitor filled partly with dielectric, partly with air. Compute the same
geometry's capacitance with the dielectric present (C) and removed (C_air);
then ε_eff ≡ C/C_air — literally "how much the dielectric actually helped," a
filling factor. A very wide strip buries almost all its field in the substrate:
ε_eff → ε_r. A vanishingly narrow strip splits its field evenly between air above
and dielectric below: ε_eff → (ε_r+1)/2. Every real line sits between.

**Level 2 — why "quasi-TEM" is a legal lie (the first-principles version).** A
strict TEM (transverse electromagnetic — E and H both perpendicular to travel)
wave cannot exist on this structure, and here is the honest argument: a TEM wave's
phase velocity is c/√ε of *its* medium; a wave straddling two media would need two
phase velocities at once. The fields resolve the contradiction by growing small
longitudinal components — the true mode is hybrid. But at frequencies where the
substrate is electrically thin (h ≪ λ — our 0.508 mm board is λ/33 even at
20 GHz), those longitudinal components are second-order small, and the mode
behaves like TEM with the compromise permittivity. That is the quasi-TEM
approximation: not an assumption, a *measured smallness*. It fails gracefully as
f rises — the field retreats into the dielectric, ε_eff creeps upward toward ε_r —
and that creep has a name, dispersion, and a bill, which section 1.4 presents.

The numbers to anchor it, on the board (the course stackup, RO4350B: ε_r = 3.48,
h = 0.508 mm): a 50 Ω line lands at ε_eff = **2.74**. Bounds check: floor
(3.48+1)/2 = 2.24, ceiling 3.48 — it sits where a w/h ≈ 2 strip should, closer to
the ceiling. Hour 3 prints it.

### 1.3 Hammerstad — worked to actual copper (0:20–0:34)

Board work. These are the formulas the homework implements; they go up in full and
they stay up.

History in one breath: Wheeler solved the strip by conformal mapping in 1965;
Hammerstad (1975) and then Hammerstad–Jensen (1980) fitted his maps into
closed-form engineering formulas good to a fraction of a percent. "Hand formula"
here means *a curve fit to an exact field solution* — not a guess.

**Analysis** (geometry → electricals), with u = w/h:

> ε_eff = (ε_r+1)/2 + (ε_r−1)/2 · (1 + 12/u)^(−1/2)
> u ≤ 1: Z₀ = (60/√ε_eff)·ln(8/u + u/4)
> u ≥ 1: Z₀ = 120π / [√ε_eff·(u + 1.393 + 0.667·ln(u + 1.444))]

Read the structure out loud, because it is not arbitrary: the ε_eff formula is the
filling-factor average from 1.2 with a fitted (1+12/u)^(−½) interpolating between
the narrow-strip and wide-strip limits; the narrow-Z₀ formula is a wire over a
plane (hence the logarithm); the wide-Z₀ formula is a parallel-plate capacitor
with a fringing correction bolted on (hence 120π/u leading order).

One correction the real world insists on: our copper is 35 μm thick (1 oz), not
zero. Wheeler's fix — a thick strip behaves like a slightly *wider* thin strip:

> w_eff = w + (t/π)·(1 + ln(2h/t))

On our stackup that is +49 μm — small, but it moves Z₀ by about 1 Ω, and the 2%
referee bar in the homework notices 1 Ω.

**Synthesis** (electricals → geometry) is the direction engineers actually need:
"give me 50 Ω." Two legitimate routes, both blessed for the homework: Pozar's
closed-form A/B inversion formulas, or — the modern move — a numeric root on your
own analysis function: find w such that Z₀(w) = 50. Say it plainly: *root-finding
on a trusted forward model is not cheating; it is how synthesis is actually done
in every tool you will ever use.*

Now work it, on the board, to real copper:

- **RO4350B, 50 Ω:** w = **1.1131 mm** (w/h = 2.19), ε_eff = **2.7361**.
- Guided wavelength at 10 GHz: λ_g = c/(f√ε_eff) = **18.12 mm** — versus 29.98 mm
  in air and 16.07 mm in the bulk dielectric. The compromise, visible.
- Lecture 3's λ/4 transformer, now physical: match the 100 Ω antenna feed through
  Z_T = √(50·100) = 70.71 Ω; that line is **0.582 mm wide** and its quarter-wave
  is **4.63 mm long**. This is the first time this course has quoted a matching
  network in millimeters. It will not be the last.
- **FR-4, same exercise:** w = 0.930 mm, ε_eff = 3.33, λ_g = 16.42 mm. Keep both
  columns on the board — the homework's first prediction question lives in the gap
  between them.

Pre-empt the reflex: *"why is the 70.71 Ω line narrower than the 50 Ω line?"*
Higher impedance = more inductance, less capacitance per meter = a skinnier strip
farther (electrically) from ground. High-Z lines are narrow; low-Z lines are wide;
lecture 9's stepped-impedance filters are exactly this fact used as a design
language.

### 1.4 Dispersion, the cousins, and the substrate market (0:34–0:46)

**Dispersion — when the quasi-TEM lie catches up.** The field retreats into the
substrate as f rises, so ε_eff climbs from its quasi-static value toward ε_r. On
our thin board the climb is mild — 2.71 at 1 GHz, 2.75 at 10 GHz, 2.81 at 20 GHz
(numbers from the Kirschning–Jansen model, which hour 3's referee runs) — and the
quasi-static hand value stays within 1% up to about 13 GHz. That mildness is
*bought by the thin substrate*: h = 0.508 mm keeps the mode quasi-TEM deep into
X-band, and it is precisely why this course's board is a 20-mil core and not a
fat cheap one. Design rule worth writing down: thin boards for high frequency,
and re-evaluate ε_eff at your operating frequency, not at DC — lecture 9 tells
the story of a fabricated filter that landed 4% low because every length was cut
for the DC value.

**The cousins, one slide each.** CPW (coplanar waveguide): the ground comes up
onto the top surface, flanking the signal — ground is always a bond-wire away
(MMICs love it), Z₀ is set by gap-to-width ratio so you get an extra degree of
freedom, and the price is more conductor edge, hence more conductor loss.
Stripline: the trace buried between *two* ground planes — a fully shielded
homogeneous sandwich, genuinely TEM, ε_eff = ε_r with no compromise and no
dispersion of the microstrip kind; the price is that you cannot solder to a
buried layer, so it carries clean routing, not components. Decision in one line:
components on microstrip, dense shielded routing on stripline, MMIC interfaces
on CPW.

**The substrate market.** Two tenants matter to us. FR-4: the epoxy-glass
everything-board — ε_r ≈ 4.4 and *loosely controlled* (±0.2 lot to lot), tan δ ≈
0.02 at 10 GHz. Rogers RO4350B: a ceramic-filled laminate engineered for RF —
ε_r = 3.48 held to ±0.05, tan δ = 0.0037, several times the cost per square inch.
tan δ (loss tangent) is the fraction of stored field energy the dielectric burns
per radian — hold that definition; hour 2 turns it into dB. The teaser number:
at 10 GHz, 30 cm of 50 Ω trace loses **1.5 dB to the dielectric alone on RO4350B —
and 9.0 dB on FR-4.** Hour 2 does the full autopsy.

### 1.5 Hour recap (0:46–0:50)

Four sentences, then break. A 50 Ω trace is geometry: 1.11 mm on this board, and
you can now compute it. The wavelength obeys ε_eff = 2.74 — a filling factor,
not a material — so the λ/4 transformer is 4.63 mm, not 4.02. Quasi-TEM is a lie
that stays within 1% to 13 GHz on a thin board, and dispersion is the lie
unraveling slowly. FR-4 at X-band burns 6× the dielectric loss of Rogers — the
substrate is a component. Hour 2 abandons the board entirely and guides the wave
with an empty pipe.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: the pipe (1:00–1:50)

### 2.1 Why hollow pipes guide (1:00–1:14)

Slide cue: the rectangular waveguide cross-section, a × b, and the TE₁₀ field
pattern — the half-sine of E across the broad wall.

Start with the provocation: remove the center conductor. Lecture 2's line theory
had two conductors carrying opposite currents; a waveguide is one hollow metal
rectangle. No pair of conductors, no TEM mode, no "voltage between them" — and
yet it guides. How?

**Level 1 — the standing-wave count (the fast version).** A metal wall demands
E_tangential = 0. Fit a wave between two walls a apart: the transverse E must be
zero at both, so you must fit *half sine waves* — one, two, three of them. A
half-sine of width a corresponds to a transverse wavelength of 2a, i.e. a
transverse wavenumber k_c = π/a. The total wavenumber k = 2πf/c must supply both
the transverse part and the traveling part:

> β² = k² − k_c², so β = (2π/c)·√(f² − f_c²) with **f_c = c/2a**.

If f > f_c there is wavenumber left over and the wave travels. If f < f_c the
geometry demands more transverse variation than the frequency can pay for; β goes
*imaginary*, e^(−jβz) becomes e^(−κz), and the field dies exponentially — not
absorbed, **refused**. There is no loss mechanism in that statement; the wave is
turned away reactively, like a too-small door. Hour 3 watches this happen in a
simulation with not one lossy element in it.

**Level 2 — separation of variables (the first-principles version, fast).** Solve
the wave equation in the rectangle with E_tan = 0 on all four walls; separation
gives sin(mπx/a)·sin(nπy/b) patterns and the general cutoff

> f_c(m,n) = (c/2)·√((m/a)² + (n/b)²)

— the standing-wave count, now with two indices. The names: TE_mn (transverse
electric — E strictly transverse, some H along the guide) and TM_mn (transverse
magnetic — the reverse). The mode zoo is just this formula's spectrum, and the
fast version was the m=1, n=0 row of it.

### 2.2 TE₁₀ and the catalog (1:14–1:26)

TE₁₀ — one half-sine across the broad wall a, uniform along b — is the **dominant
mode**: lowest cutoff, and for a standard a ≈ 2b guide the next contenders (TE₂₀
at c/a, TE₀₁ at c/2b) arrive together at exactly *twice* f_c. Between f_c and
2f_c the guide is **single-mode**: one field pattern, one β, one well-defined
transmission line. Above 2f_c, two modes carry power at different speeds and your
signal interferes with itself — multimode is not "more capacity," it is chaos.

The catalog, with numbers (say the naming convention: WR = waveguide,
rectangular; the number is the broad wall in hundredths of an inch):

| guide | a (mm) | f_c(TE₁₀) | next mode | vendor band |
|---|---|---|---|---|
| WR-90 | 22.86 | **6.5571 GHz** | 13.114 GHz | 8.2–12.4 GHz |
| WR-75 | 19.05 | **7.8686 GHz** | 15.737 GHz | 10.0–15.0 GHz |
| WR-62 | 15.80 | **9.4878 GHz** | 18.976 GHz | 12.4–18.0 GHz |

f_c = c/2a is exact — the homework checks your cutoffs to four digits against it,
and skrf agrees to every digit it prints. Note the vendor bands: not f_c to 2f_c
but roughly 1.25·f_c to 1.9·f_c. The 25% guard band at the bottom is the subject
of the next section; the guard at the top keeps the second mode's evanescent
tail from waking up at flanges and bends.

The picker question the homework automates: our front-end works at 10 GHz —
which pipe? All three are "single-mode at 10 GHz" by the cutoff arithmetic
(9.4878 < 10 for WR-62, barely). One of them is still a trap.

### 2.3 The ω-β diagram and the price of dispersion (1:26–1:36)

Slide cue: the ω-β diagram — three guide curves rising from their cutoffs,
asymptotic to the straight light line ω = cβ.

Draw it big. Every point's *slope from the origin* is the phase velocity
v_p = ω/β — above c, always, for a waveguide; let the relativity alarm ring and
silence it: phase patterns carry no information. The *local tangent slope* is the
group velocity v_g = dω/dβ = c·√(1−(f_c/f)²) — below c, always, and this is the
speed of energy and information. Their product v_p·v_g = c², a tidy fact worth
memorizing. Near cutoff the curve flattens: energy slows toward zero while the
phase pattern races to infinity. Far above cutoff the curve hugs the light line
and the pipe behaves almost like free space.

Now price it for the homework's 30 cm run, group delay τ = L/v_g at 10 GHz:

- **WR-90:** f/f_c = 1.53 → τ = **1.3254 ns** (light in air: 1.0007 ns).
- **WR-75:** f/f_c = 1.27 → τ = **1.6215 ns**.
- **WR-62:** f/f_c = 1.05 → τ = **3.1674 ns** — 2.4× WR-90.

But the delay is not the crime; the *curvature* is. Across our 200 MHz signal
window the delay itself varies — WR-90 smears the window by **20 ps**, WR-62 by
**583 ps**, a 29× penalty. Half a nanosecond of differential delay across one
pulse is visible distortion in a radar receiver (and by lecture 15, where range
is measured in nanoseconds, it is *range error*). WR-62 at 10 GHz propagates;
it is not usable. "Propagates" and "usable" are different words — the picker
chooses WR-90, and now the 1.25·f_c guard band explains itself: it is the vendor
keeping you off the flat part of the curve.

Pre-empt the misconception, because it is near-universal: *"below cutoff the pipe
absorbs the wave."* No. Below cutoff the pipe *rejects* the wave — β is
imaginary, the field is evanescent, energy is stored and returned, not burned. A
below-cutoff stub of waveguide is a nearly perfect reactance (that is how
waveguide filters get built, lecture 9's cousins). Hour 3's FDTD demo has zero
loss in it and the wave still dies in a centimeter.

### 2.4 The loss shootout (1:36–1:46)

Three ways a planar or guided wave loses power, and their fingerprints:

1. **Conductor loss** — current crowds into a skin depth δ = 1/√(πfμσ); the
   effective sheet resistance R_s = √(πfμρ) grows as **√f**. Microstrip pays it
   over a strip ~1 mm wide with crowded edges (classroom estimate:
   α_c ≈ R_s/(Z₀w)); the waveguide pays it over centimeters of wall. Same
   physics, different denominators.
2. **Dielectric loss** — the substrate burns tan δ of the stored energy per
   radian, so α_d grows as **f** (more radians per meter). The waveguide's
   dielectric is *air*: this line item does not exist for it.
3. **Radiation/surface waves** — the open microstrip's price at high f and at
   discontinuities; the closed pipe's is zero by topology. (One slide of honesty:
   this is also why microstrip measurements never quite match models — the
   homework's Q5 is about exactly this class of gap.)

The shootout, measured, 30 cm at 10 GHz (hour 3 and the homework print this
table):

| medium | conductor | dielectric | total |
|---|---|---|---|
| microstrip, RO4350B | 1.206 dB | 1.488 dB | **2.694 dB** |
| microstrip, FR-4 | 1.44 dB | 9.03 dB | **10.47 dB** |
| WR-90 waveguide | 0.0321 dB | — | **0.0321 dB** |

Read it slowly. The waveguide beats the good board by a factor of **84**. The
cheap board loses **91% of the power** (10.47 dB) in 30 cm — and there is the war
story, told properly: a 10 GHz patch-array prototype, elegant corporate feed
network, gain 4 dB below prediction. Weeks of blaming the patches. The real
culprit: ~40 cm of cumulative FR-4 feed line eating roughly 40% of the transmit
power before any of it reached an antenna. Nobody had priced tan δ = 0.02 at
X-band, because at the 2.4 GHz of their last project the same feed lost a
tolerable fraction. Dielectric loss scales with f; intuition built at WiFi does
not transfer to X-band. The fix was a Rogers respin — the substrate is a
component, and it has a bill.

And the frequency ladder, one line per rung: at 2.4 GHz, FR-4 is fine and nobody
buys waveguide. At 10 GHz, Rogers for the front-end, waveguide for the long
runs and the kilowatts — which is precisely the homework's split verdict, and
why radar transmitters still bolt brass pipes to their dishes (add power
handling: air breakdown in WR-90 is tens of kilowatts, versus a microstrip
edge arcing at tens of watts). At 77 GHz, dielectric loss and every other f-law
have won: transmission lines are millimeters long and the antenna moves onto
the package — lecture 13 lives there.

### 2.5 Hour recap (1:46–1:50)

The pipe guides by fitting half-sines between walls: f_c = c/2a, exact, 6.557 GHz
for WR-90. Below cutoff the wave is refused, not absorbed; above cutoff the guide
is single-mode for one octave, and the vendor band keeps you off the dispersive
knee — WR-62 "works" at 10 GHz and smears a 200 MHz window 29× worse than WR-90.
The loss table says waveguide wins by 84×, FR-4 loses 91% of your power, and the
substrate is a component. Hour 3 makes every one of those numbers print, watches
a wave get refused by a pipe in simulation, and then cuts a transformer to the
wrong length on purpose.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: Hammerstad vs skrf, waveguide dispersion, and a wave refused (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, scikit-rf 1.13.0, and `fdtd 0.3.5 (optional, for cell 3.5)`. Anyone
missing fdtd installs it during the cell (`pip install fdtd` — pure Python, no
compiler) or simply watches 3.5 on the projector; nothing else needs it.

### 3.2 Hammerstad by hand (2:03–2:10)

Cell 3.2: the four functions of hour 1 — thickness correction, ε_eff, Z₀ (both
regimes), and synthesis as `brentq` on the analysis. Then the two boards print:
RO4350B 50 Ω at **1.1131 mm**, ε_eff **2.7361**, λ_g **18.124 mm**; FR-4 at
0.9302 mm, 3.3323, 16.423 mm. Point at ε_eff sitting between (ε_r+1)/2 = 2.24
and 3.48: *the formula is bookkeeping for where the field lives.* This cell is
the homework's module 1, done live at half depth.

### 3.3 The referee: skrf MLine (2:10–2:18)

Cell 3.3: build `skrf.media.MLine` on the same geometry — an independent
implementation carrying *more* physics: Hammerstad–Jensen quasi-static,
Kirschning–Jansen dispersion, finite thickness, loss. Print the comparison: hand
Z₀ = 50.0000 flat; skrf says 49.88 at 1 GHz, 50.12 at 10, 50.88 at 20 — worst
disagreement **1.73%**. Hand ε_eff flat at 2.7361; skrf climbs 2.709 → 2.747 →
2.810 — worst **2.63%**. The syllabus bars are 2% and 3%: *the 1965 hand formula
survives a modern dispersive referee across the entire band this course uses.*
Then the honest read of the plot (saved as `microstrip_referee.png`): the
disagreement is not noise, it is *structure* — the dispersion curve bending away
from the quasi-static line, exactly as hour 1 promised. When two models disagree
with structure, the disagreement is information.

### 3.4 Waveguide dispersion in skrf (2:18–2:25)

Cell 3.4: `skrf.media.RectangularWaveguide` for the three catalog guides.
Cutoffs print — 6.557140, 7.868568, 9.487824 GHz — and skrf's `f_cutoff` agrees
with c/2a to every printed digit (it is the same closed form; *this* referee
checks your algebra, not the physics). The ω-β diagram draws itself
(`omega_beta.png`), and the three 30-cm group delays print: 1.3254, 1.6215,
**3.1674 ns**. Point at WR-62's curve at the 10 GHz line: flattest slope in the
picture. The picker's verdict, on screen: WR-90.

### 3.5 fdtd: a wave refused (2:25–2:33)

Cell 3.5, the demo of the day: a 2D FDTD (finite-difference time-domain — the
same algorithm openEMS runs, in 40 lines of numpy via the `fdtd` package) grid,
WR-90's 22.86 mm between two conducting walls, absorbers at both ends, a line
source inside. Run at 10 GHz: the TE₁₀ pattern marches down the guide. Run at
4.5 GHz — below the 6.557 GHz cutoff: the field *dies within a centimeter* of
the source. Two measurements against theory, printed: the 10 GHz guided
wavelength, FDTD **39.24 mm** vs theory 39.71 mm (1.2%); the below-cutoff decay,
FDTD **100.3 Np/m** vs analytic κ = √(k_c²−k²) = 100.0 Np/m (0.4%). Say the
punchline over the saved figure (`fdtd_cutoff.png`): *there is no lossy material
anywhere in that simulation — the wave below cutoff is refused, not absorbed.*
Maxwell agrees with the boundary-value algebra to half a percent, and you
watched it happen.

### 3.6 The openEMS case study — post-processing a full-wave export (2:33–2:40)

Cell 3.6: openEMS is the instructor-run full-wave solver (students never install
it — course policy). The deliverable that matters is its *export*: a Touchstone
file of the course's 50 Ω line, 30 mm long. This cell loads whatever sits at
`openems_microstrip.s2p` and post-processes it: |S₂₁| → dB/m, and ε_eff
extracted from the S₂₁ phase slope — the same two numbers we have been computing
all day, now from solved fields. Until the instructor's export lands in the lab
folder, the cell builds a **loudly-labeled placeholder** from the skrf MLine
model and runs the identical code path (today it prints: 8.11 dB/m and
ε_eff = 2.744 at 10 GHz from the placeholder's phase). The teaching point is the
pipeline: *field solver → S-parameters → the same scikit-rf post-processing as
any measurement.* When the real file drops in, nothing changes but the numbers —
and where they differ from the models, Q5 of the homework is waiting.

### 3.7 Deliberate bug — the wrong epsilon (2:40–2:44)

Cell 3.7, the bug hour 1 promised: design the homework's 70.71 Ω transformer,
but compute the wavelength with ε_r = 3.48 instead of ε_eff = 2.62. Both lengths
print: **4.0176 mm** (bug) vs **4.6305 mm** (truth) — the real quarter-wave is
1.15× longer than the one the bug would have etched. Nothing crashed; a plausible
millimeter number went to the board house. The autopsy line: the bugged stub is
78.1° at 10 GHz and becomes a quarter-wave at **11.53 GHz** — the match lands 15%
high, and every stub, transformer, and coupled-line resonator in lectures 6–9
dies the same death. ε_eff owns the wavelength; ε_r only owns the board. The
homework toolkit's `quarter_wave` docstring says exactly this, because this bug
is the single most reliable way to fail lecture 9.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. Walk the story — one X-band front-end, a board to
design and a pipe to spec — then the modules and the two commands:

- Module 1 is the core: Hammerstad analysis + synthesis + the physical λ/4 —
  today's cell 3.2 at full depth, refereed by skrf MLine at the 2%/3% bars.
- Module 2 is the picker: cutoffs to four digits against c/2a, β(f), and group
  delay by *numerical* dβ/dω against the analytic form at the 1% bar.
- Module 3 assembles the loss shootout from provided physics — the Np→dB gate is
  yours to get right, and Q4 asks you to defend the 8.686.
- **Predictions come first.** Q1 (the transformer changes boards) and Q2 (the
  pipe that technically works) are answered *before* running — committing to a
  factor is the assignment.
- `--check` prints facts, not PASS/FAIL; `--sweep` draws the two pictures Q2 and
  Q3 are about. Budget ≤ 3 hours. AI use assumed and welcome — you sign the
  width that goes to the board house.

### Wrap-up (2:48–2:50)

Recap against the three claims: 50 Ω is a geometry problem — 1.1131 mm, and skrf
could not catch the hand formula outside 1.73%. The wavelength belongs to
ε_eff — 4.63 mm, not 4.02, and you watched the wrong epsilon ship a 15%-high
match. The pipe guides above c/2a, refuses below it — measured at half a percent
by raw Maxwell — and wins the loss war 84× while WR-62 shows that "propagates"
and "usable" are different words. Teaser: next lecture the λ/4 transformer we
just cut in copper gets promoted — multiple sections, Chebyshev ripple, and the
Bode–Fano theorem that tells your boss the spec is physically impossible.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 2 (*Transmission Lines*), chs. 4–5
  (planar lines; extraordinary effects) — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 3 (for owners of the book — the
  waveguide boundary-value problems this lecture compresses, and §3.8's microstrip
  formulas, which the homework implements).
- Wheeler, "Transmission-Line Properties of Parallel Strips Separated by a
  Dielectric Sheet," *IEEE Trans. Microwave Theory Tech.* MTT-13, 1965 — the
  conformal-mapping solution behind every microstrip formula in this lecture.
- [R37] scikit-rf documentation — `skrf.media.MLine` and
  `skrf.media.RectangularWaveguide`, this week's referees:
  https://scikit-rf.readthedocs.io/
- openEMS documentation (instructor-demo context only; students post-process
  exports, never install): https://docs.openems.de/
