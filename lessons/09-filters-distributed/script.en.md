# Lecture 9 — Filters II: Distributed Realizations

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (the course venv from lecture 1: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1–8 — this is the week the investments pay out:
ABCD cascades (L4), microstrip and ε_eff (L5), even/odd-mode analysis (L7),
and the insertion-loss method with its g-values (L8). Students shaky on
even/odd should re-skim L7's hour 1 before class.
**Pre-class setup:** the course venv, then `lab/setup_check.py` — it must print
`SETUP OK`.

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: from coils to copper — Richards and Kuroda (0:00–0:50)

### 1.1 Why last week's filter cannot be bought (0:00–0:08)

Slide cue: hw8's bandpass ladder, redrawn with its element values at 2.4 GHz.

Open with the arithmetic, not the philosophy. Take homework 8's synthesis
machine — the one you own now — and point it at 2.4 GHz instead of 60 MHz:
N=3 Chebyshev, 0.5 dB, 10% bandwidth. The first series branch comes out as
**52.93 nH in series with 0.0831 pF**. Say what those numbers mean at
2.4 GHz: a 53 nH coil is many turns of wire, several millimeters of it, with
interwinding capacitance that makes it self-resonate *below* 2.4 GHz — above
self-resonance an "inductor" is a capacitor. And 0.083 pF is smaller than the
parasitic capacitance of the pads you would solder it to. The insertion-loss
*method* survives at microwave; the component catalog does not.

What does exist at 2.4 GHz, in unlimited supply and at zero unit cost, is
**printed transmission line** — lecture 5 taught you to cut it to any Z₀ from
roughly 20 to 120 Ω. This lecture is one long translation exercise: the same
g-values, realized in copper. Three claims for today, on the board:

1. **One tangent is the whole theory.** Richards' transformation, Ω = tan(βl),
   turns a network of equal-length lines into a lumped filter on a warped
   frequency axis — *exactly*, not approximately. Today's stub filter lands on
   the Chebyshev closed form to 3×10⁻¹⁴ dB.
2. **Kuroda is an identity, not an approximation.** It converts the stubs you
   cannot build into ones you can, and the checker measures the equivalence at
   7×10⁻¹⁶ — machine epsilon, at every frequency.
3. **Distributed filters are periodic.** tan repeats; therefore your filter
   repeats. Every commensurate filter has a second life — a *reentrant
   passband* — and this week you predict where it lands before you sweep.
   Ignoring claim 3 is how filters "pass" bench tests and fail in the field.

### 1.2 Richards' transformation — derived twice (0:08–0:20)

**Level 1 — the fast version: substitute and see.** Lecture 2 gave the input
impedance of stubs. A short-circuited stub of characteristic impedance Z and
electrical length θ = βl presents Z_in = jZ·tan θ; an open-circuited stub
presents Z_in = −jZ·cot θ = Z/(j tan θ). Now stare at the lumped catalog: an
inductor is Z_L = jωL, a capacitor is Y_C = jωC. Define the **Richards
frequency**

> Ω = tan θ = tan(βl)

and the stubs *are* the lumped elements with ω → Ω: a series short-circuited
stub of impedance Z = L is an inductor of reactance ΩL; a shunt open stub of
impedance Z = 1/C is a capacitor of susceptance ΩC. Every ladder network of
Ls and Cs maps element-for-element into a network of stubs — same topology,
same g-values, same transfer function *in Ω*.

**Level 2 — the first-principles version, framed as explaining the first.**
Why does the whole *response* map, not just element impedances at one
frequency? Because of the commensurate-network fact: if every line in a
network has the **same** electrical length θ (the lines are *commensurate*),
then every S-parameter of the network is a rational function of the single
variable t = j·tan θ. (Sketch the argument: each line's ABCD matrix is
cos θ·[[1, jZ tanθ],[j tanθ/Z, 1]] — polynomial in tan θ — and cascades and
terminations preserve rationality.) So a commensurate distributed network has
*exactly* the mathematics of a lumped network in the variable Ω. Synthesis
theory transfers wholesale; the only price is the axis: Ω is a *warped* copy
of ω, and it warps periodically. That price has a name — section 2.3 — and it
never goes away.

**The calibration choice.** The prototype's band edge lives at Ω = 1, so
choose the common length to make tan θ = 1 at your cutoff: **θ(f_c) = 45°,
i.e. every element is λ/8 at f_c.** Then the mapping table (hour 3 prints it):
Ω(0) = 0 — DC is DC; Ω(f_c) = 1 — the band edge lands exactly; Ω(2f_c) = ∞ —
*infinite* prototype frequency at a finite real frequency, an attenuation pole
at 6 GHz for a 3 GHz design; Ω(3f_c) = −1 — the band edge *again*; Ω(4f_c) =
0 — "DC" again, the filter has forgotten everything.

Pre-empt the question a sharp student will ask: *"tan is negative between
2f_c and 4f_c — what is a negative frequency doing in my filter?"* Answer:
the attenuation depends on |Ω| for these all-pole responses (Chebyshev
polynomials are even or odd), so the response between 2f_c and 4f_c is a
mirror image of the response from ∞ back down to DC. That mirror is exactly
how the second passband walks back in.

### 1.3 Kuroda's identities — making the unbuildable buildable (0:20–0:32)

Richards hands the N=3 ladder to the layout engineer as: **series short stub,
shunt open stub, series short stub.** The layout engineer hands it back. Two
reasons, both physical:

- A **series stub in microstrip does not exist.** A series element interrupts
  the signal conductor; a series *stub* would need that interruption to run
  off sideways and then short to ground — while the ground plane runs
  unbroken underneath. There is no way to draw it. (Coax and coplanar
  structures have their own versions of this refusal.)
- Even the buildable shunt stubs have a problem: Richards put all three
  elements **at the same point**. Three stubs sprouting from one junction
  couple to each other and turn the junction into an un-modeled blob.

Enter the **unit element** (UE): a transmission line of the same commensurate
length θ, impedance of our choosing. Its ABCD is cos θ·[[1, jZ tan θ],
[j tan θ/Z, 1]]. Two facts: first, a UE whose impedance equals the port
impedance, added at the source or load, changes *nothing* about |S21| — a
matched line only adds phase. Second — this is Kuroda's discovery — a UE lets
a stub **tunnel through it and change species**.

**The derivation (first-principles, on the board — it is six lines).**
Multiply UE(Z₁) by a series short stub Z₂ (write t for tan θ):

> UE·SS = cos θ · [[1, jt(Z₁+Z₂)], [jt/Z₁, 1 − t²Z₂/Z₁]]

Multiply a shunt open stub Ẑ₂ by UE(Ẑ₁):

> Sh·UE = cos θ · [[1, jtẐ₁], [jt(1/Ẑ₁ + 1/Ẑ₂), 1 − t²Ẑ₁/Ẑ₂]]

Match entries: Ẑ₁ = Z₁ + Z₂, Ẑ₂ = Z₁(Z₁+Z₂)/Z₂ — and check the (2,1) entry
closes: 1/(Z₁+Z₂) + Z₂/(Z₁(Z₁+Z₂)) = 1/Z₁. It does. Boxed:

> **UE(Z₁) + series short stub(Z₂) = shunt open stub(Z₁(Z₁+Z₂)/Z₂) + UE(Z₁+Z₂)**
> With n² = 1 + Z₂/Z₁: both new impedances are the old ones scaled by n².

**The fast version, framed as a sanity check of the slow one:** let θ → 0.
The left side is a short line (≈ nothing) plus a small series inductance
Z₂·θ; the right side is a small shunt capacitance θ/Ẑ₂ plus a short line. An
L trades for a C? At DC both vanish — and at any low frequency the two
networks differ only at second order in θ, exactly as the matrix identity
demands once you expand it. The identity is *exact at all θ*; the low-θ limit
just makes it believable.

State the family honestly: there are **four Kuroda identities**. The two
transformer-free ones swap a series short stub across a UE for a shunt open
stub (derived above) and the reverse (same algebra, run backward). The other
two swap open↔short stub species at the price of an **ideal n²:1
transformer** — stated for completeness (Pozar Table 8.7); microwave practice
leans almost entirely on the first two, because ideal transformers are just
another component you cannot buy.

War story, 45 seconds: a student tapes out the Richards network *without*
Kuroda by "approximating" the series stub as a thin meandered gap in the
line. The gap is a series C, not a series shorted stub — wrong element
entirely — and the filter that comes back is a coupler nobody ordered.
Kuroda is not bureaucracy; it is the difference between a filter and abstract
art.

### 1.4 The stub lowpass, worked to copper numbers (0:32–0:45)

Board work — the homework's module 1, done live. Spec: N=3 Chebyshev, 0.5 dB
ripple, f_c = 3 GHz, 50 Ω. From hw8's engine: g = [1.5963, 1.0967, 1.5963, 1].

1. **Prototype, series-L first:** L = 1.5963, C = 1.0967, L = 1.5963.
2. **Richards:** series short stub Z = 1.5963 | shunt open stub Z = 1/1.0967
   = 0.9118 | series short stub Z = 1.5963. (Normalized; all λ/8 at 3 GHz.)
3. **Add UE(1) at each end** — free, they match the ports.
4. **Kuroda once per end** (Z₁ = 1, Z₂ = 1.5963, n² = 2.5963): the series
   stub becomes a shunt stub of (1+g₁)/g₁ = 1.6265 behind a UE of 1+g₁ =
   2.5963. By symmetry the load side mirrors.
5. **Scale by 50 Ω:** shunt open **81.32 Ω** | line **129.81 Ω** | shunt open
   **45.59 Ω** | line **129.81 Ω** | shunt open **81.32 Ω** — five elements,
   all λ/8 at 3 GHz (12.49 mm of ideal line), all buildable, and the stubs
   now stand a full line-length apart. That layout benefit was not free —
   the UEs *are* the separation.

Say what "exact by construction" means before hour 3 measures it: this
network's |S21| at every frequency equals the Chebyshev closed form evaluated
at Ω = tan(45°·f/f_c). At f_c: exactly −0.5000 dB — the equal-ripple edge,
to the last digit, because nothing anywhere was approximated. Check the
impedance realism while the numbers are on the board: 45.6 to 129.8 Ω —
comfortably inside microstrip's 20–120 Ω window (the 129.8 Ω line is pushing
it; lecture 5's synthesis says it is a 0.15 mm trace on our board — thin but
legal). Richards + Kuroda handed us a *buildable* filter with no luck
involved: the UE absorption into the stub impedances is what dragged
everything toward the middle of the window.

### 1.5 Hour recap (0:45–0:50)

Three sentences, then break. Ω = tan θ maps lumped synthesis onto
commensurate lines exactly, with λ/8-at-f_c calibrating the band edge to
Ω = 1. Kuroda's identity — an exact ABCD equivalence you derived in six
lines — trades unbuildable series stubs across unit elements for shunt stubs,
and today it produced an all-shunt 3 GHz lowpass: 81.3 / 129.8 / 45.6 Ω.
The tangent that made all this work is periodic, and hour 2 collects the
debt: at 6 GHz your lowpass is a perfect blocker, and at 9 GHz it is a
filter no more.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: stepped impedance, coupled lines, and the two honesty clauses (1:00–1:50)

### 2.1 The stepped-impedance lowpass — the quick-and-wide workhorse (1:00–1:10)

Before the main event, the cheap seats. A *short* length of *high-impedance*
line (βl ≪ 1) has ABCD ≈ [[1, jZ_h·βl],[j·βl/Z_h, 1]]: the series term
dominates — it is a **series inductor** ωL = Z_h·βl. Dually, a short low-Z
line is a **shunt capacitor** ωC = βl/Z_l. So a lowpass ladder becomes a
sausage of alternating fat and thin line:

> βlᵢ = gᵢ·R₀/Z_h (inductors) βlᵢ = gᵢ·Z_l/R₀ (capacitors), at ω_c.

Worked at 3 GHz, Butterworth N=3, Z_h = 120 Ω, Z_l = 20 Ω: electrical lengths
**23.9° / 45.8° / 23.9°**. Look at that middle number and say the quiet part:
45.8° is not "short." The approximation is already straining, and hour 3
measures the bill: the realized 3-dB point lands at **3.049 GHz** (1.6%
high), the stopband reaches only **13.1 dB at 6 GHz** where a true
Butterworth gives 18.1, the whole stopband bottoms out near **−14.9 dB**, and
the response is back to 0 dB by **11.7 GHz**. Design guidance, honestly
stated: stepped-impedance is the filter you use when the spec is soft and the
board space is real — bias-line cleanup, harmonic knockdown ahead of a real
filter — and its Z_h is capped by your fab's minimum trace width, which is
what actually sets its stopband. For anything with a hard skirt, keep
walking.

### 2.2 The coupled-line bandpass — lecture 7's investment pays out (1:10–1:28)

Slide cue: two parallel microstrip traces, the four mode field-pictures from
lecture 7 underneath.

The workhorse bandpass at microwave is a row of **parallel-coupled λ/4
sections**. Take two coupled lines, feed one end of line 1, take the output
from the far end of line 2, leave the other two ends open. Lecture 7 gave you
the tool for any symmetric four-port: decompose into the **even mode**
(impedance Z0e, both lines driven together) and the **odd mode** (Z0o,
anti-phase). Running that decomposition on this connection gives the 2-port
impedance matrix — write it, don't derive it (the derivation is lecture 7
homework algebra):

