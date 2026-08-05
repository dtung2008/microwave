# Lecture 6 — Broadband Matching & Resonators

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course venv: numpy 1.26.4, scipy, matplotlib,
scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 2–4 (transmission lines, Γ and Z_in(ℓ); the Smith
chart and why a match is a resonance; S-parameters and the ABCD cascade). The λ/4
transformer from lecture 2 is today's protagonist; lecture 4's cascade machinery is
today's referee.
**Pre-class setup:** course venv + `lab/setup_check.py` — it must print `SETUP OK`.
(This lecture's check also smoke-tests `skrf.qfactor.Qfactor`, the week's second
referee.)

Format note: hours 1–2 are principles (board + slides, `slides/principles.en.html`);
hour 3 is tools, live-coded, mirroring `lab/hour3_walkthrough.py` cell-for-cell.
Practice happens in the homework (`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: broadband matching (0:00–0:50)

### 1.1 The client's email — and why one λ/4 section dies (0:00–0:08)

Slide cue: the email. *"12.5 Ω to 50 Ω, 20 dB return loss, 2–4 GHz, full octave.
Timeline is tight."*

Open with the job, not the theory. This is a real spec shape: a power-amplifier
output at 12.5 Ω (4:1 down from the system's 50), to be matched across a full
octave to 20 dB return loss — |Γ| ≤ 0.1 everywhere from 2 to 4 GHz. Lecture 2 gave
us the quarter-wave transformer and lecture 3 warned us it was a resonance; today
we find out exactly what that warning costs, and what buys it back.

The single-section answer first, with numbers on the board. Z₁ = √(Z₀Z_L) =
√(50·12.5) = 25 Ω, a quarter wave at the band center f₀ = 3 GHz. At f₀ it is
perfect by construction. Off f₀ the section is no longer 90°, and the match decays:
at the band edges (2 and 4 GHz) the exact input reflection is |Γ| = 0.351 —
**9.09 dB** of return loss against a 20 dB spec. The 20-dB bandwidth of this
design, measured in hour 3: **17.1% fractional** — the client wants **66.7%**. One
section is four times too narrow. Write the day's three claims on the board and
leave them up:

1. **Bandwidth is bought with sections.** Split the one big impedance step into N
   small ones and the match widens; choose the *split* cleverly (Chebyshev) and
   every section buys ~11.4 dB of in-band return loss.
2. **There is a ceiling, and it is a theorem.** Bode–Fano prices the best match
   any network — with any number of elements — can achieve over a band, from
   nothing but the load's stored energy. Feasibility *before* design.
3. **A resonator's measured Q is not its Q.** The 3-dB width of a swept resonance
   gives the loaded Q; the resonator's own Q hides behind the coupling, and the
   correction factor this week reaches 25×.

Pre-empt the question the schedule-readers are forming: *"why are transformers and
resonators one lecture?"* Because they are the same mathematics facing opposite
directions. A matching network is a resonance you *widen*; a resonator is a
resonance you *treasure*. Q tells the bandwidth of both — lecture 3 planted this,
lecture 8 will spend it (filters are coupled resonators), and today's two halves
are the two directions.

### 1.2 The theory of small reflections — derived twice (0:08–0:20)

The tool that makes multisection design tractable. Setup on the board: N sections,
each a quarter wave at f₀, impedances Z₀ → Z₁ → Z₂ → … → Z_N → Z_L. At each
junction k a **partial reflection coefficient**:

> Γ_k = (Z_{k+1} − Z_k)/(Z_{k+1} + Z_k), all sections θ = βℓ = (π/2)(f/f₀)

**Level 1 — the phasor sum (the fast version).** Pretend each incident wave
reflects once and is done: the wave that reflects at junction k has traveled 2k
sections farther than the one that reflected at the front. Sum the first bounces:

> Γ(θ) ≈ Γ₀ + Γ₁e^{−2jθ} + Γ₂e^{−4jθ} + … + Γ_N e^{−2jNθ}

A Fourier cosine series in disguise — and for the symmetric designs we build
(Γ_k = Γ_{N−k}), it collapses to
Γ(θ) = 2e^{−jNθ}[Γ₀cos Nθ + Γ₁cos(N−2)θ + …], the even-N middle term counting
once. **The design freedom of the whole hour is the choice of the Γ_k.**

**Level 2 — the multiple-bounce series (first principles), framed as explaining
level 1.** Do the honest two-junction problem: total reflection off one section is
the geometric series Γ = Γ₀ + Γ₁e^{−2jθ}(1−Γ₀²)·Σ(−Γ₀Γ₁e^{−2jθ})^n — every term
after the first-bounce pair carries *products* of partial reflections. Level 1 is
exactly this series with all products dropped. So the theory is first-order
perturbation in the step sizes, and its error is second-order: products like
Γ_iΓ_j. Say the warning now, collect on it in 1.4: those products are set by the
**total** impedance ratio, and for Z_L/Z₀ = 4 the total is not small. The theory
will *design* our transformer and then lie to us — measurably — about its ripple.

Common student question to pre-empt: *"why symmetric Γ_k, when the load isn't
symmetric?"* Because |Γ(θ)| of any physical two-sided match must be an even
function about θ = π/2 for a real-impedance load — the mathematics of the cosine
collapse *requires* symmetry, and every classical design (binomial, Chebyshev) has
it. The asymmetry lives in the absolute impedance levels, not the reflection
pattern.

### 1.3 Binomial: the maximally flat split (0:20–0:30)

First design: make Γ(θ) as flat as possible at f₀. Choose the phasor polynomial to
have all its zeros at θ = π/2:

> Γ(θ) = A(1 + e^{−2jθ})^N,  |Γ| = 2^N|A||cos θ|^N,  A = 2^{−(N+1)}ln(Z_L/Z₀)

(using the ln form for A — more accurate than the plain Γ for big ratios, and it
makes the recursion clean). Matching the binomial expansion term-by-term to the
phasor sum gives the design rule — each step is a binomial coefficient's share of
the total log-impedance ratio:

> ln(Z_{k+1}/Z_k) = 2^{−N}·C^N_k·ln(Z_L/Z₀)

Work our job on the board, N=2: steps in the ratio 1:2:1, so Z₁ = 50·(1/4)^{1/4} =
**35.36 Ω**, Z₂ = **17.68 Ω**. Theory band-edge return loss 2^N|A|cos^N(60°):
**15.22 dB** — fails the 20 dB spec. N=3: Z = **[42.04, 25.00, 14.87] Ω**, theory
edge **21.25 dB** — passes on paper; the exact sweep (hour 3's machinery, run while
preparing this lecture) measures **20.42 dB** worst in-band — passes by 0.42 dB,
with the 20-dB bandwidth at 67.9% versus the 66.7% asked. A pass with no margin,
and note the pattern already: exact is *worse* than theory. Hold that thought.

The binomial's personality: superb at center, spendthrift at the edges. All its
polynomial zeros are stacked at f₀, where we needed exactly one of them. A spec
that says "20 dB *everywhere in the band*" doesn't reward flatness at center — it
rewards holding the line at the worst point. That is an equal-ripple job.

### 1.4 Chebyshev: equal ripple, and the recursion (0:30–0:42)

The centerpiece. Let the ripple touch the spec limit many times instead of wasting
margin at center — the polynomial that oscillates in ±1 as long as possible and
then explodes is Chebyshev's:

> T_N(cos φ) = cos Nφ inside; T_N(x) = cosh(N·arccosh x) outside.

Design statement: substitute x = sec θ_m·cos θ. In-band (θ between θ_m and
π − θ_m) the argument stays inside [−1, 1] and |T_N| ripples at ≤ 1; out of band it
explodes. So set

> Γ(θ) = Γ_m e^{−jNθ} T_N(sec θ_m cos θ), Γ_m·T_N(sec θ_m) = ½|ln(Z_L/Z₀)|

where θ_m is the band-edge electrical length. For our octave: θ_m = (π/2)(f₁/f₀) =
60°, so **sec θ_m = 2** — a delightfully clean number that the whole homework runs
on. The design trade in one line: given N, the ripple is Γ_m =
½|ln(Z_L/Z₀)|/T_N(2). Build the table on the board, out loud (T_N(2) by the
recursion T_{N+1} = 4T_N − T_{N−1}: 2, 7, 26, 97):

| N | T_N(2) | Γ_m | theory RL |
|---|---|---|---|
| 1 | 2 | 0.3466 | 9.20 dB |
| 2 | 7 | 0.0990 | **20.09 dB** |
| 3 | 26 | 0.0267 | 31.48 dB |
| 4 | 97 | 0.0071 | 42.92 dB |

Two readings. First: **theory says N=2 clears the client's 20 dB — by 0.09 dB.**
Second: T_N(2) = cosh(N·arccosh 2) ≈ ½e^{1.317N}, so each section multiplies the
ripple down by e^{1.317} — **11.44 dB per section**, asymptotically. Compare
binomial at N=3: 21.25 dB theory versus Chebyshev's 31.48 — the equal-ripple
dividend is ~10 dB at the same hardware. (The homework's first prediction question
lives in this table; do not solve it aloud.)

Now the recursion that turns Γ_m into copper. Expand T_N(sec θ_m·cos θ) into
cosine multiples and match against 2[Γ₀cos Nθ + Γ₁cos(N−2)θ + …] term by term.
For N=2: T₂(sec θ_m cos θ) = sec²θ_m(1 + cos 2θ) − 1, so 2Γ₀ = Γ_m sec²θ_m and
Γ₁ = Γ_m(sec²θ_m − 1) — the middle term once, not twice. Then step the impedances:
ln(Z_{k+1}/Z_k) = 2Γ_k, **signs down** for our descending load. Work it: Γ_m =
0.0990, sec² = 4 → Γ₀ = 0.198, Γ₁ = 0.297, and Z₁ = 50e^{−0.396} = **33.65 Ω**,
Z₂ = **18.57 Ω** (endpoint check: 18.57·e^{−0.396} = 12.50 ✓). The self-check that
survives every algebra slip: 2ΣΓ_k = ln(Z_L/Z₀) = −1.386, exactly.

**And now collect on 1.2's warning.** The exact ABCD sweep of this N=2 design —
the cascade is lecture 4 material, the numbers are hour 3's — measures worst
in-band return loss **18.98 dB**. The theory that designed it promised 20.09. The
spec is *missed by a full dB*, and the honest minimum for this client is **N=3**:
sections [40.40, 25.00, 15.47] Ω, exact worst in-band **29.44 dB**, real margin.
The gap between promise and measurement grows with N — +0.11, +1.10, +2.04,
+3.70 dB for N = 1…4 — and *why* it grows even as the individual steps shrink is
homework question Q4. The war story below is the same lesson at production scale.

War story, 60 seconds: a 16:1 octave transformer for a broadband antenna feed,
section impedances taken straight from a textbook table, machined beautifully,
measured 3 dB shy of the table's ripple. A week was spent blaming the machinist and
the connectors. The machining was fine; the *table* was the small-reflection
approximation, and 16:1 is not a small reflection. The theory is a designer, not a
verdict. The verdict is a sweep — which is why this course made you build the
cascade machinery two lectures before handing you a design theory that needs
auditing.

### 1.5 Tapered lines in one picture, and the hour's recap (0:42–0:50)

Slide cue: the taper picture — staircase dissolving into a ramp.

Let N → ∞ at fixed total length and the staircase becomes a **taper**: Z(z)
continuous, reflections everywhere, integrated by the same small-reflection logic
(the sum becomes ∫e^{−2jβz}·d(ln Z)/dz·dz — a Fourier transform of the taper
profile; every taper's |Γ(f)| is the spectrum of its impedance slope). Three
profiles to recognize on sight: **exponential** (constant d(lnZ)/dz — simple,
sidelobes high), **triangular** (smoother ends, first sidelobe lower, main lobe
wider), **Klopfenstein** (the Chebyshev limit — equal-ripple above a cutoff,
shortest taper for a given ripple; the industry's default). The taper's virtue is
not magic bandwidth — it is that above its cutoff frequency it *never* stops
working: a high-pass match, where multisections are band-pass. Its price: length.
A Klopfenstein doing our 20 dB job needs roughly a half-wavelength-plus at the
*lowest* frequency; three λ/4 sections at 3 GHz are shorter. That is the whole
trade, and one slide is all it needs — the mathematics is Pozar §5.8, assigned,
not lectured.

Recap, three sentences: one λ/4 section is a 17% device on a 67% job; the theory
of small reflections turns section choice into polynomial choice — binomial hoards
margin at center, Chebyshev spends it evenly and buys 11.4 dB per section; and the
theory that designs the transformer under-reports its ripple at big ratios, so the
sweep, not the formula, signs the datasheet. Hour 2: the ceiling above all of this,
and then the opposite trade — the resonances we keep.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: the Bode–Fano ceiling, and resonators (1:00–1:50)

### 2.1 Bode–Fano — the physics ceiling on any match (1:00–1:16)

Reframe the hour-1 game: sections bought bandwidth, and nothing yet said where —
or whether — the buying stops. It stops. For a load that stores energy, Fano
(1950, building on Bode) proved a hard integral bound. For the canonical parallel
R-C load:

> ∫₀^∞ ln(1/|Γ(ω)|) dω ≤ π/(RC)

Derivation in outline, honestly labeled as outline (Pozar §5.9 / Fano's thesis for
the full account): ln(1/|Γ|) of any passive reflection is constrained by analyticity
— |Γ(s)| is determined on the whole jω axis by its zeros in the right half-plane,
and the load's RC fixes the high-frequency asymptote of Γ through the energy its
capacitor must store. The integral of match quality over *all* frequency is
therefore capped by the load alone: **a budget, issued by the load, spendable
anywhere, totaling π/RC.**

Read it as an engineer, on the board. You want |Γ| = Γ_m flat across Δω and don't
care elsewhere (spend nothing out of band — |Γ| = 1 there). The bound becomes:

> Δω·ln(1/Γ_m) ≤ π/(RC)

Every word of the client's email is now one factor: Δω is the octave, Γ_m is the
20 dB, RC is the load's honesty. Numbers, for our 12.5 Ω load with pad capacitance
C (hour 3 prints all of these):

- C = 2.2 pF (the client's respun board): best conceivable RL over 2–4 GHz =
  **78.96 dB**. The spec is physics-feasible; the remaining problem is ours.
- C = 10 pF (the client's first board): best conceivable RL = **17.37 dB**. The
  20 dB spec is not difficult. It is **impossible** — no network, no N, no genius.
- The largest C that keeps 20-dB-over-an-octave physical: **8.686 pF**.

Say the career skill plainly: *"your boss's spec violates a theorem"* is a
sentence that ends meetings — if you can compute it. The negotiation has exactly
three exits, one per factor: narrow Δω, relax Γ_m, or fix the load (shrink C).
Homework Q3 makes you write that email with numbers in it.

Two fine-print items, pre-empted because sharp students always raise them. First:
*"can I reach 78.96 dB with a real network?"* No — the bound assumes infinitely
many lossless elements and a brick-wall |Γ|; real finite networks waste budget on
sloped skirts. The bound separates *impossible* from *conceivable*; it never
promises *achievable*. Second: *"our transformer load was pure 12.5 Ω — where's
its ceiling?"* C = 0 → π/RC = ∞: no ceiling, which is precisely why hour 1 could
buy bandwidth indefinitely with sections. Bode–Fano bites loads that store energy;
a resistor doesn't. (And a real PA pad always does — hence the client's three load
models.)

### 2.2 Resonators — RLC near resonance, and Q derived twice (1:16–1:30)

Turn the trade around: hour 1 fought resonance to widen a band; the rest of the
course *builds* with resonance — filters (L8–9) are coupled resonators, oscillators
(L12) are resonators with gain, and this week's homework client wants their
oscillator's resonator qualified.

Series RLC on the board: Z_in = R + jωL + 1/(jωC), resonant at ω₀ = 1/√(LC). Near
resonance, ω = ω₀ + Δω:

> Z_in ≈ R + j·2L·Δω = R(1 + j·2Q_u·Δω/ω₀)

The parallel RLC is the exact dual (Y_in ≈ G(1 + j2Q_uΔω/ω₀)) — one algebra, two
circuits, and *every* single-mode resonator near resonance is one of the two. That
is why the homework can hand you three wildly different resonators and one
extraction method.

**Q, level 1 — energy bookkeeping (the fast version).**

> Q = ω₀ · (average energy stored)/(power dissipated)

For the series circuit: Q_u = ω₀L/R = 1/(ω₀RC). Subscript u — **unloaded** — the
resonator alone, its own losses only.

**Q, level 2 — pole location (first principles), framed as explaining level 1.**
The circuit's natural response is the pole pair s = −α ± jω_d with α = R/2L: ring
the resonator and its energy decays as e^{−2αt} = e^{−ω₀t/Q_u}. Q counts radians
of ringing until the energy is down 1/e — Q_u = ω₀/2α. Fourier-transform that
decaying ring and you get the Lorentzian whose **half-power full width is Δω =
ω₀/Q** — the 3-dB method is nothing but reading the pole's real part off a
spectrum. Every Q-measurement trap in 2.4 is a way of corrupting that innocent
sentence.

Numbers to carry (they are the homework's three datasets in disguise): microstrip
resonators live near Q_u ~ 100–200 (radiation + conductor + FR-4's tan δ), coax
near 500–1000, machined cavities 10⁴ and up. When someone quotes "Q = 20,000" for
a printed resonator, someone is wrong.

### 2.3 Transmission-line resonators — λ/2 and λ/4 (1:30–1:38)

Where microwave resonators physically come from: lecture 2's standing waves, now
kept on purpose. An open-ended λ/2 line looks, near its resonance, exactly like the
series... no — *parallel* RLC (test the class: at ℓ = λ/2 the open reflects to an
open, current node at the ends, impedance maximum — parallel-type). A shorted λ/4
line: also parallel-type at its fundamental; the shorted λ/2 is series-type. The
mapping every time: compute Z_in(ω₀ + Δω), expand the tangent, pattern-match
against R(1 + j2QΔω/ω₀) — lecture 2's tangent transformation doing resonator duty.

The result worth boxing, from the expansion of a low-loss shorted λ/2 line
(Z_in = Z₀(αℓ + jπΔω/ω₀)):

> Q_u = β/(2α) — the line's phase constant over twice its loss.

Read it: Q is *stored wave per lost wave*, and it prices technologies instantly.
Copper microstrip on FR-4 at 2.5 GHz: α ≈ 2–3 dB/m dominated by tan δ → Q ~ 10².
Air-dielectric coax: Q ~ 10³. A silver-plated cavity (α from wall currents only):
Q ~ 10⁴. Those are the homework's datasets A, B, C — synthetic, but their Q's are
cast from these technologies.

Pre-empt: *"why λ/4 resonators at all, if λ/2 does the same?"* Half the copper,
and the shorted end is a free heat sink and mechanical anchor — the workhorse of
combline filters. The λ/2's virtue is no ground via. Technology choices, not
physics.

### 2.4 Coupling — Q_u, Q_L, Q_e, and how measurements lie (1:38–1:48)

The uncomfortable truth that fills the last ten minutes: **you cannot measure Q_u
directly**, because measuring means coupling, and coupling adds loss. The probe,
loop, or gap that lets energy in also lets it out.

Definitions, boxed:

> 1/Q_L = 1/Q_u + 1/Q_e — loaded, unloaded, external.
> Coupling coefficient κ = Q_u/Q_e; critical coupling κ = 1.

What a swept |S21| of a transmission-coupled resonator hands you: the 3-dB width
of the resonance gives **Q_L** — resonator *plus* instrumentation. The peak
transmission tells you how much the instrumentation is: for symmetric coupling,

> |S21(f₀)| = 1 − Q_L/Q_u  ⇒  Q_u = Q_L/(1 − |S21(f₀)|), |S21| **linear**.

Read the two limits aloud. Weak coupling: |S21(f₀)| → 0 (huge insertion loss),
Q_L → Q_u — the honest but noisy regime. Strong coupling: |S21(f₀)| → 1 (tiny
insertion loss), and Q_L collapses far below Q_u — the resonance looks *wide* not
because the resonator is bad but because your test set is soldered to it. A
resonator showing 0.35 dB of insertion loss at resonance has |S21| = 0.96: its
unloaded Q is **25× its measured 3-dB Q**. That factor-of-25 is dataset C of the
homework, and it is also this:

War story, 90 seconds: a lab qualifies a filter cavity — spec Q_u ≥ 8000. The
technician sweeps it with two healthy coupling loops (nice deep trace, low
insertion loss, beautiful SNR), reads the 3-dB width, computes Q = 500, and fails
the batch. Two weeks of supplier escalation later someone asks for the insertion
loss at resonance: 0.4 dB. The loops the technician chose *for good SNR* were
loading the cavity by a factor of 20; Q_u was ~11,000 and the batch was fine. The
probe is part of the circuit. Every Q ever measured is Q_L; Q_u is *inferred*, and
the inference needs |S21(f₀)| — which is why hour 3's deliberate bug, and the
homework's trap dataset, both hinge on one skipped correction. Corollary for
honest reports: **a Q quoted without its coupling is not a measurement.**

### 2.5 Hour recap (1:48–1:50)

Bode–Fano issues each load a match budget of π/RC — spend it over Δω at depth
ln(1/Γ_m), and 10 pF of pad capacitance makes the client's spec a theorem
violation (17.37 < 20 dB); resonators are all RLC near resonance, Q = ω₀/2α is a
pole's real part read three ways; and every swept Q is Q_L, with Q_u recovered
only through 1 − |S21(f₀)| — a correction worth 25× this week. Hour 3 makes all
of it print.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the designer, the ceiling, and the Q-meter (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. Narrate while
typing; every claim from hours 1–2 becomes a printed number.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.x, matplotlib
3.10.x, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed pre-class pairs up
now — do not debug installs live. (This week's check also fits a planted resonator
with `skrf.qfactor.Qfactor` — if that smoke test passed, the whole lab will run.)

### 3.2 One quarter-wave section, measured (2:03–2:10)

Cell 3.2: the exact ABCD cascade sweep (ten lines — lecture 4's cascade, typed
fresh to demystify it) applied to the single 25 Ω section. Prints: worst in-band
RL **9.09 dB**, 20-dB fractional bandwidth **17.1%** against the client's 66.7%.
Say it as hour 1 did: one section is a 17% device on a 67% job — now we buy
sections.

### 3.3 The Chebyshev designer (2:10–2:20)

Cell 3.3: `cheb_t` (the polynomial, valid outside |x| ≤ 1), θ_m = 60°, sec θ_m =
2, and the design table prints: theory RL 9.20 / **20.09** / 31.48 / 42.92 dB for
N = 1–4, with the section impedances — N=2 [33.65, 18.57], N=3 [40.40, 25.00,
15.47]. The recursion is eight lines: expand T_N(2cos θ) in cosine multiples
(numerically — a least-squares projection; the N ≤ 3 identities from the slides
work too, and the homework accepts either), halve every coefficient except the
middle, step the logs. Point at 25.00 in the N=3 row: the middle section of any
odd-N symmetric design is √(Z₀Z_L) — the single-section transformer, now wearing
bodyguards.

### 3.4 The sweep — theory meets the exact cascade (2:20–2:30)

Cell 3.4, the hour's centerpiece. Sweep all four designs exactly; the table prints
theory vs measured: **N=2 promises 20.09, measures 18.98 — the spec is missed**;
N=3 measures 29.44 with real margin; the gap column grows +0.11 → +3.70 dB. Let
the class sit with the N=2 line for ten seconds; this is the war story's 3 dB in
miniature, and the homework's Q4. Then the referee: scikit-rf rebuilds the N=3
cascade from `DefinedGammaZ0` media, `line()`, `renormalize(50)`, and the `**`
operator — an implementation sharing zero code with ours — and agrees to
**1.1e-15** in |Γ|. Two independent implementations, one answer: the lecture-1
referee principle, now on a design instead of a budget.

### 3.5 The Bode–Fano budget calculator (2:30–2:36)

Cell 3.5: four lines of physics, then the client's three loads: C = 0 → no
ceiling; 2.2 pF → **78.96 dB**, feasible; 10 pF → **17.37 dB**, impossible —
renegotiate. Largest physical C: **8.686 pF**. Point at the impossible line: this
number ends arguments *before* three weeks of tuning, which is the entire value of
knowing a theorem. Note for the transformer modules: our design load was C = 0 —
no theorem was harmed in hour 1.

### 3.6 A resonator on the bench (2:36–2:42)

Cell 3.6: synthesize a clean transmission resonance — f₀ = 3 GHz, planted Q_u =
500, coupling diameter |S21(f₀)| = 0.5 — and extract Q the honest way: peak, half
power = peak/√2, interpolated crossings, **Q_L = 250.0**. Then the second referee:
`skrf.qfactor.Qfactor` (import from `skrf.qfactor` — the top-level alias is
deprecated), MAT 58's NLQFIT6 fit: **Q_L = 250.0, Q₀ = 500.0** via
`Q_unloaded(res, A=1.0)`. The fit uses all 801 complex points; our ruler used
three magnitudes. Same answer here — the homework's noisy datasets show where the
two methods start to differ, and by how much (spoiler: under 2%, if the crossings
are interpolated).

### 3.7 Deliberate bug — reporting Q_L as Q_u (2:42–2:46)

Cell 3.7, the bug hours 1–2 promised: take 3.6's perfectly correct Q_L = 250 and
*report it as the resonator's Q*. Nothing crashes; 250 is a plausible Q. Then the
fix prints: Q_u = Q_L/(1 − |S21(f₀)|) = 250/(1 − 0.50) = **500** — off by exactly
the coupling, ×2 here, **×25** on the homework's cavity. Second sting in the same
cell: the formula wants |S21| *linear*; feed it the dB value and you divide by
(1 − (−6.02)) and invent a nonsense Q. The habits: quote the coupling next to
every Q, and label every magnitude linear-or-dB — lecture 1's naming discipline,
back for its second collection.

### Homework brief (2:46–2:49)

`lab/HOMEWORK.md` on screen. The story: one client email, three hidden questions —
is the spec physical (module 1: Bode–Fano verdict on three load models), design
the match (module 2, the core: minimum N, the recursion, the sweep — expect the
minimum-N answer to have two layers, and reconcile them), read the bench sweeps
honestly (module 3: 3-dB plus coupling correction, refereed by `Qfactor`, one trap
planted). **Predictions first:** Q1 (what doubling N buys) and Q2 (dataset C's
trap) are answered *before* running. `--check` prints facts, not PASS/FAIL; the
edge cases are surfaced in the homework sheet — read them before coding, they are
the debugging hours you get back. Budget ≤ 3 hours; AI use assumed — you own the
contracts and the reconciliations.

### Wrap-up (2:49–2:50)

Recap against the three claims: sections bought bandwidth at 11.4 dB each, and the
sweep — not the theory — signed the design (N=3, 29.44 dB); Bode–Fano priced the
ceiling and condemned one load model by theorem (17.37 dB < spec); and every
measured Q was Q_L, one correction away from the truth, ×25 in the worst case.
Teaser: next lecture the impossibility theorem for three-ports — matched,
reciprocal, lossless: pick two — and the resistor that buys a Wilkinson divider
its isolation.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 3 (*Networks*), ch. 7 (matching,
  incl. multisection and tapered) — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, §§5.5–5.8 (multisection transformers,
  tapers), §5.9 (Bode–Fano), ch. 6 (resonators) — for owners of the book.
- Fano, "Theoretical Limitations on the Broadband Matching of Arbitrary
  Impedances," *J. Franklin Inst.* 249 (1950) — the ceiling's source paper
  (skim §1–2; the course uses Pozar's/Steer's treatment).
- Gregory, "Q-factor Measurement by using a Vector Network Analyser," NPL Report
  MAT 58 (2021) — free: https://eprintspublications.npl.co.uk/9304/ — the method
  inside `skrf.qfactor.Qfactor`, and the best modern reference on Q extraction.
- [R4] Orfanidis, *Electromagnetic Waves and Antennas*, chs. 12–13 (multisection
  and Chebyshev designs, alternative derivations) — free:
  https://www.ece.rutgers.edu/~orfanidi/ewa/
