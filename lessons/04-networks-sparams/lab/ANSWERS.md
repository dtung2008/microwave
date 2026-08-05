# Homework 4 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 2 — PREDICT FIRST) — can a passive network have |S₂₁| > 1?

**Before running anything:** the three files are all referenced to a real 50 Ω at
both ports. Can a *passive* network — resonant, mismatched, as reactive as you like —
show |S₂₁| > 1 at some frequency in that reference? Commit to yes or no, **and say
what physical quantity |S₂₁|² compares against what**. (Careful: a λ/4 line can
double the *voltage* across a high-impedance load. Is that a counterexample? Hour 3's
two lossless devices with |S₂₁| < 1 are the warm-up for this.)

Prediction (yes/no + the power argument):

Now run `--check` and `--plot`. Quote network C's peak |S₂₁| in dB and its passivity
residual, and state what your answer to the prediction implies about C — is there any
"reactive mismatch" escape hatch left, and would re-referencing the file to a
different real z₀ change the verdict?

Measured / reconciliation:

## Q2 (module 2 — PREDICT FIRST) — the loss the plot cannot show

Network B's |S₂₁| trace hugs 0 dB across its passband — on the `--plot` picture your
eye cannot separate it from lossless. **Before running:** predict the order of
magnitude of B's unitarity residual ‖SᴴS − I‖ in two worlds: (a) the file's claim is
true and all you see is the planted ~10⁻⁴ measurement noise; (b) there is really
~0.1 dB of hidden dissipation in the passband (hint: 1 − 10^(−0.1/10) ≈ 0.023).
Which world does the course tolerance UNIT_TOL = 5×10⁻³ separate you into?

Prediction (two orders of magnitude + which side of tolerance):

Now run `--check`, quote B's measured unitarity residual, its ratio to UNIT_TOL and
to the noise floor, and reconcile: what does this say about trusting a dB-scale plot
to certify "lossless"?

Measured / reconciliation:

## Q3 (module 1) — what the skrf referee can and cannot certify

Your conversions agree with scikit-rf to ~10⁻¹² and your cascade matches `**` to
~10⁻¹⁵ — yet network B sailed through those same conversions and is still a lie.
Name precisely what the module-1 referee certifies, what the module-2 invariants
certify instead, and one class of error that would slip past *both* (hour 3's
freespace lesson from lecture 1 is a cousin of this question).

Answer:

## Q4 (module 3) — the verdicts on A and B, defended

Quote your three residuals for A and for B against the course tolerances, and write
the two verdicts as you would to the vendor who sent the files. For B, go one step
further: from the unitarity residual (or the worst-frequency power deficit
1 − |S₁₁|² − |S₂₁|²), estimate *how much* dissipation the "lossless" file hides, in
dB, and where in frequency it is worst. (The sealed envelope in the toolkit will
tell you the Q values afterwards — read it only once this box is written.)

Answer:

## Q5 (module 3) — network C: disguised amplifier, or bad measurement?

C violates passivity — but a broken VNA calibration can also produce |S₂₁| > 1 on a
perfectly passive device. Argue from the *structure* of the residuals which
explanation fits: what do C's forward gain (magnitude and frequency shape), its
reverse isolation, and its reciprocity residual each suggest? Then name one
measurement you would order on the bench — not another S-parameter sweep — that
settles amplifier-vs-artifact in five minutes.

Answer:
