# Homework 8 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 1+2 — PREDICT FIRST) — the price of flatness

**Before running:** for this spec (≤ 0.5 dB across 55–65 MHz, ≥ 40 dB at
±25 MHz), how many sections does the 0.5-dB Chebyshev need, and how many MORE
does the Butterworth need to do the same job? Commit to both integers, and say
in one sentence what mechanism lets ripple buy rolloff. (Hour 2 worked the
closed forms; you may compute, but write the numbers down before `--check`
confirms them.)

Prediction (N_cheb, N_butter, and the mechanism):

Now run `--check`, quote the two exact (non-integer) order values it implies
and the two integers, and reconcile.

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — the edge that decides

The spec's two rejection points sit arithmetically symmetric about 60 MHz
(±25 MHz). Your filter does not share that symmetry. **Before sweeping:**
which stop frequency — 35 or 85 MHz — gets the *smaller* rejection margin,
and why? Roughly how many dB apart do you expect the two rejections to be?
(Hint: map both through Ω(f) = (f/f₀ − f₀/f)/Δ and remember the skirts are
monotone in |Ω|.)

Prediction:

Now run `--check` and `--sweep`, quote both measured rejections and margins,
and reconcile.

Measured / reconciliation:

## Q3 (module 1) — the load that isn't one

Your engine returns g = [1.4029, 0.7071, **1.9841**] for the 0.5-dB
Chebyshev at N=2. What is that last number physically, why does an even-order
equal-ripple filter demand it, and what would actually go wrong if you built
the N=2 ladder between 50 Ω and 50 Ω anyway? (Think about what the response
must do at ω = 0 — DC goes straight through a lowpass ladder.) Why does this
make odd N the polite choice for 50 Ω systems?

Answer:

## Q4 (module 3) — what the steep skirts cost

Quote your measured group delay at the center and at the worst passband edge.
The course radar's echoes ride through this filter on their way to detection.
Using c·Δτ/2, how many meters of range smear does your measured in-band delay
variation correspond to, and why would a *steeper* filter (more sections, or
more ripple) make it worse? One sentence on why the "best" filter for a
datasheet is not automatically the best filter for a radar.

Answer:

## Q5 — the 0.35% lie

Hour 3's deliberate bug built the ladder around f₀ = 60 MHz instead of
√(55·65) = 59.79 MHz — a 0.35% slip — and the filter still *passed both
rejection points*. Explain where the error actually lands and why it shows up
at the 55 MHz passband edge specifically (what happened to the ripple band?).
Then the uncomfortable part: the buggy curve looks perfect on a screen — state
the verification habit that catches this class of bug, and what the checker
measures per-branch to enforce it.

Answer:
