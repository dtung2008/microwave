# Homework 10 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 1 — PREDICT FIRST) — the cable moves behind the LNA

The shack chain puts the −2 dB cable in front (cable→LNA→BPF→mixer→IF amp); the
mast chain moves the LNA to the antenna (LNA→cable→BPF→mixer→IF amp).
**Before running:** system NF improves by how many dB? The tempting answer is
"2 — the whole cable loss." Commit to a number, and say what Friis's formula does
with the cable's noise once 20 dB of gain stands in front of it.

Prediction:

Now run `--check` (module 1 prints both chains), quote the two NFs and the
measured saving, and reconcile it against your prediction — where did the missing
fraction of a dB go?

Measured / reconciliation:

## Q2 (module 1 — PREDICT FIRST) — the spur arithmetic

The two-tone referee drives two equal tones through a real x + a₃x³ nonlinearity
and raises both tones in 5 dB steps. **Before running:** each 5 dB step moves the
IM3 spurs (at 2f₁−f₂) by how many dB, and closes the tone-to-spur gap by how many?
Say where the 3 comes from in the algebra — what does cubing a sum of two cosines
do to their amplitudes?

Prediction:

Now run `--check` (the two-tone referee line) or `hour3_walkthrough.py` (the level
table), quote the measured slope and one measured gap, and reconcile.

Measured / reconciliation:

## Q3 (module 2) — two verdicts, two winners

`--check` and the left panel of `--plot` show the 20 orderings ranked twice. The
best-MDS chain and the best-SFDR chain are *not the same chain*. Explain why, in
terms of which stage limits each end of the dynamic range (the blame table in the
walkthrough helps: who dominates F, who dominates 1/IIP3?). Then choose the chain
*you* would build for the drone radar and defend the choice in three sentences.

Answer:

## Q4 (module 2) — the "obvious" chain

The chain everyone's intuition builds first — cable down from the antenna, filter
to protect the receiver, *then* the LNA — ranks 9th of 20 by sensitivity, 3.04 dB
of NF behind the mast chain. Say precisely where those 3 dB go (Friis's formula
knows), and then make the strongest honest argument *for* building it anyway: what
real-world threat does filter-before-LNA defend against, and which number in the
element table would that threat attack? (Hour 2 called this the linearity–noise
squeeze; lecture 11 picks it up.)

Answer:

## Q5 (module 3) — the bandwidth knob, revisited

The radar's B = 1 MHz. Suppose lecture 15's waveform designer demands 10 MHz for
range resolution. Without editing any code: which way and by how much do (a) MDS,
(b) drone detection range, and (c) SFDR move? All three are driven by the same
10 dB floor shift, yet the three answers carry three different exponents — name
each one. Verify with one edit to `COURSE_RADAR` if you like, then put it back.

Answer:
