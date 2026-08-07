# Homework 13 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 2 — PREDICT FIRST) — the price of quiet

**Before running:** the −30 dB Chebyshev taper drops the sidelobes 17 dB below
uniform. The −3 dB beamwidth broadens by what factor? And which way does directivity
move — by roughly how much? (Hour 2's window argument: where does the energy that
left the sidelobes have to go? A number between ×1 and ×2 is expected; commit to
one.)

Prediction (broadening factor, directivity change):

Now run `--check`, quote the measured broadening and directivity cost, and
reconcile. If your prediction missed, say which mental model was wrong — not just
"it was 1.26".

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — what steering costs

**Before running:** steering to 45° at d = λ/2 broadens the beam by what factor
(hour 2 named the mechanism — say it), and at d = 0.65λ the grating lobe lands at
what angle (the formula is on the hour-2 slides; compute it)?

Prediction (broadening factor + mechanism, grating angle):

Now run `--check` and `--plot`, quote the measured broadening and grating angle, and
note the measured grating-lobe *level*. What does that level mean operationally for
a radar that steers this array to 45°?

Measured / reconciliation:

## Q3 (module 2) — which taper sees the drone

From the `--check` scene lines and the `--plot` overlay: quote both margins (drone
bump over airliner-only floor, uniform and Chebyshev). Explain the mechanism in two
sentences: the drone's echo is −17.8 dB, the uniform SLL is −13.1 dB, the Chebyshev
SLL is −30 dB — which of these three numbers is the *floor* in each case, and why
does the beam pointing *at the drone* still care about sidelobes? Then the flip
side: name one thing the Chebyshev array now does *worse* while it reveals the
drone, with a number from your module-2 output.

Answer:

## Q4 (module 1) — the two "−13 dB"s

Your measured uniform SLL is −13.15 dB. Every textbook says −13.26 dB. The checker's
referee agrees with *you* to eight decimals. Reconcile the three statements: what
exactly is the −13.26 number, why does N = 16 sit 0.11 dB above it, and which number
should you quote in a design review for *this* array? (The instrument prints the
finite-N correction — read it.) One sentence on the general habit this teaches about
quoting textbook constants.

Answer:

## Q5 (module 1 + lecture 1) — sizing the real aperture

Hour 2 sized apertures with beamwidth ≈ λ/D. From *your measured* broadside HPBW:
out to what range can this 16-element array separate two drones flying 100 m apart?
What aperture would separate them at 5 km, and — using D ≈ π·N·M for a λ/2 planar
sheet — roughly how many elements is that? Compare against the course radar's 33 dBi
dish from lecture 1: does the dish separate them at 5 km? (Convert 33 dBi to a
beamwidth via D ≈ 4π/Ω_A ≈ 4π/θ² and check.)

Answer:
