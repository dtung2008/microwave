# Lecture 13 — Antennas & Arrays

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (the course venv from lecture 1: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**; nothing new this week)
**Prerequisites:** lectures 1–12 — specifically lecture 1's Friis formula and course
radar, lectures 2–3's Γ and matching (the antenna's circuit face), and any prior
contact with the DFT (the taper section is a homecoming for it).
**Pre-class setup:** run `lab/setup_check.py` — it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the antenna as a transducer (0:00–0:50)

### 1.1 The debt this lecture pays (0:00–0:08)

Slide cue: the course radar's block diagram from lecture 1, every box now familiar
except one — the antenna, still stamped "33 dBi", still unexplained.

Open with the ledger. For twelve lectures this course has carried a debt: lecture 1
wrote `G = 33 dBi` into the radar equation and promised that lecture 13 would say
what G *is*. Between then and now you built everything that feeds the antenna —
lines, matches, filters, the receiver — and treated the antenna itself as a gain
number attached to a port. Today the port grows a far field.

Three claims for today — write them on the board and leave them up:

1. **The antenna is a transducer with two faces.** To the circuit it is an
   impedance — lecture 2's Z_L, lecture 3's match. To space it is a pattern. One
   device, two descriptions, and the course's two halves meet inside it.
2. **Gain is geometry, not amplification.** An antenna is passive; it adds no
   energy. G says only how hard the energy is *concentrated* — and A_e = Gλ²/4π
   finally closes the loop Friis opened in lecture 1.
3. **An array turns geometry into arithmetic.** The array factor is a ten-line sum,
   and everything a phased array does — beamwidth, sidelobes, grating lobes,
   steering — is already inside that sum. Hour 2 derives it twice; hour 3 types it.

Pre-empt the wireless students' question: *"we did antennas in comms — is this
review?"* Partly, and on purpose: parameters and Friis are shared ground. But comms
courses stop at the gain number; today's second hour lives where radar and 5G
actually work — amplitude tapers, grating lobes, scan loss — and homework 13 hands
you the two-target scene where those details decide whether a drone exists.

### 1.2 Pattern, directivity, gain — the far-field picture (0:08–0:22)

Slide cue: the far-field picture — a small radiator, expanding spherical phase
fronts, and the pattern as a plot of power density versus direction at fixed large R.

Set the stage honestly: close to any antenna the fields are a complicated storage
swirl (that is where the reactance in Z_A lives); far away — beyond roughly
2D²/λ for an antenna of size D — the wave is locally plane, the angular shape stops
changing with distance, and *that stable angular shape is the pattern*. Everything
today happens in the far field. For our 24 cm array at 10 GHz, 2D²/λ ≈ 3.8 m: an
anechoic chamber away, not a special place.

Definitions, built in the order each needs the last:

- **Pattern** F(θ, φ): received/radiated power density versus direction, normalized
  to its own maximum. We plot it in dB and read three features all day: the main
  lobe, its −3 dB width (**HPBW — half-power beamwidth**), and the sidelobes.
- **Directivity** D = (peak density)/(average density over the sphere) = 4π/Ω_A,
  where Ω_A is the beam solid angle. A perfectly even radiator has D = 1; every
  real one concentrates.
- **Gain** G = e·D with e the radiation efficiency (ohmic and dielectric loss —
  the FR-4 patch-array war story from lecture 5 was an efficiency story). For the
  clean metal structures of radar, e is 0.7–0.95; today we mostly say G ≈ D and
  flag it whenever it matters.
- **Polarization**: the far field is a transverse vector; the receive antenna
  projects onto its own vector. Matched: 0 dB. Orthogonal: −∞ in theory, −20 to
  −30 dB in hardware. Circular against linear: −3 dB, always.

War story, 60 seconds: a range test that "lost" 3 dB everywhere, for a week —
every cable swapped, every connector torqued twice. The transmit horn was linear;
the device under test was circularly polarized. Nobody had written the polarization
on the test plan, because polarization is invisible on a spectrum analyzer. The
−3 dB was physics, purchased at the whiteboard, findable only there.

Pre-empt the misconception now, because dBi plants it: *"a 33 dBi antenna makes the
signal 2000× stronger — like an amplifier?"* No. Passive. It takes the same total
watts and shoves them into a 4.5° cone instead of a sphere. Point the cone
elsewhere and the "gain" is negative. An amplifier is generous; an antenna is
merely *opinionated*. (This is why G multiplies both ways in the radar equation —
the opinion works in receive too.)

### 1.3 Effective aperture, and Friis closes its loop (0:22–0:32)

The receive-side description: an antenna presents an **effective aperture** A_e —
the area from which it collects an incident plane wave's power, P_r = S·A_e. The
relation lecture 1 borrowed and today owns:

> A_e = G λ² / 4π

Where it comes from, in outline (the full derivation is Orfanidis [R4] ch. 15, and
it is assigned reading, not board work): reciprocity forces the ratio A_e/G to be
the same *universal constant* for every antenna — receive and transmit are the same
physics run backwards, so no antenna can be relatively better at one than the
other. Evaluate the constant once, for any antenna you can solve exactly (the short
dipole, or thermodynamic equilibrium in a cavity), and λ²/4π falls out. The number:
at 10 GHz, an isotropic antenna's aperture is λ²/4π = 0.715 cm² — space hands every
antenna a free λ-sized catch basin, which is precisely why lecture 1's λ² sat in
the *aperture*, not in the medium.

Two conversions to make reflex, both used in hour 2's sizing:

- G = 4π A_e/λ²: the course dish's 33 dBi ↔ A_e = 0.143 m² — a 43 cm circle. The
  dish on the roof is about that size plus illumination loss. Numbers cohere.
- **Beamwidth ≈ λ/D** for an aperture of size D (radians, to sizing accuracy).
  Directivity, aperture, and beamwidth are one fact in three currencies:
  concentrating into θ ≈ λ/D needs D ≈ 4π/θ² ≈ 4π(D/λ)². Hold this; the drone
  question at the end of hour 2 is one division using it.

And with A_e in hand, say the Friis sentence that lecture 1 owed you: *received
power is transmitted density times receive aperture; density carries G_t and the
spreading, aperture carries G_r and the λ² — the formula was never anything but
those two factors.* The loop is closed; every symbol in P_r = P_tG_tG_rλ²/(4πR)²
now has an owner.

### 1.4 The workhorse elements — data points, not derivations (0:32–0:45)

Slide cue: three elements with their numbers — dipole, patch, horn.

Deliberately fast. Deriving element patterns needs the vector potential, and this
course spends its hours elsewhere — Orfanidis [R4] chs. 15–17 has every integral
for the curious. What an engineer must carry is each element's *data sheet*:

- **The half-wave dipole** — the reference element. Length λ/2 (15 mm at 10 GHz),
  input resistance ≈ 73 Ω at resonance (now you know why 75 Ω cable exists),
  gain 2.15 dBi, donut pattern, bandwidth ~10%. "dBd" on a datasheet is gain
  relative to this element: dBd + 2.15 = dBi.
- **The microstrip patch** — lecture 5's stackup grows a radiator. The resonant-
  length story: a patch is a λ/2-in-dielectric resonator whose two open edges leak,
  in phase, broadside — an accidental two-element array. Design formulas (provided,
  Hammerstad-style, in the slide notes): on RO4350B (ε_r = 3.66, h = 0.508 mm) a
  10 GHz patch measures **9.82 mm wide × 7.68 mm long** — the length is 0.256 λ₀,
  visibly less than λ/2 because ε_eff = 3.37 shortens the wave and fringing
  (ΔL = 0.24 mm per edge) shortens the copper. Gain ~6 dBi, bandwidth a few
  percent — cheap, flat, printable by the thousand: the array element of choice.
- **The horn** — a waveguide (lecture 5) flared until its mouth is an aperture.
  Gain 10–25 dBi by size, wideband, calculable to fractions of a dB — which is why
  the *standard-gain horn* is what every antenna range measures against.

The theme to say out loud: elements are 2–8 dBi devices. Nobody makes a 33 dBi
*element* — high gain means a big aperture, and big apertures are built by
*replication*, not by heroic single radiators. Which is the cue for hour 2.

### 1.5 Hour recap (0:45–0:50)

Three sentences, then break: the antenna is one device with two faces — impedance
to the circuit, pattern to space — and gain is concentration, never amplification;
A_e = Gλ²/4π closes Friis's loop and converts among gain, aperture, and beamwidth ≈
λ/D; elements are single-digit-dBi parts, so every serious aperture is a *team* of
them. Hour 2 is about the team.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: arrays — the main event (1:00–1:50)

### 2.1 The array factor, derived twice (1:00–1:12)