> Z₁₁ = Z₂₂ = −j·(Z0e + Z0o)/2 · cot θ
> Z₁₂ = Z₂₁ = −j·(Z0e − Z0o)/2 · 1/sin θ

Now evaluate at θ = 90° — quarter-wave: Z₁₁ = 0 and Z₁₂ = −j(Z0e−Z0o)/2. A
two-port with zero diagonal and purely off-diagonal coupling is an
**impedance inverter**: K = (Z0e − Z0o)/2. *The coupling strength is the
impedance split.* Everything else is lecture 8: a bandpass filter is
resonators coupled by inverters, and the g-values tell you how strong each
inverter must be. For fractional bandwidth Δ:

> Z₀J₁ = √(πΔ/2g₀g₁) — the end sections carry a square root
> Z₀Jₖ = (πΔ/2)/√(g₍ₖ₋₁₎gₖ), k = 2..N — the interior ones do not
> Z₀J₍N₊₁₎ = √(πΔ/2gNg₍N₊₁₎)

then each section's even/odd pair comes from inverting K = (Z0e−Z0o)/2 with
the constraint that the section also embeds a piece of the resonator:

> Z0e = Z₀(1 + JZ₀ + (JZ₀)²) Z0o = Z₀(1 − JZ₀ + (JZ₀)²)

Pre-empt the misconception before it forms: *"why do the end J's get square
roots?"* Because the end inverters couple a resonator to a **termination**
(g₀ = 1), not to another resonator — the same asymmetry that made hw6's
external Q different from the inter-resonator couplings.

**Worked on the board, N=3, 0.5 dB, Δ = 10%, f₀ = 2.4 GHz** (the homework's
core, done once here at full speed): J·Z₀ = 0.3137, 0.1187, 0.1187, 0.3137 —
then the table the class should copy down:

| section | Z0e (Ω) | Z0o (Ω) | K (Ω) |
|---|---|---|---|
| 1, 4 | 70.60 | 39.24 | 15.68 |
| 2, 3 | 56.64 | 44.77 | 5.94 |

(These are Pozar Example 8.8's numbers — the same electrical design at his
2 GHz — so the textbook itself referees your homework's module 2.) Each
section is λ/4 at 2.4 GHz. End sections couple hard — big even/odd split,
which physically means a *small gap*; interior sections couple gently — small
split, wide gap.

**From impedances to millimeters.** The toolkit closes the loop with
inverse-Hammerstad plus Akhtarzad's single-line equivalence (each mode of the
pair behaves like a single microstrip at half its mode impedance; a 2-D root
solve recovers width and gap). On our RO4350B board: end sections
**w = 0.93 mm, s = 0.087 mm**, interior **w = 1.15 mm, s = 0.46 mm**, lengths
**19.0 / 18.9 mm**. Pause on s = 87 µm: the end sections' gap is at the edge
of standard PCB etching — *the spec's bandwidth set that gap.* Wider Δ needs
tighter coupling needs smaller s; at some Δ the fab says no. That is a
bandwidth limit no synthesis formula prints.

One honesty clause on the design procedure itself, because the homework
measures it: the J-inverter picture is **narrowband** — exact at f₀,
first-order in (f−f₀)/f₀. The realized 0.5-dB bandwidth measures **9.83%**
against the designed 10%, and the ripple leaks to 0.57 dB at the far band
edge. Not a bug: a Taylor expansion, doing what Taylor expansions do. hw8's
lumped transformation was exact and hit its edges to machine precision; this
one is honest engineering approximation, and Q4 makes you locate it.

### 2.3 Reentrance — the periodicity debt comes due (1:28–1:38)

Slide cue: the Richards circle — θ winding around, the passband sectors
shaded, and the frequency axis unrolling it into repeating passbands.

Everything in sections 1–2 was built from cot θ and csc θ and tan θ — all
periodic in θ with period π. And θ is *linear in frequency* for TEM lines.
Conclusion, stated as a law: **every commensurate distributed filter's
response is periodic in frequency.** Where the copies land:

- **Stub lowpass** (λ/8 at f_c): passband 0 → f_c; attenuation pole at 2f_c
  (every stub λ/4: the open stubs become short circuits to ground); then the
  mirror-image skirt, and **a full passband again from 3f_c to 5f_c** —
  for the 3 GHz design, 9 to 15 GHz of wide-open filter.
- **Coupled-line bandpass** (λ/4 at f₀): passband at f₀; transmission zero
  at 2f₀ (θ = 180°, the half-wave section decouples); **the passband again
  at 3f₀** — θ = 270° = 90° + 180°, and cot/csc cannot tell the difference.
  For 2.4 GHz: **7.2 GHz, wide open, |S21| = 0 dB.** And again at 5f₀ =
  12 GHz, and forever.

The design consequences, each one a sentence the class should write down.
Your stopband spec is only enforceable *between* the passband and the first
reentrance — "40 dB ultimate rejection" is not a thing a commensurate filter
can promise. If a strong interferer sits near 3f₀, this topology is
disqualified *at the architecture level*, before any optimization. And the
system-level fix is honest cascading: a lowpass (whose own reentrance you
also check) mops up the bandpass's second life.

Pre-empt: *"does the lumped filter do this?"* No — ω runs to infinity on a
line, not around a circle; hw8's ladder rolls off monotonically forever.
Reentrance is the one genuinely new failure mode you bought when you traded
coils for copper. The hour-3 deliberate bug and homework Q1 both live here.

### 2.4 The ideal-vs-EM gap — what the field solver knows (1:38–1:48)

Our sweep so far assumes ideal TEM lines: both modes of a coupled pair travel
at the same speed, junctions are points, opens are opens. Microstrip signs
none of those contracts:

- **Even and odd modes travel at different speeds.** The odd mode's field
  lives more in the air above the gap (lower ε_eff, faster); the even mode's
  more in the substrate. The 2f₀ transmission zero required both modes to
  reach half-wave *together*; they don't, the zero splits in two, and energy
  leaks between the split zeros: the notorious **spurious passband near
  2f₀** of parallel-coupled microstrip filters.
- **Dispersion:** ε_eff rises with frequency (lecture 5), so a length cut
  using the quasi-static value is electrically long at f₀ — the whole
  response slides down in frequency.
- **Discontinuities:** open ends fringe (the stub is effectively longer than
  drawn), junctions store energy, steps scatter.

War story, the one this course keeps a candle lit for: a fabricated
coupled-line filter came back **4% low** — every section length had been cut
using ε_eff at DC instead of at f₀. Nothing in the ideal sweep could have
caught it; the ideal sweep *was the bug*. The catch is a model with more
physics: a field solver, or the board itself.

**The case study.** openEMS (a free FDTD field solver) is instructor-run
only — you post-process its exported Touchstone, never install it. Honesty
box, said out loud in class: *on the course machine this week the real export
does not exist yet*, so the lab generates a **loudly-labeled placeholder**:
the ideal model re-swept with a documented ±3% even/odd ε_eff split and +2%
dispersion. It is not a field solution — it is the ideal model plus exactly
the two mechanisms named above, so the *shape* of the gap is honest while
the numbers are stand-ins. What it shows (hour 3, cell 3.6, every figure
stamped with its source): center slides **2.4000 → 2.3740 GHz (−1.1%)**,
|S21| at 2.4 GHz drops to **−0.29 dB**, and the ideal −77 dB at 2f₀ becomes
**−0.3 dB** — the spur, life-size. When the real export lands in `lab/`, the
same cell reads it and the numbers update; the pipeline is the lesson.

### 2.5 Hour recap (1:48–1:50)

Stepped impedance: fast, wide, honest about neither cutoff nor skirt — and
capped by your fab's thinnest trace. Coupled lines: even/odd split *is* the
coupling; g → J → (Z0e, Z0o) → millimeters, with the end sections carrying
square roots and the tightest gaps. Two honesty clauses on everything
distributed: the response repeats (7.2 GHz is wide open, and you will predict
that before sweeping), and the ideal model is off by a mode-velocity split
and a dispersion shift that only more physics can price. Hour 3 makes every
one of those numbers print.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the synthesis chain, end to end, and the sweep that keeps you honest (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate
while typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x,
matplotlib 3.10.x, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed
pre-class pairs up now — do not debug installs live.

### 3.2 The Richards map (2:03–2:08)

Cell 3.2: one table, f → θ → Ω. Point at each row as it prints: 3 GHz maps
to Ω = 1 (the band edge, by our λ/8 choice); 6 GHz prints Ω ≈ 3.5×10¹⁵ —
numerical infinity, the attenuation pole; 9 GHz maps to **−1**, a band edge
again; 12 GHz maps to zero — "the filter thinks it is at DC." The closing
line of the cell is the lecture's thesis: *tan is periodic, therefore every
commensurate filter repeats. Forever.*

### 3.3 The stub lowpass, built live (2:08–2:16)

Cell 3.3: the g-recursion (compact form of hw8's engine), Richards, then the
Kuroda step printed as a before/after: the unbuildable series form on one
line, the all-shunt form on the next — 81.32 / 129.81 / 45.59 / 129.81 /
81.32 Ω. Sweep it. Three measured facts to read out loud: |S21|(3 GHz) =
**−0.500000 dB** — the equal-ripple edge, exact; the whole sweep lands on
the Chebyshev-through-the-map closed form to **2.8×10⁻¹⁴ dB**; the Kuroda'd
network and the series-stub network agree to **7.8×10⁻¹⁶** — *an identity,
not an approximation* (that number is homework Q3). The saved figure shows
the pole at 6 GHz and — keep the axis wide on purpose — the passband
returning at 9 GHz.

### 3.4 Stepped impedance, priced (2:16–2:24)

Cell 3.4: the three-line design (23.9° / 45.8° / 23.9°), swept as ideal
lines: 3-dB point **3.049 GHz**, stopband 5 dB shy at 6 GHz. Then the copper
step: inverse-Hammerstad widths on RO4350B — **0.178 mm** for the 120 Ω line
(mind your fab's minimum trace) and **4.04 mm** for the 20 Ω line — physical
lengths 4.29 / 7.27 / 4.29 mm, and the same filter re-swept with skrf
`MLine` physics (finite thickness, dispersion): the 3-dB point moves again,
to **3.112 GHz**. Moral, stated once: the ideal-line design was already an
approximation of the prototype; the copper is an approximation of the
ideal-line design; *quote which model produced every number you report.*

### 3.5 The coupled-line bandpass, end to end (2:24–2:33)

Cell 3.5: the whole chain at conversation speed — g → J·Z₀ (0.3137 / 0.1187,
"end sections carry the square root") → the Z0e/Z0o table (70.60/39.24,
56.64/44.77 — "Pozar's own Example 8.8, at our frequency") → the ideal
sweep: IL(f₀) = 0.0000 dB, 0.5-dB band 2.282–2.518 GHz = **9.83%** against
the designed 10 ("the narrowband mapping's fee — module 2 is exact, the
inverter *picture* is not") → Akhtarzad dimensions, w/s/ℓ per section, with
the 87 µm end-gap called out. This cell is the homework's modules 2 and 3
compressed into one screen; slow down over the θ = 90°-at-f₀ line in the
sweep function, because that one line is module 3.

### 3.6 The case study — ideal meets "reality" (2:33–2:40)

Cell 3.6, lecture 5's precedent upgraded: the cell loads whatever Touchstone
sits at `openems_coupled_bpf.s2p` and post-processes it identically whether
it is the instructor's field solve or the placeholder. Today it prints its
source in capital letters: **PLACEHOLDER — NOT field-solved**. The three
deltas from hour 2 print live: center −26 MHz, −0.29 dB at 2.4 GHz, and the
2f₀ spur at −0.3 dB where the ideal model promised −77. Say the two-sentence
sermon: *the same code will read the real export the day it exists — build
the pipeline before the data, and label every stand-in so loudly it cannot
survive into a report by accident.*

### 3.7 Deliberate bug — victory declared at 2f₀ (2:40–2:44)

Cell 3.7, the bug hour 2 promised. The system spec: ≥ 40 dB above 3.2 GHz.
Sweep the finished filter 0.1 → 4.8 GHz — a perfectly reasonable-looking
choice, 2× the center frequency, exactly where a lumped-filter engineer
would stop. Worst rejection above 3.2 GHz: **52.8 dB, deepening with
frequency.** Ship it. Then re-run the sweep to 10 GHz: worst rejection above
3.2 GHz is **0.0 dB, at 7.20 GHz** — a second passband, wide open, 2.4 GHz
beyond the edge of the bug's sweep. The two-panel figure goes on the
projector for a long ten seconds. The rule that survives the course:
**commensurate filters are periodic — sweep past 3f₀, always, and know
where 5f₀ is.**

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. Walk the story — hw8's philosophy, this week's
copper — then the modules and the two commands:

- Module 1 is the stub lowpass: Richards + Kuroda, and the checker demands
  −0.5000 dB at 3 GHz *exactly* — no series stubs may survive in your output.
- Module 2 is the core: the g → J → (Z0e, Z0o) chain; the textbook's own
  table referees you, and the toolkit turns your impedances into millimeters.
- Module 3 is the honest sweep: 0.1–10 GHz, the spec table, and
  `find_reentrant`.
- **Predictions come first.** Q1 (where does the filter come back, and why)
  and Q2 (does the 2f₀ zero survive contact with microstrip) are answered
  *before* running — committing to the mechanism is the assignment.
- `--check` prints facts, not PASS/FAIL — closed forms, the skrf referees,
  the textbook table, and case-study deltas loudly tagged PLACEHOLDER.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: Ω = tan θ carried lumped synthesis into
copper exactly (−0.500000 dB, measured); Kuroda was an identity (7.8×10⁻¹⁶,
measured); and the periodicity bill arrived on schedule (7.2000 GHz, wide
open, measured — after a truncated sweep said everything was fine). Teaser:
next week the passives are done and the *receiver* begins — noise
temperature, Friis's other famous formula, and why the first amplifier in
the chain owns your radar's sensitivity almost by itself.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 4 (*Modules*), chs. 2–3 — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, §§8.5–8.8 — Richards/Kuroda,
  stepped-impedance, and coupled-line filters as taught here (for owners).
- Richards, "Resistor-Transmission-Line Circuits," *Proc. IRE* 36, 1948 —
  the commensurate-network theorem in the original.
- Akhtarzad, Rowbotham & Johns, "The Design of Coupled Microstrip Lines,"
  *IEEE Trans. MTT-23*, 1975 — the lab's dimension helper.
- [R18] Matthaei, Young & Jones, *Microwave Filters, Impedance-Matching
  Networks, and Coupling Structures* — the exact-bandwidth corrections Q4
  gestures at (reference only).
- openEMS case-study files in `lessons/09-filters-distributed/lab/`
  (placeholder until the instructor export lands — the file says so itself).
