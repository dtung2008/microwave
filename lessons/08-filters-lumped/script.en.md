# Lecture 8 — Filters I: The Insertion-Loss Method

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (`pip install -r requirements.txt`: numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 1–7 — especially the dB grammar (L1), the ABCD cascade
(L4), and resonators/Q (L6). Rusty on ABCD? Skim L4's hour 3 before class.
**Pre-class setup:** the course venv from lecture 1, then run `lab/setup_check.py` —
it must print `SETUP OK`.

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the spec, the method, and the two classic shapes (0:00–0:50)

### 1.1 The receiver's front door (0:00–0:10)

Slide cue: the 60 MHz IF strip with its neighbors — the wanted band flanked by an
image band at 35 MHz and a co-site VHF transmitter at 85 MHz.

Open with the customer, not the mathematics. Lecture 1's course radar mixes its
10 GHz echoes down to an IF (intermediate frequency) of 60 MHz — lecture 12 will
show you *why* 60, but the consequence lands today: the IF strip lives in a crowded
neighborhood. The frequency plan parks two known aggressors ±25 MHz away — the
second mixer's image band at 35 MHz, a co-site VHF comms link at 85 MHz — and both
arrive *stronger* than a drone echo from 4 km out. Before homework 1's carefully
priced 1 MHz detection bandwidth means anything, something must kill the neighbors
without touching the band. That something is this lecture.

The spec language — three numbers, and every filter conversation you will ever have
uses them:

- **Passband ripple:** the worst attenuation anywhere in the band you promised to
  pass. Ours: ≤ 0.5 dB across 55–65 MHz. (Ripple wobbles; the *spec* is its ceiling.)
- **Stopband rejection:** the least attenuation at the frequencies you promised to
  kill. Ours: ≥ 40 dB at 35 and 85 MHz.
- **Group delay:** how long each spectral slice takes to get through — the phase
  spec amplitude plots hide. Hour 2 shows why a radar cares.

Three claims for today — on the board, left up:

1. **Every ladder filter is one filter.** You will design exactly one thing — the
   lowpass prototype, cutoff 1 rad/s, 1 Ω ends — and reach every passband shape,
   impedance level, center frequency, and bandwidth by mechanical substitution.
   That architecture *is* the insertion-loss method.
2. **Ripple is a currency.** Allowing the passband to wobble up to its 0.5 dB
   ceiling buys steeper skirts — today we measure the exchange rate: 11.7 dB more
   rejection at the same order, or one whole section saved.
3. **The bandpass center is the geometric mean, √(f₁f₂)** — not the arithmetic
   one — and hour 3 builds the wrong one to show you how politely a filter fails
   when you forget.

Pre-empt the question forming in the DSP crowd: *"I've done Butterworth and
Chebyshev in a signals course — is this review?"* The polynomials are the same
friends. What is new is that our filter must be a *circuit*: a passive, doubly
terminated LC ladder whose element values come from the polynomial, whose source
and load are 50 Ω, and whose imperfections are physical. The g-values you compute
today are component values next week — and their microstrip descendants in
lecture 9.

### 1.2 The insertion-loss method — one machine, four stages (0:10–0:20)

Slide cue: the pipeline — spec → prototype → scale → transform → sweep.

Define the object we design against. The **power loss ratio** of a two-port between
its terminations:

> P_LR = (power available from source)/(power delivered to load) = 1/|S21|² —
> and IL = 10·log₁₀ P_LR is the **insertion loss** (插入損耗 for the bilingual
> glossary; it is the |S21| of lecture 4, upside down).

The insertion-loss *method* is the decision to specify P_LR(ω) as mathematics
first and find a circuit second. For a physical two-port, |Γ|² is an even function
of ω, which forces P_LR = 1 + M(ω²)/N(ω²), a ratio of polynomials. Choose the
polynomial, get the response; extract the circuit, get the filter. Contrast it
with the older image-parameter method — cascade sections and hope the terminations
forgive you — which gave filters that worked and specs that were never quite
guaranteed. Insertion loss says: state the response you are owed, then synthesize
a network that *provably* delivers it between real terminations.

The four stages on the slide, because they are the homework's module map:

1. **Prototype:** a lowpass ladder, cutoff Ω = 1, source and load ≈ 1 Ω, element
   values g₁ … g_N and load g_{N+1}. All the shape decisions happen here.
2. **Impedance scale** to 50 Ω. 3. **Frequency transform** to lowpass/highpass/
   bandpass/bandstop at the real frequencies. 4. **Sweep** what you built and
   read the spec table off the curve — the step everyone skips and regrets.

The ladder convention, drawn now and reused for two weeks: series inductors g₁,
g₃, … alternating with shunt capacitors g₂, g₄, … (or the exact dual — same
g-numbers, swapped roles), g₀ = 1 the source, g_{N+1} the load. One ladder,
N reactive elements, N g-numbers plus a load.

### 1.3 Butterworth — derived twice (0:20–0:33)

**Level 1 — maximal flatness (the fast version).** Demand the flattest possible
passband: P_LR = 1 + Ω^(2N). At Ω = 0, perfection; at Ω = 1, always 3.01 dB (this
is a *definition* to remember — the Butterworth band edge is its 3-dB point);
beyond, the skirt falls at 20N dB/decade. All 2N−1 first derivatives of P_LR
vanish at DC — hence *maximally flat* (最平坦). The price is visible already: all
the approximation error is hoarded at the band edge, where the spec was loosest.

**Level 2 — pole positions (the first-principles version).** Where must the poles
of S21(s) sit? On the imaginary axis P_LR = 1 + (−s²)^N, so the poles of
|S21|² solve (−s²)^N = −1: **2N points equally spaced on the unit circle**, none
on the axis. Keep the N in the left half-plane (stability chooses for you), and
for N = 3 read them off: s = −1 and −½ ± j(√3/2). This is exactly what
`scipy.signal.buttap` returns, and hour 3 uses that identity as a referee. From
the poles, network synthesis (the machinery in 1.4) delivers a closed form worth
boxing:

> g_k = 2·sin[(2k−1)π/2N], k = 1…N, g_{N+1} = 1 — always symmetric, always
> terminated in 1.

Check it the way an engineer checks: N = 1 says g₁ = 2·sin(π/2) = 2. Direct
derivation: one shunt C across a 1 Ω source and 1 Ω load gives |S21|² =
1/(1 + (ωC/2)²); demand 3 dB at ω = 1 and C = 2 falls out. The formula and the
circuit agree on the simplest case you can do by hand — hold that method, 1.4
repeats it under harder conditions. N = 4, which the homework needs: 0.7654,
1.8478, 1.8478, 0.7654. Hour 3 prints the table.

### 1.4 Chebyshev — ripple mechanics and the recursion (0:33–0:47)

Slide cue: Butterworth and Chebyshev N = 3 on the same axes; the equal-ripple
band highlighted.

The equal-ripple idea in one sentence: if the spec lets you err by 0.5 dB anywhere
in the band, err by *exactly* 0.5 dB everywhere — hoarding flatness at DC, where
nobody asked for it, wastes budget the skirt could spend. The Chebyshev polynomial
C_N is the tool because it is the polynomial that oscillates between ±1 on [−1,1]
and then explodes: C_N(Ω) = cos(N·arccos Ω) in band, cosh(N·arccosh Ω) outside,
with the recursion C_{N+1} = 2Ω·C_N − C_{N−1} (state it; the DSP students will nod).
So:

> P_LR = 1 + ε²·C_N²(Ω), with ε² = 10^(ripple/10) − 1. For 0.5 dB, ε = 0.3493.

In band, P_LR ripples between 1 and 1+ε² — N ripple extrema, band edge *at* the
ripple value (for odd N; even N has a wrinkle we meet in a minute). Outside,
C_N ≈ ½(2Ω)^N, so the skirt runs (2^(2(N−1))·ε²)× higher than a same-order
Butterworth's — 6(N−1) dB plus change. Measured, hour 3, same 0.5-dB passband,
N = 3, at the homework's stopband frequency: Chebyshev 40.52 dB, Butterworth
28.84 dB. **Ripple bought 11.7 dB.** That is claim 2 with a number on it.

Pre-empt the misconception now, because it is written on half the whiteboards in
industry: *"more allowed ripple = worse filter."* No — it is a **trade**. More
ripple means more in-band error *and* more rejection per section. The designer
does not minimize ripple; the designer spends exactly the ripple the system can
tolerate (an ADC driver may take 1 dB; a channelizer 0.1 dB) and cashes it as
sections saved. Equal-ripple is minimax approximation wearing an LC costume.

**The g-values — stated, then earned.** The recursion, boxed, because the homework
implements it for any N:

> β = ln[coth(ripple_dB/17.37)], γ = sinh(β/2N)
> a_k = sin[(2k−1)π/2N], b_k = γ² + sin²(kπ/N)
> g₁ = 2a₁/γ, g_k = 4a_{k−1}a_k / (b_{k−1}·g_{k−1}), k = 2…N
> g_{N+1} = 1 (N odd), coth²(β/4) (N even)

(That 17.37 is 40/ln 10 — it converts dB of ripple into the nepers the hyperbolic
functions want. Nothing mystical.)

Earn it twice. **Fast:** the N = 1 closed loop, same method as Butterworth's. One
shunt C between 1 Ω ends, demand attenuation exactly `ripple` at ω = 1: C = 2ε.
The recursion says g₁ = 2a₁/γ = 2/sinh(β/2), and a short hyperbolic-identity fight
(do it — two lines with e^(β/2) = √coth) gives 2/sinh(β/2) = 2ε *identically*.
The β/γ machinery is ε in disguise. Hour 3 prints both: 0.698623 = 0.698623.

**First-principles:** where does the general recursion come from? From doing to
P_LR what we did for N = 1, at any N: write S11 from |S11|² = 1 − 1/P_LR (a
spectral factorization — pick the left-half-plane factors), form
Z_in = (1+S11)/(1−S11), and peel the ladder off one element at a time by
continued-fraction division — series L, shunt C, series L… — the same long-division
you did for rational functions, with circuit meaning. Takahasi and others pushed
the algebra symbolically to the closed recursion above; we will not grind it on
the board — instead, hour 3 *executes* it numerically: the homework's referee
extracts g-values from scipy's own poles by exactly this Z_in long division, an
independent path that must agree with your recursion to 1e-8. It agrees to 1e-12.
The derivation is real; the machine just holds the pencil.

**The even-N wrinkle**, because the checker will show it to you: for even N,
C_N(0) = ±1, so the response is 0.5 dB down *at DC*. But a lowpass LC ladder is
transparent at DC — series Ls short, shunt Cs open — so DC loss can only come from
a resistive mismatch. Hence g_{N+1} = coth²(β/4) = 1.9841 for 0.5 dB: the even-N
equal-ripple filter *requires unequal terminations*, and the mismatch loss of
1.9841 vs 1 is — compute it — 0.4999 dB. Exactly the ripple. Nothing in a filter
table is arbitrary. (Practical corollary: 50 Ω catalogs are full of odd-N filters.
Homework Q3 makes you own this argument.)

### 1.5 Hour recap (0:47–0:50)

Three sentences, then break: the insertion-loss method designs a response
(P_LR = 1 + ε²C_N² or 1 + Ω^(2N)) and then synthesizes the unique ladder that
delivers it between real terminations; Butterworth hoards flatness at DC and pays
at the skirt, Chebyshev spends the ripple budget everywhere and collects 11.7 dB;
the g-recursion is β, γ, a_k, b_k — and it is scipy-checkable, which is how you
will know yours is right. Hour 2 makes it a 60 MHz filter with real henries.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: scaling, transformation, order, and delay (1:00–1:50)

### 2.1 Impedance and frequency scaling (1:00–1:10)

The prototype lives at 1 Ω / 1 rad/s. Real life is 50 Ω and megahertz. Two
substitutions, each earned in one line:

**Impedance scale by R₀:** multiply every impedance in the network by R₀ and no
ratio changes — S-parameters (referenced to the new R₀) are untouched. Inductor
impedance jωL scales by making L' = R₀L; capacitor impedance 1/jωC scales by
making C' = C/R₀. Resistors: R' = R₀R.

**Frequency scale by ω_c:** replace Ω ← ω/ω_c everywhere; a reactance that was
jΩg becomes jωL' with **L' = g/ω_c** — element values shrink as frequency grows
(hold that thought for 2.5). Combined, the lowpass recipe: L' = gR₀/ω_c,
C' = g/(R₀ω_c).

Do one out loud to calibrate hands: 0.5-dB Chebyshev N = 3 lowpass at 100 MHz,
50 Ω: L₁ = 1.5963·50/(2π·10⁸) = 127 nH; C₂ = 1.0967/(50·2π·10⁸) = 34.9 pF.
Buyable parts. The homework's checker prints values in nH and pF for the same
reason — a synthesis that ends in numbers you cannot solder is not finished.

### 2.2 Lowpass → bandpass — worked fully, traps included (1:10–1:28)

Board work, the centerpiece. The transformations are frequency substitutions in
P_LR(Ω):

- **Highpass:** Ω ← −ω_c/ω. Inductors become capacitors and vice versa (the
  slide has the two-line table).
- **Bandpass:** Ω ← (1/Δ)·(ω/ω₀ − ω₀/ω). - **Bandstop:** the reciprocal.

Everything about bandpass lives in that substitution, so read it slowly. It maps
ω = ω₀ to Ω = 0 (band center ← DC), and it maps the *pair* ω₁, ω₂ to Ω = ∓1
provided you define:

> **ω₀ = √(ω₁ω₂)** — the geometric mean — and **Δ = (ω₂−ω₁)/ω₀** — the
> fractional bandwidth *measured against that ω₀*.

Why geometric? Because the map has an exact symmetry: Ω(ω₀²/ω) = −Ω(ω). The
transformed filter treats ω and ω₀²/ω as the same frequency. Frequencies pair by
*ratio*, not by difference — the lowpass response is symmetric on a log axis, and
√(f₁f₂) is the log-axis midpoint. For our spec: f₀ = √(55·65) = **59.7913 MHz**,
Δ = 10/59.7913 = **0.1672**. Not 60.0. The 0.35% gap between the right center and
the obvious one is hour 3's deliberate bug, and it is exactly one ripple-band's
width of wrong.

Now push the substitution through the elements — this is where algebra becomes
hardware:

- A **series inductor** g: reactance jΩg → j(g/Δ)(ω/ω₀ − ω₀/ω) — positive slope
  through zero at ω₀ — that is a **series L-C pair, resonant at ω₀**:
  L = gR₀/(Δω₀), C = Δ/(gR₀ω₀).
- A **shunt capacitor** g: same story in admittance — a **parallel L-C to
  ground, resonant at ω₀**: C = g/(ΔR₀ω₀), L = ΔR₀/(gω₀).

Say the invariant out loud, because it is the homework's per-branch check: **every
branch of a bandpass ladder resonates at the same f₀ = √(f₁f₂)** — lecture 6's
resonators, one per g, each detuned copy of the same resonance, coupled through
the ladder. (Cohn [R23] rebuilt this whole picture as "resonators + couplings",
which is the form lecture 9 and every microwave filter book actually uses.)

The numbers for our filter, on the board — hour 3 prints them and the homework
checker measures them:

> series branches: **1270.3 nH / 5.578 pF** · shunt branch: **20.30 nH /
> 349.09 pF** · all resonant at **59.7913 MHz**.

Two traps, named while the numbers are on the board:

1. **The element spread.** Series-branch L over shunt-branch L is 1270/20.3 ≈
   63×. Track the Δs: series L ∝ 1/Δ, shunt L ∝ Δ — the spread grows as
   g₁g₂/Δ². Narrow the bandwidth by 3× and the spread grows by ~9×; at Δ a few
   percent the parts leave the catalog. This — not taste — is why narrowband
   filters abandon the direct ladder for coupled resonators (L9).
2. **The center.** If any branch resonates off √(f₁f₂), the ripple band slides.
   Hour 3 quantifies the damage.

Pre-empt the fair objection: *"my two edges 55 and 65 aren't geometrically placed
around anything nice — is the map still exact?"* Yes — f₀ is *defined* from your
edges, so the two edges always land exactly on Ω = ±1. What is **not** symmetric
afterwards is everything else you care about: an arithmetically-placed spec point
(±25 MHz!) maps to two very different Ω values. That is 2.3's opening move, and
homework Q2's prediction.

### 2.3 Order estimation — the nomogram, retired (1:28–1:36)

The old books solve "what N do I need" with a nomogram. We have closed forms.
First map the stop frequencies through the bandpass substitution:

> Ω(35 MHz) = (1/0.1672)·(35/59.79 − 59.79/35) = **−6.714**
> Ω(85 MHz) = (1/0.1672)·(85/59.79 − 59.79/85) = **+4.294**

The skirt is monotone in |Ω|, so the *smaller* |Ω| binds: the 85 MHz edge decides
the order, and the 35 MHz edge will enjoy a fat margin it never asked for. (The
geometric mirror of 85 MHz is 59.79²/85 = 42.1 MHz — the spec's 35 sits well
below it.)

Both families face the same attenuation headroom ratio — the spec in one number:

> A = (10^(L_stop/10) − 1)/(10^(L_edge/10) − 1) = (10⁴−1)/(10^0.05−1) = **81,945**

Invert the two P_LR formulas at Ω_s (two lines each — do the Chebyshev one on the
board: ε²cosh²(N·arccosh Ω_s) ≥ A·ε² gives):

> Chebyshev: N ≥ arccosh(√A)/arccosh(Ω_s) = 6.350/2.137 = **2.972 → N = 3**
> Butterworth: N ≥ log₁₀(A)/(2·log₁₀ Ω_s) = 4.914/1.266 = **3.882 → N = 4**

One honest subtlety before someone's design misses spec by definition: for
Butterworth, "the band edge" must mean *the 0.5-dB point* — our passband promise —
not the traditional 3-dB point. The formula above, with A built from
L_edge = 0.5 dB, pins it correctly; equivalently you widen the design bandwidth
by ε^(−1/N) so the 3-dB points move out and the 0.5-dB points land on 55/65
(hour 3 does exactly this to build a fair group-delay comparison). Use the 3-dB
convention here and you get a filter that is 3 dB down at 65 MHz — legal
Butterworth, failed spec.

So: claim 2, settled by arithmetic — **3 sections of Chebyshev do what 4 sections
of Butterworth do** for this spec. The homework's Q1 asks you to predict this gap
before the checker confirms it; the interesting part of the reconciliation is why
the gap is only one.

### 2.4 Group delay — where the steep filter pays (1:36–1:44)

Definition on the board: **τ_g = −dφ/dω**, φ the phase of S21. A filter is
distortionless through the band only if τ_g is flat there; delay that varies
across the band smears any signal whose spectrum spans the band.

The shape to internalize: group delay **peaks at the passband edges** — the
band-edge poles sit closest to the jω axis, and each pole contributes delay like
a resonance. Steeper amplitude ⇒ edge poles pushed closer ⇒ higher, sharper delay
peaks. Flat amplitude was never free; the equal-ripple filter pays in phase.

Measured, hour 3, both filters built to the same 0.5-dB edges:

> Chebyshev N = 3: **68.3 ns** at center, **128.5 / 108.8 ns** at the edges.
> Butterworth N = 4: **63.9 ns** center, **99.2 / 84.0 ns** at the edges —
> flatter delay *despite the extra section*.

Now the radar tie-in, because the course's filter serves lecture 1's radar: the
echo is a pulse; its spectral slices ride through this filter at different speeds.
An in-band delay spread of Δτ ≈ 60 ns is c·Δτ/2 ≈ **9 m of range smear** — the
pulse edge lecture 15's range resolution will depend on, softened before the
detector ever sees it. A channelized comms receiver might not care; a precision
ranging system does. Hence the honest design statement: *the steepest filter that
meets the rejection spec is not automatically the right filter* — amplitude spec,
delay spec, and section count are one negotiation. When delay flatness dominates,
there is even a third family — Bessel, maximally flat delay — which we name today
and use the day a homework pulse comes out smeared.

### 2.5 Where lumped stops working — and recap (1:44–1:50)

Look back at the element values: at 60 MHz, 1270 nH and 349 pF are shelf parts
with self-resonances safely above band. Now run the same three-branch recipe at
2.4 GHz, 10% bandwidth (hour 3 prints it): series **52.9 nH with 0.083 pF**,
shunt **0.30 nH with 14.5 pF**. A 0.083 pF capacitor is smaller than the parasitic
of the pad you would solder it to; 0.30 nH is less than the inductance of a single
via; and a real 52.9 nH coil's self-resonance sits *below* 2.4 GHz — it is a
capacitor up there. The lumped ladder is over. What survives is everything else:
the spec language, the g-values, the transformations, the order formulas. Lecture
9 keeps the mathematics and swaps the hardware — transmission-line resonators via
Richards' transformation and Kuroda's identities, coupled-line filters via Cohn's
resonator-and-coupling picture. Same brain, new copper.

Recap: scale by R₀ and ω_c; bandpass = every g becomes a resonator at √(f₁f₂)
(geometric!); order from the closed forms after mapping the *binding* stop edge
(here 85 MHz → Ω 4.294 → Chebyshev 3, Butterworth 4); group delay peaks at the
edges and prices the steepness (60 ns spread ≈ 9 m of radar smear). Hour 3 builds
all of it, then breaks the center on purpose.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the synthesis machine, live (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:05)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed pre-class pairs up
now — do not debug installs live.

### 3.2 The g-value engine, and scipy as referee (2:05–2:15)

Cell 3.2: the whole recursion is a dozen lines — type it, do not paste it. Print
the tables: Butterworth N = 3 gives [1, 2, 1, 1] (tell them to memorize that one;
it is the "did I break something" canary), Chebyshev 0.5 dB N = 3 gives the
classic [1.5963, 1.0967, 1.5963, 1] and N = 2 ends in 1.9841 — the even-N load
from 1.4, on screen. Then the two checks: the hand-derived N = 1 case
(g₁ = 2ε = 0.698623 — recursion agrees to the sixth decimal), and the referee —
sweep the g-ladder by ABCD at prototype level and overlay
`scipy.signal.cheb1ap`'s response: **max |Δ| = 1.4e-14 dB**. Say the moral: the
ladder and the pole set are the same filter through two unrelated code paths;
when they disagree, someone's algebra is wrong, loudly. The homework's referee is
this idea upgraded: it extracts g-values *from* scipy's poles by continued
fractions and demands 1e-8 agreement.

Close the cell with the exchange rate: same order, same 0.5-dB edge, rejection at
Ω = 4.294: Chebyshev **40.52 dB**, Butterworth **28.84 dB**. Ripple bought
11.7 dB. Q1 of the homework starts here.

### 3.3 Scale, transform — the IF filter appears (2:15–2:25)

Cell 3.3: `f0 = sqrt(55 * 65) MHz = 59.7913 MHz (not 60!)` prints first —
foreshadowing. Then `bandpass_ladder`: fifteen lines that turn three g-numbers
into six component values; the printout shows every branch resonating at
59.7913 MHz. Sweep by ABCD (the lecture-4 cascade, vectorized), draw |S21| and
|S11| against the spec mask, and print the spec table:

> worst passband attenuation **0.5000 dB** · rejection **52.38 dB** @ 35 MHz ·
> **40.52 dB** @ 85 MHz.

Point at the asymmetry — the spec was symmetric, ±25 MHz; the filter is not.
Twelve dB of unrequested margin below, half a dB above. The 85 MHz edge is doing
all the work, exactly as the Ω mapping predicted. Then the referee line: the same
six components handed to scikit-rf's lumped-element media, cascaded with `**` —
**max |ΔS21| = 4.2e-14**. Two implementations, one filter.

### 3.4 Group delay — the cost, plotted (2:25–2:33)

Cell 3.4: build the fair Butterworth — N = 4, design band widened by ε^(−1/4) so
its 0.5-dB points land exactly on 55/65 (the subtlety from 2.3, now three lines
of code). Its spec table prints 41.49 dB at 85 MHz — it meets the same spec, with
one more section. Then `-np.gradient(np.unwrap(np.angle(s21)), 2πf)` and the
delay plot: Chebyshev peaking at 128.5 ns on the 55 MHz edge against its 68.3 ns
center; Butterworth flatter everywhere despite being the bigger filter. Print the
9-meter line: 60 ns of in-band spread, times c/2. Let the class sit with the
trade for ten seconds: the *steeper* filter and the *better-behaved* filter are
different filters, and the spec sheet chose one without asking the radar.

### 3.5 Deliberate bug — the arithmetic-mean center (2:33–2:42)

Cell 3.5, the bug hour 1 promised. Copy `bandpass_ladder`, change one line:
`f0 = (f1 + f2) / 2`. Sixty instead of 59.79 — a 0.35% slip that every tired
engineer has typed. Sweep it. On screen the curve is beautiful: centered, steep,
rejections printing 52.66 and 40.33 dB — *both still passing*. Then print both
spec tables side by side and let the 55 MHz row land: **0.9726 dB where 0.5 was
promised.** The whole ripple band slid up to 55.21–65.21 MHz; the lower spec edge
fell off it, onto the skirt. Say the two lessons slowly. First: this bug does not
crash, does not look wrong, and passes the stopband — only the *spec-edge numbers*
convict it. Never grade a filter by its plot. Second: the checker's per-branch
resonance test exists because of exactly this failure — the wrong center shows up
as every L·C product resonating at 60.00 MHz, a 3.5e-3 relative offset the
instrument reads instantly, where the eyeball reads nothing.

Then cell 3.6, thirty seconds, the door to next week: the same recipe at 2.4 GHz
prints 0.083 pF and 0.30 nH — parts smaller than their own parasitics. Lumped is
over; the g-values are not.

### Homework brief (2:42–2:47)

`lab/HOMEWORK.md` on screen. Walk the story — the radar's 60 MHz IF, two
aggressors at ±25 MHz, one filter — then the modules and the two commands:

- Module 1 is the core: `g_values`, both families, any N, by recursion — refereed
  against element extraction from scipy's own prototypes (read the referee
  *after*; it is 1.4's derivation running on silicon). Module 2 is the
  synthesizer: order estimate, then spec → henries and farads. Module 3 sweeps
  the ladder by ABCD and fills the spec table with measured margins.
- **Predictions come first.** Q1 — how many more sections does Butterworth need
  than 0.5-dB Chebyshev for this spec? — and Q2 — which stop edge gets the thin
  margin? — are answered *before* running. Committing to the number is the
  assignment.
- `--check` prints facts, not PASS/FAIL — the scipy deltas, the branch
  resonances, the margins. `--sweep` draws the picture Q2 and Q4 are about.
- Budget ≤ 3 hours. AI use assumed and welcome — the predictions and
  reconciliations in ANSWERS.md are the part that must be yours.

### Wrap-up (2:47–2:50)

Recap against the three claims: one prototype reached every spec — the pipeline
ran spec → g → 50 Ω → 59.7913 MHz → measured margins; ripple was a currency —
11.7 dB at equal order, one section at equal spec; and the center was the
geometric mean — being 0.35% wrong about it cost the 55 MHz edge its ripple
budget. The IF filter you built today is a block in lecture 1's radar: it guards
the strip that feeds the 1 MHz detection bandwidth homework 1 priced, and
lectures 10–12 will bolt the LNA and mixer around it. Teaser: next week the same
g-values leave the component catalog and become geometry — Richards'
transformation, Kuroda's identities, coupled-line filters, and the reentrant
passbands that lumped filters never warned you about. Same philosophy, in copper,
at 2.4 GHz.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 4 (*Modules*), ch. 2 (filters) —
  free: https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, ch. 8 — the insertion-loss method as
  taught here (for owners of the book).
- [R23] Cohn, "Direct-Coupled-Resonator Filters," *Proc. IRE* 1957 — the
  resonator-and-coupling view this lecture's branch-resonance invariant points
  toward; lecture 9 lives in it.
- [R18] Matthaei, Young & Jones, *Microwave Filters, Impedance-Matching Networks,
  and Coupling Structures* — the industry's filter bible (reference only; the
  tables you now generate by recursion).
- [R4] Orfanidis, *Electromagnetic Waves and Antennas*, ch. 13 (filter design
  sections) — free: https://www.ece.rutgers.edu/~orfanidi/ewa/