The setup, drawn carefully because every formula today lives on this drawing: N
identical elements on a line, spacing d, element n at x = n·d. A plane wave arrives
from angle θ measured *from broadside* (the array's perpendicular — our convention
all course, matching the homework). The wave reaches element n early by a path
n·d·sin θ, which is a phase ψ·n with

> ψ = k d sin θ,  k = 2π/λ.

Sum the element voltages with complex weights w_n:

> AF(θ) = Σₙ wₙ e^{jnψ} — the **array factor (AF)**. That is the whole theory.

**Level 1 — the geometric series (the fast derivation).** Uniform weights, wₙ = 1:
the sum is a geometric series, and

> |AF| = |sin(Nψ/2) / sin(ψ/2)|

Peak N at ψ = 0 (broadside: all paths equal). Nulls where the numerator zeroes:
ψ = 2πm/N. Everything in 2.2 falls out of this closed form — and it is also the
homework checker's referee, which is why the homework forbids it *inside* your
measurement code.

**Level 2 — phasor spokes (the first-principles picture).** Slide cue: the phasor
fan. Draw N unit phasors head-to-tail. At broadside they are collinear: length N.
Off broadside each rotates ψ more than its neighbor; the chain curls. When the
chain curls into one full closed circle — total wrap Nψ = 2π — the sum is *zero*:
first null. Curl it another half turn and the chain wraps 1.5 circles: the phasors
partially re-align and the sum grows again — *that is a sidelobe*, and its size is
roughly the diameter of a circle whose circumference is 2N/3 of the chain:
2/(3π) ≈ −13.5 dB. The exact number arrives in a minute, but notice what the
picture already gave: nulls are *complete wraps*, sidelobes are *extra half-wraps*,
and no taper has been mentioned because none exists yet. When a student asks in
week 15 "why does my FFT leak," this is the same picture with ψ renamed.

### 2.2 Anatomy of the uniform beam — every feature a number (1:12–1:22)

Now read the closed form onto the course array — N = 16, d = λ/2 = 14.99 mm,
10 GHz — and turn every feature into the number hour 3 prints:

- **First null:** Nψ/2 = π → sin θ = λ/(Nd) → θ = asin(2/16) = **7.181°**. The
  aperture is Nd = 24 cm; λ/(aperture) in radians — beamwidth is λ over size,
  exactly the hour-1 currency.
- **HPBW:** solve |AF|² = N²/2: **6.348°** closed form; the sampled pattern will
  measure 6.359°. (Small-angle version 0.886·λ/(Nd) = 6.346° — three digits of
  agreement between three routes; this is what "understood" looks like.)
- **First sidelobe:** the sinc envelope says sin(x)/x at its first extremum:
  **−13.26 dB**. The *finite* array says −13.15 dB at N = 16 — the denominator
  N·sin(ψ/2) is smaller than the sinc's Nψ/2 there, lifting the lobe +0.11 dB.
  Both numbers are honest; they answer different questions (limit vs hardware).
  Homework Q4 makes you defend which one goes in a design review.

Pre-empt the question the −13 number always raises: *"can we fix the sidelobes by
adding elements?"* No — try it on the closed form: N changes the sidelobe *count*
and the beamwidth, but the first sidelobe stays pinned near −13 dB for any uniform
array. Sidelobe level is set by the *shape* of the weights, not the size of the
array. That is section 2.4's job.

And the claim that makes sidelobes matter at all, planted now for the homework:
sidelobes are where *other targets* leak in. A −13 dB floor means any echo 13 dB
stronger than your target, anywhere in the sky, competes with it. Lecture 1 priced
the drone's echo at 17.8 dB below an airliner's. Hold those two numbers next to
each other for twenty minutes.

### 2.3 Grating lobes — the d > λ/2 crime (1:22–1:30)

Slide cue: the visible-window picture — |AF| periodic in ψ with period 2π, and the
visible sky |sin θ| ≤ 1 as a window of width 4πd/λ sliding over it.

The AF is periodic: ψ → ψ + 2π reproduces it exactly, because a phase of 2π per
element is invisible to a sampled wave. Those replicas are harmless while they sit
outside the **visible window** ψ ∈ [−kd, +kd]. Widen d and the window widens; at
d > λ/2 (window wider than 2π) a *full replica of the main beam* can enter the sky:
a **grating lobe** — same height, wrong direction. This is spatial aliasing:
elements sample the wavefront, d > λ/2 is under-sampling, and the grating lobe is
the alias. (DSP students: yes, exactly Nyquist. Say so.)

Steered arrays make it worse. Steering to θ₀ moves the main beam to sin θ = sin θ₀;
the nearest replica sits at

> sin θ_g = sin θ₀ − λ/d,

visible as soon as that number reaches −1. The safe-spacing budget follows:

> d < λ / (1 + |sin θ₀|) — scan to ±90° and you are back at λ/2; scan to ±45° and
> d_max = 0.586 λ = **17.56 mm** for the course array.

The numbers hour 3 animates: at d = 0.65λ, onset is at scan **32.6°**; steered to
45°, the grating lobe stands at **−56.24°**, at **full height** — the array
genuinely cannot tell −56° from +45°. War story, 60 seconds: a harbor-surveillance
array, spacing opened past λ/2 to stretch aperture on a fixed element budget,
commissioning at boresight flawless. Weeks later, night shift: an inbound contact
at −55° with nothing on the camera. The ferry at +45° was the contact; the array
was reporting its alias. The fix was not software — you cannot filter an alias
after sampling — it was masts moved 3 mm each. Sampling theorems collect in copper.

Then the honest engineering coda: designers *do* commit the crime deliberately —
when the scan sector is narrow (the budget formula with small θ₀), or when the
element pattern (2.5's pattern multiplication) is trusted to sit on the grating
angle. Automotive radars do it every day. The crime is not d > λ/2; it is doing it
*without the budget line*.

### 2.4 Tapers are windows — the DSP homecoming (1:30–1:38)

Look at the array factor again: Σ wₙ e^{jnψ}. Say it slowly: *the array factor is
the DFT of the weight vector.* Not "analogous to" — is. Hour 3 proves it with one
`np.fft.fft` call agreeing to 4.5×10⁻¹⁴. Everything your signals course knew about
windows transfers wholesale: uniform weights = rectangular window = −13 dB leakage;
sidelobes = spectral leakage in space; tapering the aperture = windowing the data.
Two communities, one mathematics, met in an antenna.

So shop for windows:

- **Raised cosine (Hann)**, the DSP reflex: at N = 16, sidelobes fall to −31.5 dB —
  but HPBW pays ×1.53.
- **Chebyshev** — the optimal shopper. Dolph's 1946 result: for a specified
  sidelobe level, the Chebyshev weights give the *narrowest possible* main lobe,
  and all sidelobes sit at exactly the specified level — equal ripple (lecture 8's
  Chebyshev filters, same polynomial, same bargain). At −30 dB, N = 16:
  HPBW ×**1.2550**, directivity −**0.65 dB**. Compare the Hann line: 1.5 dB *more*
  quiet than Hann for a *third* of Hann's extra broadening. In scipy it is one
  call — `scipy.signal.windows.chebwin(16, at=30)` — and its equal-ripple floor is
  the homework's second referee.

The trade stated as economics, because that is how array engineers talk: 17 dB of
sidelobe quiet costs 26% of beamwidth and 0.65 dB of gain. Cheap. That asymmetry —
sidelobes are cheap, beamwidth is precious — is why fielded radars almost never fly
uniform. And the payoff line for the homework, delivered with the two numbers from
2.2 still on the board: against a −13 dB floor, a −17.8 dB drone echo is *below the
floor*; against a −30 dB floor it is 12 dB proud. The taper is not cosmetic. It is
the difference between a detection and nothing.

### 2.5 Steering, scan loss, and pattern multiplication (1:38–1:45)

**Steering is linear phase.** Give element n the phase −k·d·n·sin θ₀ and the ψ in
every formula becomes k d(sin θ − sin θ₀): the entire anatomy — beam, nulls,
sidelobes — translates to sit on θ₀. No motors. Microseconds. This is the phased
array, and lecture 16 will do it with received snapshots in software.

What the scan costs, because nothing is free:

- **Broadening:** the aperture *foreshortens* — seen from 45°, 24 cm projects to
  24·cos 45° = 17 cm, so the beam widens ≈ 1/cos θ₀. Measured: 6.359° → **9.025°**,
  ×**1.4194** (the exact arcsin form runs slightly past 1/cos's 1.4142 — the two
  beam edges do not foreshorten equally; the checker referees with the exact form).
- **Scan loss:** the same foreshortening shrinks effective aperture, so gain falls
  ≈ cos θ₀ (−1.5 dB at 45°) — before the element pattern adds its own droop.
- **Grating exposure:** 2.3's budget, now with sin θ₀ spent.

**Pattern multiplication**, the principle that assembles everything: real elements
are not isotropic, and for identical elements the total pattern *factors*:

> E_total(θ) = E_element(θ) × AF(θ).

The element is a slow envelope (patches: broad, ~cos θ); the AF is the fast
structure. This is why grating-lobe sinners survive — the element envelope
multiplies the alias down — and why arrays of arrays work: a row of 16 becomes the
"element" of a column of 16, and the planar pattern is the product. One principle,
three uses, zero new mathematics.

### 2.6 Sizing the aperture — the drone question (1:45–1:48)

The worked example the whole hour was aimed at, done in four board lines. Two
drones fly 100 m apart at 5 km. Separating them needs beamwidth < 100/5000 =
0.02 rad = 1.146°.

- Our 16-element array: HPBW 6.36° → separates them only inside **901 m**.
- Required aperture: D ≈ λ/θ = 3 cm/0.02 = **1.5 m** — at λ/2 pitch, a planar
  sheet of ~100 × 100 = **10⁴ elements** (D ≈ π·N·M → ~45 dBi).
- The course dish? 33 dBi → beam ≈ 4.5° → separates only inside 1.26 km. **No.**

Say the moral plainly: lecture 1 bought *detection* — 33 dBi closes the drone's
link at 4.11 km. Today's currency is *resolution*, priced in beamwidths, and the
same 33 dBi cannot pay. Detection asks "is something there"; resolution asks "is it
one thing or two" — different questions, different apertures, and the second one is
why drone-hunting radars are large even when their link budgets close with margin.
(The 16-element row's 12.04 dBi vs the dish's 33: one line — π·16·16 → 29 dBi says
a 16×16 sheet nearly matches the dish; ~635 elements actually match it. The full
sheet is lecture 16's hardware.)

### 2.7 Hour recap (1:48–1:50)

The array factor is a DFT with ψ = kd sin θ, and its anatomy is three numbers you
now own: 6.35°, −13 dB, and null-at-λ/Nd; spacing past λ/(1+|sin θ₀|) buys aliases
at full height; tapers are windows — 17 dB of quiet for 26% of beamwidth — and
steering is linear phase that pays 1/cos θ₀. Hour 3 types all of it, then feeds
`np.sin` degrees and watches a 16-element radar grow 57 beams.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the array factor engine, live (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.1, matplotlib
3.10.x, scikit-rf 1.13.0. Nothing new installs this week; anyone whose
`setup_check.py` failed pre-class pairs up now.

### 3.2 The engine, in ten lines (2:03–2:12)

Cell 3.2: type `af()` live — weights in, angles in, complex sum out; the only
physics is `psi = k*d*np.sin(np.radians(theta))`. Point at `np.radians` and say
*this call is load-bearing; cell 3.7 removes it*. Then the uniform 16-element
pattern, measured by a `stats()` helper that hunts the peak, the −3 dB edges, and
the sidelobes from samples: |AF|max = 16.0 at 0.000°, first null 7.181° (formula
agrees to the printed digit), HPBW 6.359° vs closed form 6.346° (small-angle), SLL
−13.1468 dB. Every number from section 2.2, out of a for-loop instead of a formula
— *two witnesses, no shared assumptions*, which is exactly the homework's module-1
design.

### 3.3 The homecoming, proved (2:12–2:20)

Cell 3.3: `np.fft.fft(np.ones(16), 4096)` against the AF sampled in ψ — max
difference **4.5×10⁻¹⁴**. The array factor *is* the DFT; applause optional. Then
`chebwin(16, at=30)`: SLL prints −30.0000 dB — equal ripple, as purchased — and
HPBW 7.979°, cost ×1.2548. (A scipy `UserWarning` about spectral analysis is
filtered at the top of the file, with a comment explaining why it does not apply to
pointing antennas — read the comment aloud; silencing warnings *with a reason* is
engineering, silencing them without one is negligence.)

### 3.4 Steering (2:20–2:26)

Cell 3.4: the linear-phase loop — steer to 0°, 25°, 45°. Peaks land at +0.000,
+25.000, +45.000; HPBW walks 6.359 → 7.020 → 9.026°; broadening ×1.419 with 1/cos
45° = 1.414 printed beside it; worst lobe holds at −13.15 dB at every angle — at
d = λ/2 the scan is *clean*. Say the foreshortening sentence while the loop runs:
seen from 45°, the 24 cm array looks 17 cm wide.

### 3.5 The crime, animated (2:26–2:34)

Cell 3.5: open the spacing to 0.65λ and scan 0° → 45° in six frames
(`hour3_grating.png`). Predicted onset asin(λ/d − 1) = 32.58°. The far-lobe
readout: −19.8 dB at scan 0, −17.6 at 15, **−2.4 dB at scan 30** — the horizon
glows *before* the formal onset, because the replica's skirt pokes in ahead of its
peak — then 0.00 dB from 33° on. At scan 45: grating lobe measured at −56.238° vs
formula −56.238°, full height. Close with the no-crime budget: d < 0.586λ for a
45° sector.

### 3.6 Sizing, and the tie-back (2:34–2:39)

Cell 3.6: the drone question in five prints — 1.146°, D ≈ 1.50 m, the 16-element
row separates only inside 901 m; then the lecture-1 ledger: this row is 12.04 dBi,
the dish was 33 dBi, a 16×16 sheet reaches ≈29 dBi (π·N·M), and matching the dish
wants ~635 elements. One radar, three apertures, all priced in the same two
currencies.

### 3.7 Deliberate bug — degrees into np.sin (2:39–2:44)

Cell 3.7, the bug hour 2 promised: rebuild the pattern with `np.sin(TH)` — TH in
*degrees* — and plot it next to the truth (`hour3_bug.png`). It does not crash. It
is not ugly. It is a gorgeous comb of **57 full-height beams** — a plausible
exotic array, the kind of plot that gets pasted into a slide deck at 11 p.m. Then
the measurement: peak spacing **3.1416°**. Let the class say it: *that is π.* A
period of exactly π on a degrees axis is the fingerprint — `sin(θ_deg)` repeats
every π *units*, and every repeat manufactures a fake broadside. The habit that
prevents it is lecture 1's habit wearing angle units: `theta_deg` and `theta_rad`
are different quantities, and the name is the type checker. The homework starter
names every angle; keep it that way.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. Walk the story — the course radar grows a 16-element
array; an airliner at 10 km, the drone at 3.5 km and 15° off, echo 17.8 dB down —
then the modules and the two commands:

- Module 1 is the core: the AF engine plus `pattern_stats`, which must *measure*
  the pattern (peak, −3 dB edges, sidelobe hunt) with no closed forms inside — the
  closed forms are the checker's referees, not yours. Modules 2 (taper study) and
  3 (steering) run on your engine.
- **Predictions come first.** Q1 (the Chebyshev broadening factor) and Q2 (what
  steering costs, and where the grating lobe lands) are answered *before* running —
  committing to a number is the assignment.
- `--check` prints facts, not PASS/FAIL — beamwidth vs closed form, SLL vs the
  exact finite-N referee, the chebwin guarantee, the grating angle to 0.1°.
  `--plot` makes the four pictures ANSWERS.md interrogates, including the
  two-target overlay where one taper reveals the drone and one buries it.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: the antenna has two faces, and you can now convert
among gain, aperture, and beamwidth in one line; gain is concentration — 33 dBi is
a 4.5° opinion, not free energy; and the array factor turned geometry into a DFT —
beamwidth 6.36°, sidelobes −13 dB until you pay 26% of beamwidth to buy −30, full-
height aliases past λ/(1+sin θ₀), all of it steered by phase alone. Teaser: next
lecture the antenna meets the statistics — the radar equation gets its honest
P_d/P_fa mathematics, the 13 dB placeholder dies, and you find out what CFAR does
when the drone flies next to a clutter edge.

---

## References

- [R4] Orfanidis, *Electromagnetic Waves and Antennas* — chs. 15 (antenna
  parameters, A_e = Gλ²/4π), 19–20 (arrays, Dolph–Chebyshev) — free:
  https://www.ece.rutgers.edu/~orfanidi/ewa/
- [R2] Steer, *Microwave and RF Design*, Vol. 1 (*Radio Systems*), antennas & RF
  link chapter — free: https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 14.1–14.3 (for owners of the book).
- [R11] Balanis, *Antenna Theory: Analysis and Design* 4e, ch. 6 (arrays) —
  reference; the closed-form beamwidth the checker uses is its eq. 6-22 lineage.
- [R31] MIT Lincoln Laboratory, *Introduction to Radar Systems*, antenna lecture —
  free: https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/
