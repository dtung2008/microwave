# Lecture 11 — Amplifier Design & the LNA

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (course venv: numpy 1.26.4, scipy, matplotlib,
scikit-rf 1.13.0; **Python 3.12, exactly**)
**Prerequisites:** lectures 3 (Smith chart, L-sections), 4 (S-parameters,
signal-flow graphs, the invariant suite), 10 (noise figure, Friis's cascade).
**Pre-class setup:** run `lab/setup_check.py` → `SETUP OK`; **and step 0**:
download the Mini-Circuits PGA-103+ S-parameter zip (browser; link in
`lab/README.md`), extract `PGA-103+_5V_Plus25DegC.s2p` into `lab/`. Everything
degrades gracefully to a labeled synthetic device if the download fails — but
this is the course's week of *measured reality*, so do the download.

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the transistor as a two-port, and the gain zoo (0:00–0:50)

### 1.1 Why this lecture exists (0:00–0:08)

Slide cue: the receiver chain from lecture 10, with the first block — "LNA,
NF = 1 dB, G = 15 dB" — circled in red.

Open with the promotion: for ten lectures the amplifier has been a *box with
two numbers on it*. Lecture 10 proved those two numbers rule the whole
receiver — the first stage's noise is paid in full, and its gain divides
everyone else's sins. Today the box opens. By the end of hour 3 you will have
taken a real transistor amplifier — a part you can buy for a few dollars,
whose measured S-parameters you downloaded from the vendor — and walked the
entire design of a 2.4 GHz low-noise amplifier around it.

Three claims for today — write them on the board and leave them up:

1. **We design amplifiers from measured S-parameters, not from transistor
   physics.** A two-port file is a complete contract for linear design — and
   today you'll also learn exactly where that contract cracks.
2. **|S₂₁|² is not "the gain."** There are three gains — G_T, G_A, G_P — and
   |S₂₁|² is merely G_T into 50 Ω terminations. Matching networks, which are
   passive and lossless, will *buy* you the difference. On today's device the
   purchase is worth 0.54 dB; on this week's synthetic understudy, 3.3 dB.
3. **Stability is a promise about every passive termination — at every
   frequency, not just yours.** The single most expensive amplifier mistake
   in industry is checking stability only at the design frequency.
   Oscillators get built at the frequency you ignored. Hour 3 builds one,
   on purpose, out of this week's actual device.

Pre-empt the question the digital and device-physics students are forming:
*"where's the transistor model — g_m, C_gs, all that?"* Answer honestly: not
in this course, and mostly not on the RF bench either. Below ~10 GHz on a
mature process, the vendor's measured S-parameters at your bias point *are*
the device, and every formula today consumes them directly. The physics
matters when you design the transistor; we are designing *around* it.

### 1.2 The measured two-port — and when the worldview cracks (0:08–0:18)

Slide cue: the first lines of the actual .s2p file — comment header, `# Hz S
dB R 50`, and the wall of numbers.

Show the part: the **PGA-103+**, a Mini-Circuits MMIC (monolithic microwave
integrated circuit) LNA in a SOT-89 — an E-PHEMT with internal feedback,
0.05–4 GHz, about two dollars. The datasheet says: gain 11.0 dB and NF 0.9 dB
at 2 GHz, 8.1 dB and 1.2 dB at 3 GHz, bias +5 V at 97 mA. The vendor also
publishes what lecture 4 taught you to demand: **measured S-parameters** —
660 frequency points, 10 MHz to 20 GHz, a PNA-X network analyzer, the test
board named in the header. Eighteen files in the zip: six bias voltages,
three temperatures. Each is a different linear device.

Say what the file *is*: a complete description of the device's linear,
small-signal behavior at that bias and temperature. Every design quantity
today — gain ceilings, stability verdicts, match targets — is a formula
evaluated on those 660 rows. That is the whole method: **read the file,
compute, design, verify.**

And say where it cracks, because engineers who don't know this ship failures:

- **Large signals.** S-parameters are the small-signal limit; at P_1dB
  (+22.5 dBm out for this part) the "linear two-port" is a fiction.
  Compression and IP3 (lecture 10) live outside the file.
- **Other bias, other temperature.** That's why the zip has 18 files. μ at
  3 V is not μ at 5 V.
- **Outside the measured band.** The file stops at 20 GHz and *starts at
  10 MHz* — and your bias network lives below 10 MHz. The file cannot clear
  what it cannot see.
- **Noise.** A Touchstone .s2p carries *no noise data* — S-parameters are
  deterministic. Noise needs four extra numbers per frequency (§2.3); this
  week's set is instructor-modeled and labeled as such.

### 1.3 The gain zoo — from the signal-flow graph (0:18–0:36)

Board work; this is lecture 4's investment paying out.

Set the scene: device S between a source of reflection Γ_S and a load Γ_L.
Not 50 Ω — that's the whole point. The matching networks you'll build present
the device with whatever Γ_S, Γ_L you choose; the design question is what to
choose.

**Fast version — the three definitions.** Power available from the source
P_avs; power delivered to the input P_in; power available at the output
P_avn; power delivered to the load P_L. Then:

> G_T = P_L / P_avs (transducer gain — what the amplifier *does for you*)
> G_A = P_avn / P_avs (available gain — input side fixed, output promised)
> G_P = P_L / P_in (power gain — output side fixed, input forgiven)

G_T is the honest one: it charges you for both mismatches. G_A depends only
on Γ_S — which is exactly why LNA design (where Γ_S carries the noise) runs
on G_A. And |S₂₁|² is G_T in the special case Γ_S = Γ_L = 0. The datasheet's
"gain 11.0 dB" is a 50 Ω test fixture number — it is |S₂₁|², nothing deeper.

**First-principles version — Mason on the two-port flow graph.** Draw the
flow graph: nodes a₁, b₁, a₂, b₂; branches S₁₁, S₂₁, S₁₂, S₂₂; the load
closes b₂ → a₂ with Γ_L; the source injects b_s and closes b₁ → a₁ with Γ_S.
One loop matters first: S₂₂Γ_L. Apply the one-loop rule from lecture 4 to
the reflection seen looking into port 1:

> Γ_in = S₁₁ + S₁₂S₂₁Γ_L / (1 − S₂₂Γ_L)

Read it aloud, term by term: the direct reflection, plus a wave that went
*through* the device, bounced off the load, and leaked *back through* S₁₂.
That second term is the seed of everything in hour 2 — stability lives in it.
Chasing the full graph (three loops, one forward path — do it slowly once)
gives the master formula:

> G_T = (1 − |Γ_S|²) |S₂₁|² (1 − |Γ_L|²) / ( |1 − Γ_inΓ_S|² |1 − S₂₂Γ_L|² )

Sanity-check the limits live: Γ_S = Γ_L = 0 → G_T = |S₂₁|². |Γ_S| → 1 →
G_T → 0 (a reactive source delivers nothing). Every factor is a mismatch
tax or a mismatch refund.

Now the number that motivates the whole hour, from the actual file at
2.4 GHz: |S₂₁|² = **9.685 dB**. The best any lossless matching can do (the
ceiling, once we've earned it in §2.2): **10.227 dB**. The gap — 0.54 dB — is
power the bare device *reflects* at its ports; matching is how you stop
throwing it away. Free gain, no transistor changed. On the synthetic
understudy device the same gap is 3.33 dB — bare transistors, unlike
internally-matched MMICs, leave serious money on the table.

Pre-empt the misconception (planted in lecture 4, collected now): *"so S₂₁
is the gain, right?"* — Only into matched terminations. The homework's
checker prints |S₂₁|², MSG, and MAG side by side at f₀ precisely so the
three-way distinction becomes muscle memory.

### 1.4 Stability — where oscillation physically comes from (0:36–0:48)

Stare at Γ_in again: Γ_in = S₁₁ + S₁₂S₂₁Γ_L/(1 − S₂₂Γ_L). Everything
dangerous is in the second term. S₁₂ is the *reverse* path — output voltage
leaking back to the input through the device (in a FET, mostly the gate-drain
capacitance). The forward path S₂₁ amplifies; the load Γ_L reflects; S₁₂
closes the loop. For some passive loads the second term can grow until
**|Γ_in| > 1**: the input port then *reflects more than arrives* — negative
resistance. Attach any resonator (a bias choke, a cable length, the next
stage's filter) and you have built an oscillator. This is not exotic: hour 3
will exhibit a passive load with |Γ_L| = 0.40 that drives this very device to
|Γ_in| = 1.061 — at 10 MHz, a frequency your 2.4 GHz bench never displays.

Definitions, said precisely: a two-port is **unconditionally stable** at a
frequency if |Γ_in| < 1 and |Γ_out| < 1 for *every* passive source and load
(|Γ_S|, |Γ_L| ≤ 1). Otherwise it is **conditionally stable**: some passive
terminations oscillate, and your safety depends on never presenting them —
at any frequency, including the ones you never look at.

Two tests, both computed from the file alone:

> K = (1 − |S₁₁|² − |S₂₂|² + |Δ|²) / (2|S₁₂S₂₁|), Δ = S₁₁S₂₂ − S₁₂S₂₁
> Unconditional ⇔ K > 1 **and** |Δ| < 1 (two conditions — Rollett)
>
> μ = (1 − |S₁₁|²) / ( |S₂₂ − Δ·conj(S₁₁)| + |S₁₂S₂₁| )
> Unconditional ⇔ μ > 1 (one condition — Edwards–Sinsky, 1992)

The theorems are equivalent — K > 1 with |Δ| < 1 *if and only if* μ > 1 —
and the homework makes your code prove it at all 660 frequencies. Why
industry moved to μ: it is a single number, and (hour 2 shows) it is a
*distance* — μ = 1.23 means every unstable load is at least 0.23 away from
the chart center; K = 1.10 means "yes," with no ruler attached.

The device at 2.4 GHz: **K = 1.0973, |Δ| = 0.5499, μ = 1.2254.**
Unconditionally stable at f₀ — barely. Hold that "barely."

War story, 60 seconds: a 2 m ham-band preamp — E-PHEMT, gorgeous NF —
that oscillated at 40 MHz, but only with certain antennas, only on cold
mornings. The stability audit had been run at 144 MHz. At 40 MHz the
device's gain was 10 dB higher and μ was 0.5; the antenna's out-of-band
reflection walked into the unstable region as the cable contracted. The fix
was one resistor — and the lesson is a *sweep*, not a spot check.

### 1.5 Hour recap (0:48–0:50)

Three sentences, then break: the .s2p file is the device — complete for
linear design, silent about large signals, other bias, and noise; G_T is the
honest gain and |S₂₁|² is only its 50 Ω special case — matching buys the
difference up to a ceiling; and stability is a promise about every passive
termination, tested by K–Δ or by μ, whose violation is an oscillator you
didn't order. Hour 2 draws all of this on lecture 3's chart — and prices it.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: circles on the chart, and the LNA procedure (1:00–1:50)

### 2.1 Stability circles, and μ as a distance (1:00–1:14)

The condition |Γ_in| = 1 is one equation in the complex Γ_L plane. Set
|S₁₁ + S₁₂S₂₁Γ_L/(1 − S₂₂Γ_L)| = 1 and grind (or remember lecture 3: bilinear
maps send circles to circles). The boundary is a circle — the **load
stability circle**:

> C_L = conj(S₂₂ − Δ·conj(S₁₁)) / (|S₂₂|² − |Δ|²), R_L = |S₁₂S₂₁| / | |S₂₂|² − |Δ|² |

Swap ports (1↔2) for the source circle. On one side of the circle |Γ_in| < 1;
on the other, > 1. Which side is safe? The center of the chart answers it:
Γ_L = 0 gives Γ_in = S₁₁, and |S₁₁| < 1 here, so *the origin's side is the
stable side.*

Now the beautiful part — the geometric meaning of μ. At 10 MHz, where this
device is worst, the load circle has |C_L| = 1.718 and R_L = 2.012: a huge
circle that *swallows the chart center*, whose rim passes 0.294 from the
origin. That distance — from chart center to the nearest unstable load — **is
μ**. Not an analogy; Edwards and Sinsky's theorem, and the homework's harness
referees your μ formula against exactly this circle geometry (they agree to
1e-14). μ = 0.294 at 10 MHz says: a passive load 0.294 from center can start
an oscillation. μ = 1.2254 at 2.4 GHz says: the nearest killer load is 0.225
*outside* the unit circle — no passive load reaches it. One number, with a
ruler built in.

The audit culture, stated as a rule: **you sweep μ over the entire file,
every design, every time.** This device: μ < 1 over 10–110 MHz (worst 0.294)
*and again* over 15.1–16.8 GHz (worst 0.710). The second band surprises
everyone — gain is long gone up there; it's |S₂₂| swelling out of band
(package resonance territory) that collapses the margin. The homework's Q1
asks you to predict the bands before you sweep; expect to get the low band
right and learn something from the high one.

What "conditionally stable" costs you: nothing, *if* you can guarantee the
terminations. In-band that's your own matching network — controllable. Out of
band it's whatever the antenna, the bias tee, and the next stage present —
not controllable. Hence the standard medicine, named now, prescribed in
Steer/Pozar: a small series or shunt resistor where it hurts noise least, or
feedback — trading a fraction of a dB of gain for μ > 1 everywhere. This
week you design at a frequency where the device is already unconditional;
the audit is how you *know* that, and the resistor discussion is your
ANSWERS.md epilogue.

### 2.2 Designing for gain — the match, the ceiling, and 2 dB of humility (1:14–1:28)

Where does maximum gain live? Make both ports simultaneously conjugate-
matched: Γ_S = conj(Γ_in) *and* Γ_L = conj(Γ_out), solved together (each
side's match moves the other's target — the S₁₂ coupling again). The closed
form, with B₁ = 1 + |S₁₁|² − |S₂₂|² − |Δ|², C₁ = S₁₁ − Δ·conj(S₂₂) (and the
port-swapped B₂, C₂):

> Γ_MS = (B₁ − sqrt(B₁² − 4|C₁|²)) / (2C₁), Γ_ML = (B₂ − sqrt(B₂² − 4|C₂|²)) / (2C₂)

(minus root: the one inside the chart — the plus root is its image outside).
Only meaningful where μ > 1; inside a conditionally stable band the
"simultaneous match" chases itself off the chart. At that match:

> G_T,max = MAG = |S₂₁/S₁₂| · (K − sqrt(K² − 1))

**MAG** (maximum available gain) is the design ceiling. For this device at
2.4 GHz: Γ_MS = 0.413∠−160.8°, Γ_ML = 0.360∠+70.4°, MAG = **10.227 dB** —
and the identity G_T(Γ_MS, Γ_ML) = MAG is a line your checker measures at
1e-15. Where K < 1, MAG doesn't exist; datasheets then quote **MSG**
(maximum *stable* gain) = |S₂₁/S₁₂| — the ceiling you would have *after*
stabilizing to exactly K = 1. It is a marketing-adjacent number: this device
"offers" MSG = 12.128 dB at 2.4 GHz, but only MAG's 10.227 is real as-is.
The homework makes you print both and say which is honest where.

Then the twist that separates coursework from practice: **you almost never
design at MAG.** At MAG the margins are zero — component tolerance walks the
match, gain sags, stability margin evaporates (remember "barely" from §1.4).
The homework's target is **MAG − 2 dB**, and the tool for hitting a number
*below* the ceiling is the **constant-available-gain circle**: in the Γ_S
plane, the locus of G_A = target is a circle (centers march along the C₁
direction, radii grow as the target drops). Procedure, boxed:

> 1. Draw the G_A = target circle. 2. Pick a point Γ_S on it — *which* point
> is a free choice, and §2.3 is about spending it. 3. Conjugate-match the
> output: Γ_L = conj(Γ_out(Γ_S)). Then G_T = G_A = target, exactly.

The reference pick when nothing else matters: the circle point nearest the
chart center (gentlest network). The homework verifies your pick by
*cascade*: lecture 3's L-sections realized around the device in skrf, and
|S₂₁|² of the assembled amplifier read at f₀ — target hit to 1e-13 dB, or
your algebra is wrong. The referee is a build, not a formula.

### 2.3 Noise circles — the tension that defines the LNA (1:28–1:40)

Lecture 10 told you *what* NF is. Here is what it *depends on*: the source
match. A two-port's noise figure against source reflection Γ_S is:

> F = F_min + 4·r_n·|Γ_S − Γ_opt|² / ( (1 − |Γ_S|²)·|1 + Γ_opt|² )

Four noise parameters per frequency: **F_min** (the floor), **Γ_opt** (the
source reflection that reaches it), **r_n = R_n/Z₀** (how steeply F rises as
you leave Γ_opt). Constant-F loci are — again — circles, nested around
Γ_opt. Provenance, stated honestly on the slide: .s2p files carry no noise
data; measuring Γ_opt takes a source-pull bench most labs lack. This week's
noise parameters are **instructor-modeled**, calibrated so that F(Γ_S = 0)
reproduces the PGA-103+ datasheet's 50 Ω NF column — teaching data, labeled
as such, exactly like lecture 9's EM case study.

Now the tension. The gain formulas want Γ_S = Γ_MS. The noise formula wants
Γ_S = Γ_opt. **They are different points.** At 2.4 GHz: Γ_MS = 0.413∠−160.8°
but Γ_opt = 0.372∠+75.6° — nearly opposite sides of the chart. You cannot
have both. The numbers, from the model + file:

- Sit at Γ_MS (max gain): G_T = 10.227 dB, but NF = **1.599 dB** — you pay
  0.78 dB of noise over the F_min = 0.820 floor.
- Sit at Γ_opt (min noise, output re-matched): NF = 0.820 dB, but G_T =
  8.794 dB — the noise match costs **1.433 dB of gain**.

Every LNA ever designed lives on the curve between those endpoints. The
homework's module 3 draws that curve — the **gain-vs-NF frontier** — by
walking Γ_S from Γ_MS to Γ_opt with the output re-matched at every step, and
asks you to pick a point and *defend it with Friis*: system NF with a 6 dB
second stage is 2.376 dB at the gain end, 2.045 dB at the noise end — the
noise end wins by 0.33 dB *for this receiver*, and flips if the second stage
is worse than ≈8.7 dB. The LNA is not a component decision; it is a system
decision made at a component. (Notice also — homework Q2 — that this
device's noise match *still clears* the MAG − 2 dB gain target: the dreaded
trade costs less than the humility you had already budgeted. It is common in
practice and nobody tells students.)

### 2.4 Bias in one slide, and the full procedure (1:40–1:48)

Bias, one slide, as promised: the PGA-103+ wants +5 V at 97 mA *through the
output pin* — so the schematic grows an RF choke (feed DC, block RF), two DC
blocks (the S-parameter file's ports are DC-open by convention), and a supply
resistor. Two design rules only: the bias network is *part of the
termination* — a choke is an inductor, inductors resonate, and 10 MHz (where
μ = 0.294, remember) is bias-network country; and the vendor's "suggested
layout" exists because ground inductance eats stability margins. Full bias
design is a lab course; the stability consequences are this course.

The complete single-stage LNA procedure — the checklist the homework
executes end-to-end, boxed on the slide:

> 1. Get measured S (+ noise) data at your bias. 2. Sweep K–Δ *and* μ over
> the whole file; find every μ < 1 band. 3. At f₀: if μ > 1, MAG exists —
> else stabilize first and re-audit. 4. Set the gain target below the
> ceiling (here MAG − 2 dB). 5. Draw G_A circles and noise circles on one
> chart; pick Γ_S on the frontier, knowingly. 6. Γ_L = conj(Γ_out).
> 7. Realize both matches (L-sections here; stubs at higher f). 8. Verify by
> cascade: G_T at f₀, swept response, and *the finished amplifier's* |Γ_in|,
> |Γ_out| over the whole file. 9. Bias without ruining step 8.

Pre-empt the classic misconception, verbatim, because half the class holds
it silently: *"unconditionally stable means the amp is stable at the design
frequency."* No — it means stable for **every passive termination at that
frequency**. It says nothing about 10 MHz. "Stable at f₀, μ-swept nowhere
else" is how the 40 MHz oscillator in hour 1's war story got built — and hour
3 rebuilds exactly that failure with today's device, on purpose.

### 2.5 Hour recap (1:48–1:50)

Stability circles put the danger on lecture 3's chart, and μ is your distance
from it — sweep it over the whole file, always; gain design is a ceiling
(MAG), a humble target (−2 dB), and a circle to pick from; noise adds a
second family of circles centered somewhere else, and the LNA is the art of
standing between the two centers with your eyes open. Hour 3 does all of it
to a real device in about sixty lines of Python — then ships the bug.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: a real .s2p through the whole procedure (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. The device
on screen is whichever `the_device()` finds: the vendor file (if step 0 was
done) or the labeled synthetic fallback — the narration below quotes the
vendor numbers.

### 3.1 Setup + the device (2:00–2:05)

Run cell 3.1: versions, then `the_device()` — the label line is the honesty
check (`vendor: PGA-103+_5V_Plus25DegC.s2p (660 pts, 10 MHz-20 GHz)` or the
`file not found — download step 0 first` fallback). Print S at 2.4 GHz: four
complex numbers. Point at S₂₁ = 2.09 + 2.22j: *that* is what eleven lectures
of machinery consume.

### 3.2 The gain zoo at f₀ (2:05–2:12)

Cell 3.2: K, Δ, μ typed straight from the board, then the three headline
numbers: |S₂₁|² = **9.685 dB**, MSG = **12.128 dB**, MAG = **10.227 dB**.
Narrate the ordering: the 50 Ω number is the floor, the marketing number is
the ceiling-after-surgery, MAG is the real ceiling — and the 0.54 dB between
|S₂₁|² and MAG is what matching will buy. Cross-check against the datasheet
out loud: 11.0 dB at 2 GHz, 8.1 at 3 GHz → ≈9.8 dB interpolated at 2.4;
the file says 9.685. The datasheet's "gain" is |S₂₁|² — now you know.

### 3.3 The whole-band audit (2:12–2:18)

Cell 3.3: the μ sweep, printed and plotted (`walkthrough_mu.png`). Two red
bands appear: **0.010–0.110 GHz (worst μ = 0.294)** and **15.1–16.8 GHz
(worst 0.710)** — with μ(f₀) = 1.2254 comfortably green. Invite predictions
before scrolling: everyone calls the low band (gain rises as f falls);
almost nobody calls the 16 GHz band. Also print the theorem check: K–Δ and μ
verdicts agree at 660/660 points — if your homework prints 659, the bug is
yours, not Rollett's.

### 3.4 Stability circles on the chart (2:18–2:24)

Cell 3.4: load stability circles at the worst frequency and at f₀
(`walkthrough_circles.png`). At 10 MHz the circle swallows the chart center
and its rim passes 0.294 away — *point at it*: that distance is μ, the
Edwards–Sinsky picture made visible. At 2.4 GHz the circle clears the unit
chart by 0.225 — every passive load safe, at this frequency.

### 3.5 The gain design, verified by cascade (2:24–2:32)

Cell 3.5: Γ_MS = 0.413∠−160.8°, Γ_ML = 0.360∠+70.4° from the B/C closed
forms; G_T at that pair prints 10.2268 = MAG to four decimals (the identity
is the algebra audit). Then `build_amp` — lecture 3's L-sections realized in
skrf, cascaded with `**` — and the assembled amplifier's |S₂₁|² at f₀ prints
**10.2268 dB**. Formula, meet hardware-shaped referee. The swept plot
(`walkthrough_amp.png`) shows the price of a one-frequency match: a resonant
gain peak, not a flat line. (Homework module 2 repeats this at MAG − 2 dB,
where the target is a *choice*, not a ceiling.)

### 3.6 The noise trade (2:32–2:38)

Cell 3.6: the instructor-modeled noise parameters at f₀ (say the provenance
line out loud — the .s2p has no noise data), then the two endpoint facts: NF
at the gain match = **1.599 dB** vs F_min = 0.820; G_T at the noise match =
**8.794 dB** vs MAG = 10.227. The 1.433 dB / 0.78 dB tension in two printed
lines — module 3 of the homework turns it into a frontier and makes you
stand somewhere on it.

### 3.7 Deliberate bug — "it's stable at 2.4 GHz, ship it" (2:38–2:44)

Cell 3.7, the re-enactment §1.4 promised. The f₀-only engineer checks
μ(2.4 GHz) = 1.225 > 1 and declares victory. The sweep says worst μ = 0.294
at 10 MHz. Then the kill, constructed live: a **passive** load, |Γ_L| = 0.40,
placed just inside the 10 MHz instability circle → the device's input shows
|Γ_in| = **1.061 > 1**. Negative resistance, at a frequency the 2.4 GHz bench
never displays, reachable by an unlucky bias choke. And the finale: our own
finished amplifier — the one that measured perfectly in 3.5 — has |Γ_in| =
**1.175 at 16.15 GHz**. The amp we just "verified" is a reflection amplifier
out of band. Point at both numbers: *nothing about the f₀ design was wrong;
what was wrong was the frequency axis of the verification.* Sweep μ. Whole
file. Every time.

### Homework brief (2:44–2:48)

`lab/HOMEWORK.md` on screen. The story: your first LNA, on the real part —
step 0 is a vendor download, and the harness tells you honestly which device
you're on. Module 1 is the audit (K/Δ/μ, bands, circles — refereed by skrf's
K, by circle geometry for μ, and by a theorem that must hold 660/660);
module 2 is the core (the MAG − 2 dB design, refereed by a built cascade,
not a formula); module 3 is the frontier and a defended design point.
**Predictions first:** Q1 (where are the μ < 1 bands, and why) and Q2 (what
does moving to Γ_opt cost) are committed before running. `--check` prints
facts, not PASS/FAIL; `--plot` makes the three pictures the questions are
about. Budget ≤ 3 hours; AI welcome — the predictions, reconciliations, and
the Q5 defense must be yours.

### Wrap-up (2:48–2:50)

Recap against the three claims: the file was the device — you designed a real
amplifier without one transistor equation; |S₂₁|² was not the gain — you
printed the zoo and bought the gap with lossless matching; and stability was
a promise about every termination at every frequency — you watched a
perfectly-designed 2.4 GHz LNA go active at 16 GHz, and you know the sweep
that catches it. Next lecture the receiver grows its frequency-translation
stage: mixers, images, and why your radar's IF plan is a chess game against
every emitter in the neighborhood.

---

## References

- [R2] Steer, *Microwave and RF Design*, Vol. 5 (*Amplifiers and
  Oscillators*), chs. 2–3 — free:
  https://repository.lib.ncsu.edu/handle/1840.20/36776
- [R1] Pozar, *Microwave Engineering* 4e, chs. 11–12 (amplifier design;
  noise in ch. 10 backstops lecture 10).
- [R7] Gonzalez, *Microwave Transistor Amplifiers: Analysis and Design* 2e —
  the classic single-topic reference (library copy suffices).
- Edwards & Sinsky, "A new criterion for linear 2-port stability using a
  single geometrically derived parameter," *IEEE Trans. MTT* 40(12), 1992 —
  the μ paper; four pages of the homework's referee.
- PGA-103+ datasheet and S-parameter data, Mini-Circuits —
  https://www.minicircuits.com/WebStore/dashboard.html?model=PGA-103%2B
