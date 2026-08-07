# Homework 14 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 2 — PREDICT FIRST) — what the hand-wave hid

Lecture 1 declared the drone detectable to 4.11 km using a bare "SNR ≥ 13 dB" bar.
The honest contract is (P_d = 0.9, P_fa = 10⁻⁶). **Before running:** does the honest
detection range come out *larger* or *smaller* than 4.11 km — and is the change
closer to 1%, 10%, or 50%? Two things to weigh before you commit: where the honest
SNR requirement lands relative to 13 dB (Albersheim is in HOMEWORK.md if you want to
hand-crank it — but commit to a ballpark first), and how many percent of *range* one
dB of required SNR costs under the fourth root.

Prediction:

Now run `--check` and `--plot`, quote the honest bar, the three honest ranges, and
the actual P_d delivered at exactly 13 dB, and reconcile. Then the uncomfortable
half of the question: the second picture shows P_d vs range as a cliff, not a step —
from your plot, roughly how much range separates P_d = 0.9 from P_d = 0.5 for the
drone, and why is the cliff so steep? (Think in dB per km at 4 km, via R⁴.)

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — doubling the training window

The baseline CFAR uses n_train = 8 cells per side (N = 16). Suppose you double it to
16 per side. **Before running:** which direction does the CFAR loss move, and which
direction does the clutter-edge false-alarm count move? Give the mechanism for each
in one sentence — what does a bigger window buy, and what does it average *across*?

Prediction:

Now run `--check`, quote the two CFAR losses and the two "false alarms per edge
crossed" numbers from the edge ensemble, and reconcile. If your radar lived on a
coastline (one long clutter edge, always in view), which n_train would you ship,
and what did that choice cost you in the clean scene?

Measured / reconciliation:

## Q3 (module 1) — measuring one-in-a-million

Your `monte_carlo_pfa` at design 10⁻⁶ counted 0–4 crossings in 10⁶ trials, and the
checker still called that "inside 3σ". Explain why a million trials cannot *measure*
a probability of one-in-a-million (how many trials would you want, and what rule of
thumb does the checker suggest?). Then explain what the 10⁻³ and 10⁻² rows are doing
in the checker: what do they establish about your threshold formula that the 10⁻⁶
row cannot, and why is that enough? (Hour 3's deliberate bug is relevant: at which
of the three design points would it have been caught instantly?)

Answer:

## Q4 (module 3) — the drone that vanished

In the two-drones scene, the 15 dB drone at cell 1006 is detected when it flies
alone and lost when the 22 dB drone sits six cells away. Walk the mechanism: whose
power ended up in whose training cells, and by roughly what factor did the victim's
threshold rise? (You can read it off the `--plot` panel.) Then propose one change to
the detector — not just a parameter tweak — that would recover the weak drone, and
name what new failure your fix introduces. (The literature's answers have names like
smallest-of, censored, and order-statistic CFAR; you may reinvent or look up, but
say the trade-off in your own words.)

Answer:

## Q5 — the coastal radar (the war story, quantified)

A coastal radar's threshold was set in the lab against thermal noise, P_fa = 10⁻⁶.
On the coast, sea clutter raised the noise floor by 20 dB. Compute the P_fa the
operators actually saw — exactly, from the Rayleigh closed form (hint: the exponent
divides by 100; the answer is not a small number). At one decision per microsecond
(B = 1 MHz), how many false alarms per second is that? Then: which of this week's
tools fixes it, what does that fix cost (in dB, from your own checker output), and
name one thing on that coastline the fix still cannot handle.

Answer:
