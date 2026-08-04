# Homework 1 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 1+2 — PREDICT FIRST) — six versus twelve

**Before running:** when a one-way link doubles its range, SNR falls by how many dB?
When the radar doubles its range? Say *where the extra loss physically comes from* —
what happens on the way out, and what happens on the way back?

Prediction:

Now run `--check`, quote the two measured numbers (the WiFi budget at 50 m vs 200 m
gives you the one-way case; the radar line prints the other), and reconcile.

Measured / reconciliation:

## Q2 (module 2 — PREDICT FIRST) — what stealth buys

From airliner to drone, σ falls from 40 m² to 0.01 m² — a factor of 4000 (36 dB).
**Before running:** the maximum detection range shrinks by what factor? Why is the
answer nowhere near 4000? (Hour 2 named the mechanism; one exponent is doing all
the work.)

Prediction:

Now run `--check` and `--plot`, quote the measured airliner/drone range ratio, and
say what the +1/4 guide line on the log-log plot is asserting.

Measured / reconciliation:

## Q3 (modules 1+2) — what the referee can and cannot catch

Your engines work in dB; the checker's referee walks the same physics in watts. Name
one class of mistake this comparison catches loudly, and one class of mistake that
would sail through *both* implementations in agreement. What outside the code would
catch the second kind?

Answer:

## Q4 (module 3) — the bandwidth knob

The course radar's bandwidth is 1 MHz. Suppose the designer widens it to 10 MHz.
Without editing any code: which direction does every detection range move, and by
what factor? Verify with one edit to `COURSE_RADAR` if you like, then put it back.
(Lecture 15 will give the designer's counter-argument — wider B buys something
range-related that this week's radar equation cannot see.)

Answer:

## Q5 — the 30 dB lie

Hour 3's deliberate bug fed 40 dBW into a dBm slot — a 30 dB power error — yet the
drone's "detection range" moved only from 4.11 km to 23.09 km, a factor of 5.62.
Explain the exponent arithmetic, and then the uncomfortable part: why does this make
dB unit errors *hard to spot from results alone*? End with the habit that prevents
them.

Answer:
