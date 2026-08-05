# Homework 6 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 2 — PREDICT FIRST) — what doubling N buys

The theory table says an N=2 transformer holds ~20 dB of worst-case in-band return
loss over this octave. **Before running:** if you double the section count to N=4,
the worst-case in-band return loss (theory) improves by how many dB? State the
mechanism — which single quantity in the ripple formula does N act on, and how fast
does that quantity grow with N for sec θ_m = 2?

Prediction:

Now run `--check`, quote the measured theory values for N=2 and N=4 *and* the exact
swept values, and reconcile both gaps (your prediction vs theory; theory vs sweep).

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — the trap in dataset C

The bench notes say `C_cavity` shows about **0.35 dB of insertion loss at
resonance**, and its 3-dB bandwidth works out to Q ≈ 470. **Before running module
3:** is this resonator's *unloaded* Q above, below, or equal to 470 — and by
roughly what factor? (The coupling formula from 2.4 turns the 0.35 dB into the
factor; remember what unit the formula wants.)

Prediction:

Now run `--check`, quote your extracted Q_L and Q_u for C_cavity and the skrf fit's
numbers, and reconcile.

Measured / reconciliation:

## Q3 (module 1) — negotiating with a theorem

Your `--check` says the client's first board (C = 10 pF) caps the octave match at
17.37 dB — the 20 dB spec is not hard, it is *impossible*. Write the three-sentence
reply to the client: the only three quantities that can move (one is the band, one
is the spec, one is the load), and for each, the number that would make the spec
physical (use your own module 1 to compute them). Which one did the client actually
choose, judging by `LOAD_MODELS`?

Answer:

## Q4 (module 2) — the theory that designed it says 20.09; the sweep says 18.98

The small-reflection theory picked N=2 as sufficient; the exact cascade of that
very design misses the spec by a full dB, and the honest minimum is N=3. Explain
where the missing dB physically went — what does the theory of small reflections
throw away, and why is it not small for Z_L/Z₀ = 4? Then the sharper question: the
gap *grows* with N (+0.11, +1.10, +2.04, +3.70 dB for N=1…4) even though each
individual step Γ_k gets *smaller*. Why? (Hint: compare what the neglected terms
depend on with what the ripple depends on.)

Answer:

## Q5 (module 3) — the 3-dB method's honest error budget

Name two *distinct* ways a 3-dB Q measurement lies even when the arithmetic is
right (this homework planted at least two: think about what the peak sits on, and
what the formula's inputs must be), and state for each whether the skrf `Qfactor`
fit is immune to it, and why. End with the one-line lab rule that would have saved
the war-story cavity measurement from section 2.4.

Answer:
