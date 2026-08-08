# Lecture 15 — FMCW, Doppler, and Micro-Doppler

**Duration:** 3 hours (three ~50-minute segments, 10-minute break each hour)
**Delivery tier:** A — local pip (`pip install -r requirements.txt`: numpy 1.26.4,
scipy 1.13.1, matplotlib, scikit-rf 1.13.0; **Python 3.12, exactly**; no new
packages this week)
**Prerequisites:** lecture 12 (the mixer — the dechirp receiver's hardware was
built there), lecture 13 (windows/tapers — spectral leakage is about to become
lethal), lecture 14 (CA-CFAR — this week it is imported as plumbing), lecture 1
(the radar equation and the drone problem), signals (the DFT and its bin width).
**Pre-class setup:** `lab/setup_check.py` must print `SETUP OK` (this week's
smoke test dechirps a 60 m target and demands its beat land in FFT bin 120).

Format note: hours 1–2 are principles (board + slides,
`slides/principles.en.html`); hour 3 is tools, live-coded, mirroring
`lab/hour3_walkthrough.py` cell-for-cell. Practice happens in the homework
(`lab/HOMEWORK.md`), not in class.

---

## Hour 1 — Principles I: the chirp, the dechirp, and why bandwidth is resolution (0:00–0:50)

### 1.1 Two radars that cannot do the job (0:00–0:08)

Slide cue: the two broken radars — a CW tone with its phase-ambiguity spiral,
and a pulse radar with its blind zone shaded.

Open with the failure modes, because FMCW is best understood as the repair of
both.

**CW cannot range.** Transmit a pure tone, receive the echo: everything about
range is in the phase 4πR/λ — modulo 2π. At 77 GHz that is range modulo
λ/2 = **1.95 mm**. A CW (continuous-wave) radar is a superb speedometer —
Doppler is a frequency, frequencies are measurable — and a useless rangefinder.
The information problem is fundamental: a zero-bandwidth signal has no time
structure to mark *when* it left.

**Pulse struggles close-in.** Mark time with a pulse instead: range from delay,
τ = 2R/c. But a monostatic radar cannot listen while its transmitter shouts —
a 1 µs pulse blinds the receiver out to cτ/2 = **150 m**. Our parking-lot
drone problem lives entirely inside 150 m. Shorten the pulse to 3 ns and the
blind zone shrinks to 45 cm — but a 3 ns pulse *is* a 300 MHz-wide signal, and
its peak power must carry all the energy detection needs (lecture 14: energy,
not peak power, buys P_d). Close-in radar wants the energy of a long
transmission with the time-marking of a wide bandwidth, transmitted and
received *at the same time*.

Three claims for today — on the board, left up all hour:

1. **The mixer is the ranging engine.** FMCW (frequency-modulated continuous
   wave) marks time with frequency; lecture 12's dechirp mixer turns range
   into a beat tone: f_b = 2Rα_c/c. Range measurement becomes tone
   measurement, and an FFT is the whole receiver.
2. **Bandwidth is resolution: ΔR = c/2B.** Not power — power buys detection
   range (L14); bandwidth buys the ability to *separate*. 300 MHz separates
   half-meters, whatever the transmit power.
3. **The second FFT reads velocity, and the third reads intent.** Chirp
   after chirp, the phase at a target's range bin spins at the Doppler rate:
   a slow-time FFT makes the range-Doppler map — the modern radar's retina.
   And a *long stare* at one cell reads the micro-Doppler comb that tells a
   drone from a bird — same RCS (radar cross section), different machinery.

### 1.2 The chirp on the f–t plane (0:08–0:18)

Slide cue: the f–t diagram — transmit ramp, delayed echo ramp, the constant
vertical gap labeled f_b.

The FMCW transmit signal ramps its frequency linearly: start at f₀, climb
B hertz in T_c seconds, snap back, repeat. Slope **α_c = B/T_c** (course
ledger symbol; the code calls it `alpha`). Today's numbers, which are the
homework's numbers: f₀ = 77 GHz (λ = 3.8934 mm), B = 300 MHz, T_c = 10 µs —
α_c = **3×10¹³ Hz/s**. Thirty terahertz per second; say it once for the
audacity, then never be impressed again.

The echo from range R is the same ramp delayed by τ = 2R/c. Draw both ramps.
At any instant the transmitter is at f₀ + α_c·t; the echo arrives still
carrying f₀ + α_c·(t − τ). The vertical gap between the two lines is
**constant**: α_c·τ. Two parallel ramps, one lag — the entire ranging idea is
this picture.

Now lecture 12's hardware earns its keep: mix the received echo with the
transmit chirp itself — the LO (local oscillator) *is* the waveform. The
cos·cos identity from L12 turns the constant frequency gap into a constant
audio-like beat tone:

> **f_b = α_c·τ = 2Rα_c/c** — range became a frequency.

Numbers on the board: 2α_c/c = **200.14 kHz per meter of range**. The drone
at 25 m beats at 5.0 MHz; the parked airliner's tail at 180 m beats at
36.06 MHz. The transmitted problem was 300 MHz wide; what arrives at the ADC
(analog-to-digital converter) is a tone you could almost hear. Lecture 12
called this "the mixer performed the compression, analog, for free" — today
we spend the winnings.

Pre-empt the question the DSP students are forming: *"why not sample the
300 MHz directly and matched-filter it?"* You could — pulse-compression
radars do (lecture 14's B was inside the noise floor for exactly that
reason). But that needs a ≥600 MS/s converter with real dynamic range;
the dechirp needs 51.2 MS/s (our ADC) because it only ever sees beats up to
α_c·τ_max. FMCW is the poor engineer's matched filter — and the reason a
77 GHz radar costs what a WiFi chip costs.

### 1.3 The dechirp done honestly — the full phase, and the R–v coupling (0:18–0:32)

Board work. The fast version above waved at the geometry; now the
first-principles pass, because a coupling term hides in the algebra and the
homework's referee checks that you kept it.

Write the transmit phase (up-chirp, one chirp, 0 ≤ t < T_c):

> φ_tx(t) = 2π[f₀t + ½α_c t²]

The echo is φ_tx(t − τ). The mixer output's phase is the difference:

> Δφ(t) = 2π[f₀τ + α_c τ·t − ½α_c τ²]

Read the three terms out loud — each one is a feature, not debris:

1. **f₀τ = 4πR/λ (over 2π):** the carrier phase. Constant during one chirp;
   *this term is where Doppler lives across chirps* — hold it for hour 2.
2. **α_c τ·t:** the beat tone, frequency α_c τ = 2Rα_c/c. The fast version's
   answer, recovered.
3. **½α_c τ²:** the residual video phase — for us, α_c τ²/2 at 180 m is a
   few hundred hertz of constant offset; negligible today, and the toolkit
   simulator keeps it anyway because honesty is cheaper than remembering
   what you dropped.

Now let the target move. R(t) = R₀ + v·t, with **v = range rate, receding
positive** — the sign convention the entire course codebase uses from here
through lecture 16 (a closing target has v < 0; its Doppler *shift* is
f_d = 2|v|/λ upward — physics unchanged, bookkeeping fixed once). The
delay τ(t) = 2(R₀ + vt)/c is now itself a ramp, and the beat frequency picks
up the Doppler term:

> **f_beat = 2R α_c/c + 2v/λ** — range and velocity, coupled in one number.

One chirp fundamentally cannot split them. How bad is the contamination?
Hour 3 measures it: the car receding at 20 m/s shifts its apparent range by
**+51.3 mm** (closed form f_d·c/2α_c; the zero-padded FFT measures
+46.8 mm — sub-bin interpolation on a noisy peak). And here is the number
worth a box on the slide: the worst-case coupling *inside the waveform's own
unambiguous velocity window* (±97.3 m/s, hour 2) is **250 mm — exactly half
a range bin, always**. Prove it in one line: coupling in bins =
f_d·T_c = 2vT_c/λ, and v_unamb = λ/4T_c, so at the edge it is ½. The
chirp-sequence waveform is self-protecting: if the velocity is unambiguous,
the range error the coupling can inflict never exceeds half a cell. (Q5 of
the homework makes you run this argument yourself.)

Pre-empt the misconception: *"so the beat spectrum tells me range, up to
this small Doppler shift — where did the Doppler SHIFT of the carrier go?"*
It did not go anywhere: 2v/λ *is* the carrier Doppler, arriving in the beat
because dechirp preserves it. The point is proportions: at 77 GHz the car's
6.06 kHz of Doppler rides on 9.07 MHz of range beat — a 0.07% perturbation
of the frequency but 100% of the velocity information. Hour 2 is about
refusing to throw it away.

### 1.4 Range resolution — the FFT bin *is* the resolution (0:32–0:44)

The claim on every automotive datasheet: ΔR = c/2B. Derive it the honest
way — from the FFT, because that is where it actually comes from.

The ADC collects one chirp for T_c seconds. An FFT of a T_c-long record has
bins **1/T_c wide** — that is not a choice, it is the uncertainty principle
wearing engineering clothes. Two targets separate when their beats differ by
at least one bin:

> Δf_b = 2·ΔR·α_c/c ≥ 1/T_c  ⟹  **ΔR = c/(2 α_c T_c) = c/2B**

Watch what cancelled: T_c is gone. Chirp slower and the bins get finer but
the beat-per-meter drops in exact proportion. The *only* thing left is B.
**Bandwidth is resolution.** Numbers: B = 300 MHz → ΔR = **0.4997 m**. The
77–81 GHz automotive band offers 4 GHz → 3.7 cm — the reason regulators gave
cars that band, and the reason your car can see the curb.

Say the complementary sentence, because it completes lecture 14: power buys
*detection* (SNR, P_d at range), bandwidth buys *separation* (two drones, a
drone next to a car). They are different currencies, and the radar equation
never mentioned B except as a noise tax — lecture 1's Q4 promised this
counter-argument, and here it is.

Bookkeeping that the homework needs (fast, on the slide): with a complex
(I/Q) ADC at f_s = 51.2 MS/s we get N_s = f_s·T_c = 512 samples per chirp,
512 range bins, each 0.4997 m: **unaliased coverage 255.8 m**. The beat at
200 m is 40.03 MHz — inside the 51.2 MHz complex Nyquist with margin. (Real-
sampled ADCs — TI's parts — halve this; our idealized I/Q keeps the algebra
clean, and the homework states the assumption.)

### 1.5 Hour recap (0:44–0:50)

Five sentences, then break. CW has no clock and pulse cannot listen close-in;
FMCW marks time with frequency and listens while it talks. The dechirp mixer
(L12's hardware, promoted to ranging engine) outputs f_b = 2Rα_c/c —
200.14 kHz per meter for our waveform. The full phase expansion keeps a
Doppler term: f_beat = 2Rα_c/c + 2v/λ, and within the unambiguous velocity
window that coupling is at most half a range bin — self-protecting. The FFT
bin width 1/T_c turns into ΔR = c/2B — bandwidth, not power, is resolution.
Hour 2 spins up the second FFT and the drone starts waving.

**Break (0:50–1:00).**

---

## Hour 2 — Principles II: the range-Doppler map, the design triangle, and the drone that waves (1:00–1:50)

### 2.1 Doppler, and the chirp-sequence waveform (1:00–1:14)

Slide cue: the processing cube — a 512×512 matrix of ADC samples; the range
FFT arrow across fast time, the Doppler FFT arrow down slow time.

Doppler at 77 GHz first, as numbers: f_d = 2v/λ = **513.7 Hz per m/s**. The
car at 11.8 m/s: 6.06 kHz. A hovering drone body: 0 Hz. Blade tips at
69 m/s: 35.5 kHz — hold that one.

One chirp gave us a coupled f_beat. The fix is not a cleverer chirp; it is
*more* chirps. Recall term 1 of the phase expansion: each chirp carries
carrier phase 2πf₀τ_n = 4πR_n/λ. From chirp n to chirp n+1, the target moves
v·T_c and the phase advances by 4πvT_c/λ — the beat tone's *phase* spins
chirp-to-chirp at exactly the Doppler frequency 2v/λ. So:

- **Fast time** (within a chirp, 512 samples): FFT → range bins. Everything
  in one range bin, whatever its velocity, lands in the same column.
- **Slow time** (across chirps, 512 chirps): at each range bin, a second FFT
  over the chirp index → Doppler bins. The stationary airliner sits at 0;
  the receding car at +6.06 kHz; and the sampling rate of this second
  dimension is the chirp repetition rate **PRF = 1/T_c = 100 kHz**.

Two FFTs, and the matrix of samples becomes the **range-Doppler map** with
physical axes: range in meters, range rate in m/s. Every automotive radar,
every modern surveillance processor, ends its analog story here. The axes
for our waveform: 512 columns × 0.4997 m, 512 rows × **Δv = λ/2NT_c =
0.3802 m/s**, spanning **±λ/4T_c = ±97.3 m/s**, all from one CPI (coherent
processing interval) of N·T_c = **5.12 ms**.

Derive the two Doppler-axis numbers the same way as range — they are the
same theorem in the second dimension. Resolution: the slow-time record lasts
N·T_c, so Doppler bins are 1/(N T_c) wide → Δv = λ/(2NT_c). Ambiguity:
slow time is *sampled* at PRF, so Doppler is only known modulo PRF →
unambiguous span ±PRF/2 → **v_unamb = ±λ/(4T_c)**. Sampling theory, met in
lecture 12 as "sampling is a mixer too," now pricing what the radar can see.

Pre-empt the sign question before someone asks: *"why is the receding car at
positive Doppler in our maps?"* Convention, fixed by which mixer output you
call I and which Q; the course books v as range rate (receding positive)
because lecture 16's collision logic wants range rate anyway. The physics —
closing targets shift the carrier *up* — is untouched. What matters is that
the toolkit's axis and the planted truth agree, and the referee checks it.

### 2.2 The waveform-design triangle, worked for our radar (1:14–1:28)

Slide cue: the triangle — B, T_c, N at the corners; each edge a trade; the
spec table beside it.

Now design, because this is homework module 1 and the part industry actually
pays for. Three knobs: B, T_c, N. Four demands from the parking-lot spec:

| spec | formula | constraint |
|---|---|---|
| ΔR ≤ 0.5 m | c/2B | B ≥ 299.79 MHz |
| coverage ≥ 200 m at f_s = 51.2 MS/s | f_s·c·T_c/2B | T_c ≥ 7.82 µs |
| v_unamb ≥ ±75 m/s | λ/4T_c | T_c ≤ 12.98 µs |
| Δv ≤ 0.4 m/s | λ/2NT_c | N ≥ 486.7 |

Work it on the board in this order, narrating the tensions. **B** is bought
first and alone: 300 MHz, done — resolution costs nothing but spectrum
license and ADC beat headroom. **T_c is squeezed from both sides** — the
star of the design. Long chirps put more range on the same ADC (coverage
∝ T_c at fixed B and f_s); short chirps sample slow time faster and push the
velocity ambiguity out. The legal window here is **[7.82, 12.98] µs**; pick
the round number 10 µs. **N** buys velocity resolution linearly and pays in
CPI duration: 512 chirps → 5.12 ms and Δv = 0.38 m/s. (Also pays in
migration: a target must stay inside one range cell for the CPI —
ΔR/CPI = 97.6 m/s here, conveniently at the ambiguity edge. Nothing in this
design is accidental.)

And the fourth demand that makes this radar *this course's* radar: the spec
pinned v_unamb at ±75 m/s not for traffic — no car in a parking lot does
270 km/h — but because **blade tips do 69 m/s** (§2.3). The waveform was
designed so the drone's micro-Doppler is unaliased and observable. The spec
drives the waveform; the target drives the spec. (An aliased design would
fold the blade comb — livable if you know it is folded, but our unambiguous
design keeps the physics readable, and the homework audit checks yours the
same way.)

War story, 90 seconds, because Doppler ambiguity has a famous victim: the
wind farm. A surveillance radar's PRF puts its unambiguous velocity window
at a few tens of m/s. A modern turbine's blade disc smears from −100 to
+100 m/s tip-to-tip — a 200 m/s-wide ribbon of Doppler, folding over and
over into the radar's window, in *every* scan, at 40+ dB over the noise,
parked exactly where the turbines are but painting velocities everywhere.
Controllers see rain that never moves and aircraft that do not exist;
several countries now negotiate turbine siting against radar coverage maps.
One waveform triangle, drawn badly at national scale.

### 2.3 Micro-Doppler — the drone waves back (1:28–1:44)

Slide cue: the rotating-scatterer geometry; below it, the HERM comb with
spacing N_b·f_rot marked.

Lecture 1 left a debt: a drone and a large bird are both −20 dBsm — on the
range-Doppler map they are the same anonymous blip. Lecture 14 could detect
the blip but never name it. Today the naming.

**The fast version — sinusoidal phase makes sidebands.** A rotor blade tip
at radius L sweeps toward and away from the radar: its range oscillates
r(t) = R₀ + L·cos(2πf_rot·t). The echo's carrier phase is therefore
phase-modulated: 4πL/λ·cos(2πf_rot·t), modulation index

> **β = 4πL/λ** = 4π·0.11 m / 3.8934 mm = **355 rad.**

A sinusoidal phase modulation of index β makes a comb of sidebands at
multiples of the modulation rate (Bessel functions J_n(β), the FM-radio
theorem the comms students know), with significant lines out to n ≈ β —
i.e., a spectral band of half-width β·f_rot = 2πf_rot L·(2/λ) = **2v_tip/λ**.
The blade "waves" at the radar and the radar hears an FM signal 35.5 kHz
wide.

**The first-principles version — Chen's rotating scatterer [R24].** Drop
the hand-wave, put a point scatterer on the blade tip, write
τ(t) = 2r(t)/c into hour 1's dechirp phase, and read off the instantaneous
slow-time frequency: f(t) = 2ṙ(t)/λ = −(2·2πf_rot L/λ)·sin(2πf_rot·t) — a
sinusoid in the spectrogram swinging between ±2v_tip/λ. That sinusoid *is*
micro-Doppler; Chen's 2006 paper [R24] (course pack — read §II, the model
is four equations) builds every rotating, vibrating, tumbling target from
exactly this scatterer. The toolkit's channel simulator contains nothing
else: point scatterers whose r(t) you choose. Nothing is bolted on; the
spectrogram falls out of the same phase expansion as the beat tone.

**The comb, and its spacing.** One blade repeats its geometry every 1/f_rot:
its spectrum is a comb spaced f_rot. A rotor with N_b *identical, evenly
spaced* blades repeats every 1/(N_b·f_rot) — the flash of one blade is
indistinguishable from the flash of the next — so the comb decimates to
spacing

> **Δf_HERM = N_b · f_rot** (HERM lines — helicopter rotor modulation, the
> name is Vietnam-era radar jargon and nobody has improved it).

Our quadcopter: two-blade rotors at f_rot = 100 Hz (6000 rpm hover) →
**200 Hz spacing**, planted exactly, measured by you in module 3 to 2%.
And the time-domain reading: one blade flash every 1/(N_b f_rot) = 5 ms —
the spectrogram's vertical stripes, the comb's reciprocal.

What the comb buys, in one sentence each:
- **Spacing → N_b·f_rot**, the product: blade count times rotation rate —
  a *mechanical* fingerprint no bird carries. (Factoring the product needs
  more: the vendor's blade count, or the flash pattern; homework Q4.)
- **Band edge → 2v_tip/λ** → tip speed, 69 m/s: propeller-sized, not
  wing-sized.
- **A bird**: body Doppler plus a few-hertz wingbeat flutter — no 200 Hz
  comb, no ±35 kHz flash. Same blip; different machinery; separable in one
  spectrogram. This is drone-vs-bird classification as physics rather than
  machine learning — and it is also what the ML systems [R28][R29] eat as
  features.

Honest footnotes, said aloud: our quad has four rotors — locked to one RPM
in the model (flight controllers dither them in reality, splitting each
line into a cluster; the spacing survives). And the tips do 69 m/s while the
map's ambiguity is ±97 m/s — *this* waveform observes the comb unaliased;
lecture 14's radar could not have (its Doppler window was narrower than one
blade's sweep — the wind-farm problem in miniature).

### 2.4 The industrial instance — TI's 77 GHz single chip (1:44–1:48)

Slide cue: the TI block diagram from SPYY005 [R34], each block stamped with
its home lecture.

Close the arc with the artifact you can buy: TI's AWR-class 77 GHz sensors
[R34] put the entire lecture on one die — the ramp synthesizer (L12's PLL
with phase noise budgeted in dBc/Hz), the dechirp mixer (L12), the IF
amplifier and anti-alias filter (L8's language), a low-rate ADC digitizing
*beats* rather than RF (today's §1.2 dividend), and the 2-D FFT engine
(today's §2.1) — in a package the size of a postage stamp, three transmit
and four receive channels (lecture 16 will want those for angle), up to
4 GHz of ramp across 77–81 GHz. Every collision-avoidance radar shipping in
cars today is this diagram. You now know what every block costs and which
lecture priced it.

### 2.5 Hour recap (1:48–1:50)

The second FFT turns chirps into a range-Doppler map with physical axes —
0.4997 m by 0.3802 m/s for our numbers, ±97.3 m/s unambiguous. The design
triangle is four inequalities; T_c is squeezed from both sides, and our spec
pinned the velocity window wide enough to watch blade tips. Micro-Doppler is
carrier phase modulation by moving parts — β = 355 rad of it — and identical
evenly spaced blades decimate the comb to N_b·f_rot = 200 Hz. Hour 3 builds
all of it, then deletes one window and loses the drone.

**Break (1:50–2:00).**

---

## Hour 3 — Tools: the pipeline, live, and the window that saves the drone (2:00–2:50)

Live-coding, mirroring `lab/hour3_walkthrough.py` cell-for-cell. The course
waveform throughout: 77 GHz, B = 300 MHz, T_c = 10 µs, f_s = 51.2 MS/s
complex, N = 512 chirps. Everything seeded; every number below reproduces.

### 3.1 Setup verification (2:00–2:03)

Run cell 3.1. Expected: python 3.12.x, numpy 1.26.4, scipy 1.13.1,
matplotlib 3.10.x, scikit-rf 1.13.0. Anyone whose `setup_check.py` failed
pre-class pairs up now — do not debug installs live.

### 3.2 One chirp, one target (2:03–2:10)

Cell 3.2: the toolkit's channel — the full phase 2π(f₀τ + α_cτt − ½α_cτ²),
τ = 2r(t)/c, nothing more — one stationary target at 60 m, one FFT.
Peak in bin 120: f_b = 12.000 MHz measured against the formula's 12.008
(one 50 kHz bin of quantization); 200.14 kHz per meter printed. Say the
L12 payoff line at the printout: *a 300 MHz problem arrived at the ADC as a
12 MHz tone.*

### 3.3 The coupling, measured (2:10–2:16)

Cell 3.3: same target, now receding at 20 m/s; zero-pad the FFT ×32 and
watch the peak slide: apparent range 60.005 → 60.052 m, **+46.8 mm** against
the closed form's +51.3 mm. Then print the boxed fact from 1.3: worst case
inside the unambiguous window = **250 mm = half a bin**. The class should
feel mildly cheated that the scary coupling term maxes out at half a cell —
that feeling is the design lesson.

### 3.4 The chirp sequence — the map appears (2:16–2:24)

Cell 3.4: 512 chirps, three planted targets (30.00 m at 0 m/s; 80.60 m at
−15.30 m/s closing; 150.20 m at +30.00 m/s receding), Hann on both axes,
two FFTs, physical axes. The three peaks print at (29.98, +0.00),
(80.44, −15.21), (150.40, +30.04) — every error under half a bin. Then the
Parseval line: energy in, energy out, residual **0.0e+00** — the FFT moves
energy between bins, it never manufactures it. That residual is the
homework's third referee.

### 3.5 Resolution, demonstrated honestly (2:24–2:30)

Cell 3.5: two equal targets, separation swept: at 1.0 m both windows see
two peaks; at 0.6 m and 0.5 m the rectangular window still sees two, Hann
sees **one**; at 0.4 m everyone sees one. c/2B = 0.4997 m is real — and the
Hann window really does cost ~×1.6 of it. Leave the tension on screen:
*so why would anyone window?* Next cell.

### 3.6 Deliberate bug — forgetting the range window (2:30–2:38)

Cell 3.6, the syllabus-mandated crime: a 48 dB target with an 18 dB target
sixteen cells away (30 dB down, 8 m — the airliner and the drone in
miniature). Without the window, the strong target's sinc sidelobes hold the
floor at **+13.7 dB re thermal** sixteen cells out; the CA-CFAR threshold
rides on the training cells at **30.2 dB**, and the weak target's 16.1 dB
cell is *buried* — not near the line, 14 dB under it. Add one line —
`np.hanning` — and the floor collapses to **−3.4 dB**, the threshold to
13.5, and the weak target stands at 17.7: **detected**. Lecture 13 sold you
tapers as a −13 dB cosmetic; at 80 dB of scene dynamic range the taper is
the difference between a target list with the drone on it and one without.
The homework's checker prints this exact experiment on the full scene:
threshold at the drone's cell 12.7 dB windowed versus 41.6 dB not.

### 3.7 Micro-Doppler — the drone waves back (2:38–2:45)

Cell 3.7: slow-time only — hovering body plus two blade tips at 100 Hz,
80 ms of dwell at PRF 100 kHz. The STFT (short-time Fourier transform,
`scipy.signal.stft`) spectrogram saves to `hour3_microdoppler.png`: the
body's DC line, the blade sinusoids sweeping ±35.5 kHz, one flash every
5 ms. The full-dwell FFT shows the comb; `find_peaks` + the fold-down
estimator measures spacing **200.000 Hz** against the planted
N_b·f_rot = 200. Then the classifier sentence, pointed at the picture: *a
bird has the DC line and none of the comb — same blip on the map, different
spectrogram.* This figure is the entire drone-detection literature's
opening slide [R28][R30], and you just generated it from four lines of
scatterer geometry.

### Homework brief (2:45–2:49)

`lab/HOMEWORK.md` on screen. The story: a 77 GHz sensor watches an airport
parking lot — a parked airliner's tail at 180 m, a car leaving at 11.8 m/s,
a quadcopter hovering at 25 m. Module 1 designs the waveform from the spec
(the audit checks your closed forms; T_c is squeezed from both sides).
Module 2 is **the core** — dechirp cube → windowed range FFT → Doppler FFT →
CA-CFAR (imported plumbing, your hw14 module verbatim) → target list, every
planted (R, v) recovered within one bin; then the window experiment with
numbers. Module 3 stares at the drone's cell for 80 ms and measures the
HERM spacing to 2%. **Predictions come first:** Q1 (where does a hovering
drone's body land on the map, and where do its blades go?) and Q2 (does the
drone survive the missing window, and what floor does the airliner leave at
25 m?) are answered *before* running. `--check` prints facts, not
PASS/FAIL; `--map` draws the four pictures the questions discuss. Budget
≤ 3 hours. AI use assumed and welcome — the predictions and reconciliations
must be yours.

### Wrap-up (2:49–2:50)

Recap against the three claims: the mixer is the ranging engine —
200.14 kHz/m, measured; bandwidth is resolution — 0.4997 m from 300 MHz,
and the window's ×1.6 tax measured too; the second FFT read velocity and
the long stare read the machinery — 200.000 Hz of HERM comb, exactly
N_b·f_rot. Teaser: lecture 16 gives the radar its last dimension — angle —
and the course's capstone: detect, locate, track, and decide whether to
move. The drone has been seen and named; next week we take its bearing.

---

## References

- [R34] Iovescu & Rao, "The Fundamentals of Millimeter Wave Radar Sensors,"
  TI white paper SPYY005 — free: https://www.ti.com/lit/spyy005 (the
  industrial instance; read before or after, it is 8 pages)
- [R24] Chen, Li, Ho, Wechsler, "Micro-Doppler Effect in Radar: Phenomenon,
  Model, and Simulation Study," *IEEE Trans. AES* 42(1), 2006 — course
  pack; §II is the rotating-scatterer model used verbatim in the toolkit
- [R16] Chen, *The Micro-Doppler Effect in Radar*, 2nd ed., Artech 2019
  (reference — the book of [R24])
- [R30] Cai et al., "Simulation of Radar Micro-Doppler Patterns for
  Multi-Propeller Drones," RADAR 2019 — free author copy:
  https://okrasnov.github.io/pdf/YCai-etal-2019-RADAR.pdf
- [R33] MIT OCW RES.LL-003, *Build a Small Radar System* (the coffee-can
  FMCW radar — our pipeline on $200 of hardware) — free:
  https://ocw.mit.edu/courses/res-ll-003-build-a-small-radar-system-capable-of-sensing-range-doppler-and-synthetic-aperture-radar-imaging-january-iap-2011/
- [R28] Coluccia, Parisi, Fascista, "Detection and Classification of
  Multirotor Drones in Radar Sensor Networks: A Review," *Sensors* 20(15),
  2020 — free: https://www.mdpi.com/1424-8220/20/15/4172
- [R29] "A Survey on Detection, Classification, and Tracking of UAVs using
  Radar and Communications Systems," arXiv:2402.05909 — free:
  https://arxiv.org/pdf/2402.05909
