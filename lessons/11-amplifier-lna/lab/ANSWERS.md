# Homework 11 — answer sheet

Name: ___________

Device used (from `--check`'s first line): vendor / synthetic fallback: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 1 — PREDICT FIRST) — where will it be conditionally stable?

Your LNA's design frequency is 2.4 GHz, and the lecture claimed this device is
unconditionally stable there. The file spans far more than 2.4 GHz.
**Before running the audit:** at which end of the file do you expect μ < 1,
and why? Argue from the physics of the instability mechanism — what happens to
|S21| as f falls, what happens to the S₁₂ feedback path, and what the product
|S₁₂S₂₁| (the loop) does as a result.

Prediction (band(s) and mechanism):

Now run `--check`, quote the measured μ < 1 band(s) and worst-μ values, and
reconcile. If the audit found a band your prediction missed, say what the
mechanism there must be instead (hint: look at what |S22| does in that band —
`--plot`'s left panel and the raw file both show it).

Measured / reconciliation:

## Q2 (modules 2+3 — PREDICT FIRST) — what the noise match costs

Your gain match Γ_MS is not the noise match Γ_opt. **Before running module 3:**
moving the source from Γ_MS to Γ_opt (output re-matched each time) costs how
many dB of G_T? Commit to a number. Reason from geometry: `--plot`'s middle
panel shows both points — the available-gain circles around Γ_MS are spaced
roughly evenly in dB, and the MAG−2 dB circle passes between the two points.

Prediction (dB):

Now run `--check`, quote the measured cost line, and reconcile. Then the flip
side: quote NF at Γ_MS versus NF_min — what did *gain* cost in noise?

Measured / reconciliation:

## Q3 (module 1) — two referees that must agree

The harness checks your K–Δ verdict against your μ verdict at every frequency
and prints the agreement count. These are not two independent measurements of
nature — they are two theorems about the same S-matrix. So: (a) what would it
actually mean if they disagreed at some frequency? (b) Given that they must
agree, why does the course (and industry) still prefer μ — what does μ = 1.23
tell you that (K = 1.10, |Δ| = 0.55) does not? (c) Name one thing *neither*
criterion can see (think: what data went in, and lecture 11's opening claim
about when the measured-two-port worldview cracks).

Answer:

## Q4 (module 2) — the cascade referee and the datasheet referee

Your `design_for_gain` pair hits the target to machine precision at f₀ in the
cascade — then `--plot` (or the walkthrough's swept-amp figure) shows the gain
falling away from the target off-frequency. (a) Why must it fall — what did
the L-sections promise, and at how many frequencies? (b) Now the outside
referee: the PGA-103+ datasheet's typical gain is 11.0 dB at 2 GHz and 8.1 dB
at 3 GHz. Interpolate to 2.4 GHz and compare with your file's |S21|² and your
MAG. Do the numbers cohere? What, physically, is the ~0.5 dB gap between
|S21|² and MAG — why can a passive, gainless network "add" that much?
(Synthetic-device users: answer (b) for why the check is impossible for you,
and what that implies about trusting synthetic data.)

Answer:

## Q5 (module 3) — pick your point and defend it

Run `--plot` and look at the frontier. Pick a design point (Γ_S somewhere on
the walk — the gain end, the noise end, or between), and defend it in one
paragraph **with numbers**, using `system_nf_db(nf1_db, g1_db, nf2_db)` and a
second stage of NF₂ = 6 dB (lecture 10's mixer-ish number): compute the
two-stage system NF at the gain-match end and at the noise-match end of your
frontier, and state which wins, by how much, and what would have to change
about the *rest of the receiver* (NF₂, or an interstage filter's loss) for
your answer to flip. This is lecture 10 and lecture 11 shaking hands — say so
in your own words.

Answer:
