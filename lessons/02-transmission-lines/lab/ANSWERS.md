# Homework 2 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 1+3 — PREDICT FIRST) — where the line tells the truth in real numbers

A λ/4 transformer only matches *real* impedances, so module 3 must first walk to a
plane where Z_in is purely real. **Before running:** at which ℓ/λ from the antenna
does the first purely-real plane sit, how many purely-real planes are there per
wavelength, and what are the two resistance values they alternate between? (Hour 2
gave both values in terms of Z₀ and SWR; the crank diagram says where and how
often. Our antenna's Γ has angle −110°.)

Prediction (first ℓ/λ, count per λ, the two values):

Now run `--check`, quote the spacer length and the plane impedance module 3
found, and reconcile.

Measured / reconciliation:

## Q2 (modules 1+2 — PREDICT FIRST) — which way does the cable lie?

You measure return loss at the shack end of 10 m of cable (one-way loss 9.66 dB)
instead of at the antenna (RL 10.90 dB). **Before running:** does the instrument
read *better* or *worse* than the antenna's truth, by how many dB, and why that
factor — what path does the reflected wave walk that the incident wave does not?

Prediction (direction, number, mechanism):

Now run `--check` (module 2 prints THE LIE line) and `--sweep` (the three-planes
picture), quote the measured shack-end return loss, and reconcile — including why
the simple formula is ~0.1 dB off.

Measured / reconciliation:

## Q3 (module 2) — the ledger and the invariant

From `--check`: of 1 W incident at f₀, quote the three fractions (delivered,
reflected, heat). Two parts: (a) delivered sits 10.03 dB below incident — show
how that number decomposes into the two "taxes," and say why they *add in dB*.
(b) The checker also runs your ledger on the lossless cable and prints
|Γ|² + delivered − 1. What physics makes that residual zero, what kinds of bug
would it catch, and name one bug it would *not* catch.

Answer:

## Q4 (module 3) — the price of the deep null

Your fix is exact at f₀ (|Γ| ≈ 10⁻¹⁷ — by construction, not by tuning). Quote its
measured 10-dB-RL and 20-dB-RL bandwidths from `--check`. The 10-dB band is ~4×
the 20-dB band and neither is symmetric bookkeeping: explain *why* a match built
from line lengths degrades as you leave f₀ (what physical quantity drifts, and in
proportion to what?), and what the two numbers together tell a customer that
"matched at 2.4 GHz" does not.

Answer:

## Q5 — the 3λ/4 transformer that "also works"

Hour 3's deliberate bug designed the same transformer at 3λ/4 instead of λ/4:
both printed |Γ(f₀)| ≈ 10⁻¹⁷ lossless, and with the cable's own loss both still
beat 50 dB return loss at f₀ — yet the 20-dB bandwidth measured 576.8 MHz (λ/4)
versus 275.6 MHz (3λ/4). Explain, using the tangent's periodicity, why the two
designs are identical at f₀ and not identical anywhere else. Then the transfer
question: your module 3's *spacer* has the same λ/2 ambiguity — what happens to
your fix if the spacer picks the second real plane instead of the first, and
which line of `--check` would show it?

Answer:
