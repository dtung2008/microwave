# Homework 3 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 1+2+3 — PREDICT FIRST) — which product survives the band?

Two perfect matches at 2.4 GHz: an L-section (two lumped elements) and a shunt
stub (a 0.199 λ line plus a 0.085 λ stub). **Before running:** which design
holds its match over a wider band, and why? Count the stored-energy elements
in each — every reactance and every stretch of line stores energy, and stored
energy is what makes a response steep in frequency. Commit to a ranking of all
four designs the checker sweeps (two L-section solutions, two stub solutions).

Prediction (ranking + mechanism):

Now run `--check`, quote the four worst-in-band return losses, and reconcile.

Measured / reconciliation:

## Q2 (module 2 — PREDICT FIRST) — the two stub solutions are not twins

Your `stub_match` returns two mathematically perfect solutions: d = 0.199 λ
with ℓ = 0.085 λ, and d = 0.495 λ with ℓ = 0.415 λ. **Before running:** which
one is wider-band, and by roughly what factor? (Hint: off f₀, every electrical
length βd = 2πd·f/f₀ drifts in proportion to its own size. One solution
carries 0.28 λ of copper, the other 0.91 λ.)

Prediction:

Now run `--check`, quote both true 10-dB bandwidths from the wide sweep, and
reconcile the factor.

Measured / reconciliation:

## Q3 (modules 1+2) — the rail every trajectory must touch

Your `--smith` chart shows both matches passing through a marked intermediate
point on the g = 1 circle before sliding to the center. Explain why the
*last* move of each design forces the *previous* move to end on that specific
circle. Then explain what hour 3's deliberate bug did instead, and why its
final point missed the center by |Γ| = 0.53 — worse than no matching network
at all — even though every individual step looked reasonable.

Answer:

## Q4 (all modules) — what "matched by construction" does and does not certify

The skrf cascade reports |Γ(f₀)| ≈ 10⁻¹⁶ for your designs. Name one class of
mistake this referee catches loudly (think: what did it catch in hour 3?),
and one class of real-world failure that would sail through the referee at
10⁻¹⁶ and still sink the product on the bench. What, outside this homework,
catches the second kind?

Answer:

## Q5 (module 3) — the threshold that was already met

The unmatched antenna sits at 10.90 dB return loss — *already past* the
10-dB threshold — which is why several of your band edges came back
edge-limited (`None`). Two parts: (a) So what did the matching network
actually buy? Quantify it at f₀ (the toolkit prints delivered power). (b)
What does this teach about quoting "10-dB bandwidth" for a device that
starts above the threshold — and what *should* you quote instead when two
designs are compared? (Lecture 6 sharpens this into the Bode–Fano limit:
match quality × bandwidth is a budget you spend, not a score you win.)

Answer:
