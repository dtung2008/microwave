# Homework 16 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 1 — PREDICT FIRST) — two drones, 1.5 beamwidths apart

Lecture 13 taught "resolution = the beamwidth"; the two drones sit 9.52° apart
against a 6.35° beamwidth. **Before running:** does beamscan separate them? Does
MVDR? And at what per-element SNR does each answer *flip* (stop, or start, being
true) across −15…+18 dB? Commit to three things: a yes/no for each method at high
SNR, the flip SNR for each (or "never flips in this range"), and one sentence on
*what physically changes* as SNR drops that could un-resolve two sources whose
angular separation never changes.

Prediction:

Now run `--check` (the resolution_study block) and `--plot` (panels 1 and 3).
Quote both flip SNRs and the two dip depths at 18 dB SNR, for 1.5 BW *and* for the
checker's second separation, 0.7 BW. Reconcile — in particular: if you predicted
beamscan fails at 1.5 BW, say precisely which half of "resolution = beamwidth"
you over-applied.

Measured / reconciliation:

## Q2 (module 1 — PREDICT FIRST) — the jammer

Scene 3's jammer sits at +25°, 40 dB above the drone at −10°. Lecture 13 measured
the uniform 16-element array's first sidelobe at −13.26 dB. **Before running:**
predict the beamscan spectrum's approximate level at the drone's angle (reason
from the jammer's power and the sidelobe envelope), and therefore whether the
drone's 10 dB bump is visible in the beamscan spectrum at all. Then predict what
MVDR shows at −10° and *why it can* — one sentence on where a null 40 dB deep
comes from without anyone telling MVDR where the jammer is.

Prediction:

Now run `--check` and `--plot` (panel 2). Quote: beamscan's two strongest peak
angles (what IS its second peak?), the beamscan level at the drone's angle, and
the MVDR level there. Reconcile.

Measured / reconciliation:

## Q3 (module 2) — why the mask saves MVDR and not beamscan

The jammed chain masks out peaks within 3° of the jammer bearing — the same mask
for both methods. Yet the measured θ error is ~54° for the beamscan chain and
~0.035° for the MVDR chain. Explain the asymmetry mechanically: what does the
beamscan spectrum look like *outside* the mask, and what does the MVDR spectrum
look like there? (Your `--plot` panel 2 is the exhibit.) Then the design question:
the mask means the sensor is blind within ±3° of the jammer — state one concrete
operational consequence for the corridor guard, and one mitigation (there is a
hardware one in lecture 13 and a geometry one in this lecture's MIMO slide).

Answer:

## Q4 (module 3) — defend the alert rule, both directions

The contract alerts iff 0 < t_CPA ≤ 20 s and d_CPA < 30 m. Defend it against
**both** costs, using your measured table: (a) *miss side* — drone_a's CPA is
23.7 m, only 6.3 m inside the alert radius, and your tracked estimate carried
~0.03–0.94 m of error; how much measurement error would flip that verdict, and
which chain stage (R, θ, or the α-β velocity) contributes most at 40 m range?
(b) *false-alarm side* — drone_b passes at 60 m and leaving_drone's CPA is in the
past; state what each non-alert would cost if the rule fired anyway (lecture 14's
false-alarm economics: what does a cockpit or a brake pedal do with a false
alert?). (c) Finally: a colleague proposes the simpler rule "alert if R/(−v) < 20 s"
(range over closing rate — no array, no DOA needed). Using drone_b as the witness,
show which verdict it gets wrong or right *for the wrong reason*, and say what the
crossing geometry does to −v as the target approaches CPA.

Answer:

## Q5 — the whole course in one pipeline

The capstone chain is waveform → channel → front-end → snapshots → range-Doppler →
CFAR → DOA → track → decision, and every arrow is a lecture. Trace **two** failure
modes end to end, naming the owning lecture at each step: (1) the element spacing
is widened to d = 0.65λ to cheapen the array, and a target at −40° is tracked —
what appears, which lecture predicted it (quote its formula), and what does the
avoid stage do with the ghost? (2) hour 3's deliberate bug ships to production:
MVDR covariance from 8 snapshots, no loading — walk the consequences through DOA,
track, and alert for the jammed scene, and state the two-word fix and its cost.
Close with one sentence: of the sixteen lectures, which block of this pipeline
would you now trust yourself to *design*, and which would you only dare *review*?

Answer:
