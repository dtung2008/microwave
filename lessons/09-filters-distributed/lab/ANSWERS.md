# Homework 9 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 2+3 — PREDICT FIRST) — where does the filter come back?

Your bandpass sections are quarter-wave at f₀ = 2.4 GHz. **Before running any
sweep:** at exactly which frequency does the *first reentrant passband* land,
and why there? Derive it from θ(f) and the periodicity of the coupled section's
cot/csc terms — state the period in θ, then in f. Bonus commitment: where is the
*second* reentrance, and can this week's 0.1–10 GHz sweep see it?

Prediction (a frequency in GHz, and the mechanism):

Now run `--check` and `--sweep`, quote the measured reentrant center and the
|S21| there, and reconcile.

Measured / reconciliation:

## Q2 (module 3 + case study — PREDICT FIRST) — the zero that isn't

At 2f₀ = 4.8 GHz every section is half-wave, and the ideal sweep shows a
transmission **zero** (hundreds of dB). **Before running the case-study
overlay:** will the case-study curve (microstrip "reality") honor that zero?
Commit to yes or no, and to the physical mechanism — think about what microstrip
does differently to the even and the odd mode (lecture 7 told you where each
mode's field lives).

Prediction:

Now run `--check`, quote the measured worst |S21| near 2f₀ for ideal and case
(note the PLACEHOLDER tag — these are stand-in numbers until the instructor's
openEMS export lands), and reconcile.

Measured / reconciliation:

## Q3 (module 1) — what kind of statement is Kuroda?

The checker measures max ||S21| yours − |S21| series-stub form| ≈ 7e-16 — machine
epsilon. What does that number say Kuroda's identity *is* (approximation?
narrowband equivalence? something stronger?), and over what frequency range the
claim holds? Then the practical half: state what you would physically have to
etch if the identity did not exist, why microstrip refuses, and what the two
unit elements cost you in a real layout (hint: they were not free — but they
were *useful*; what do the λ/8 connecting lines buy the layout engineer?).

Answer:

## Q4 (modules 2+3) — the missing 0.17%

You designed Δ = 10%; the checker measures a 0.5-dB ripple bandwidth of 9.83%,
and the worst attenuation over the *designed* band is 0.5659 dB — the ripple
budget leaks at the 2.28 GHz edge. hw8's lumped ladder hit its band edges
exactly; this filter does not. Where in the coupled-line design procedure did
the approximation enter (which step of g → J → Z0e/Z0o assumes "narrowband")?
Why does the same procedure land *closer* for a 5% filter and *worse* for a
20% one? And what is the honest fix if the spec edge at 2.28 GHz were
contractual?

Answer:

## Q5 (module 3 + case study) — pricing the ideal-vs-EM gap

Quote the three case-study deltas from your `--check` (center shift, IL at
2.4 GHz, the 2f₀ spur), tagged placeholder or not. The placeholder manufactured
them from exactly two documented knobs — name both, and say which measured
delta each knob is chiefly responsible for. Then: name at least two *additional*
physical effects a real openEMS solve (or the fabricated board) would add that
the placeholder cannot show. Finish with the lecture's war story: the fabricated
filter that came out 4% low — which single number in your (w, s, ℓ) table was
cut wrong, and which check in *this* homework's chain would have caught it
before the board house did?

Answer:
