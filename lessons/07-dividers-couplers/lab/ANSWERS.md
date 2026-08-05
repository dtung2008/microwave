# Homework 7 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 2 — PREDICT FIRST) — imbalance and the tree

Every real Wilkinson splits slightly unevenly — say each one's two arms can differ
by up to 0.1 dB. **Before running:** in a corporate tree feeding N antennas, the
worst-case amplitude imbalance between two outputs grows how — with the *number of
Wilkinsons* (N−1), with the *tree depth* (log₂N), or with something else? Give the
number for this week's 4-output tree, and for a 64-element radar aperture.

Prediction:

Now run `--check`, quote the depth-instrument rows, and reconcile. (Why do the
errors combine the way they do? Hint: what operation is a dB?)

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — where the null lives

The monopulse experiment feeds the branch-line's ports 2 and 3 with equal-amplitude
signals, relative phase ψ — the angle-of-arrival proxy. **Before running:** at
boresight (ψ = 0), what does the Δ port read — a null, all the power, or something
else? At what ψ does the Δ null actually sit? (Careful: this is a *90°* hybrid.
Hour 2's rat-race slide is the contrast.)

Prediction:

Now run `--check` and `--plot`, quote the boresight numbers and the measured null
position/depth, and reconcile. What would change if the comparator were a rat-race?

Measured / reconciliation:

## Q3 (modules 1+2) — the impossibility theorem, as three numbers

The checker prints unitarity residuals: the ideal Wilkinson 3-port carries
‖SᴴS − I‖ = 1.0 at f₀, the corporate feed √3 ≈ 1.732, while lecture 4 would report
the branch-line hybrid at ~1e-15. Explain all three: why *must* the Wilkinson's be
nonzero (state the theorem), why is the 4-port allowed to be zero, and where —
physically — does the feed's "missing" power go when you drive it from an output
port? (Nothing is lost driving port 1 balanced and matched. Reconcile that too.)

Answer:

## Q4 (module 3 + hour 3) — coupling, directivity, isolation

From hour 3's C/D/I table (or your own sweep of `branchline_network`): quote C, D,
and I at 9.5 GHz and at 8 GHz, and verify I = C + D at both. A colleague says "the
datasheet quotes 20 dB isolation, so the coupler can measure a 20 dB return loss."
Using the numbers, explain what directivity actually limits, and why "isolation =
directivity" is wrong for any coupler whose coupling isn't 0 dB.

Answer:

## Q5 (module 1 + hour 3) — the resistor that doubled

Hour 3's deliberate bug doubled the isolation resistor to 200 Ω: input match
stayed *exactly* perfect, yet output match and isolation collapsed to −15.56 dB.
Your own `wilkinson_s0` agreed with the sick circuit to 1e-16. Explain both facts
with the even/odd decomposition: which S-entries are pure even mode, which carry
the odd mode, and why 20·log₁₀(1/6) — walk the Γ_odd = 1/3 through the
superposition. Then the uncomfortable part: what does the referee's 1e-16
agreement certify, and what does it *not* certify? End with the measurement habit
that catches this part before it ships.

Answer:
