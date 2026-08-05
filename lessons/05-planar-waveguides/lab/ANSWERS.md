# Homework 5 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (module 1 — PREDICT FIRST) — the transformer changes boards

The λ/4 transformer is designed on FR-4 (ε_r = 4.4) and the project then upgrades
to RO4350B (ε_r = 3.48), same 0.508 mm thickness. **Before running:** does the
transformer's physical length get *longer* or *shorter*, and by roughly what
factor? Careful — the naive √(4.4/3.48) is not quite the right ratio. Say which
epsilon actually sets the wavelength, and why the true factor is smaller than the
naive one.

Prediction (direction + factor + mechanism):

Now run `--check`, quote the two measured lengths and the printed ratio, and
reconcile against both your factor and the naive √(ε_r ratio) = 1.124.

Measured / reconciliation:

## Q2 (module 2 — PREDICT FIRST) — the pipe that technically works

WR-62's TE₁₀ cutoff is 9.488 GHz, so 10 GHz *does* propagate in it. **Before
running:** for the 30 cm run at exactly 10 GHz, is WR-62's group delay longer or
shorter than WR-90's, and by roughly what factor? (τ = (L/c)/√(1−(f_c/f)²) — you
can predict this with one square root per guide.) Then say what the ω-β diagram
looks like at a point that close to cutoff, and what that does to a 200 MHz-wide
signal.

Prediction (factor + the ω-β picture):

Now run `--check` and `--sweep`, quote the three delays and the three window
spreads, and give the picker's verdict with its reason.

Measured / reconciliation:

## Q3 (module 1) — where the hand model bends

`--sweep`'s left panel shows your flat quasi-static ε_eff against skrf's rising
curve. Which direction does ε_eff move as frequency rises, what is the physical
mechanism (where does the field energy migrate, and why), and at what frequency
does the disagreement on this stackup cross 1 %? Then the design consequence: a
lecture-9 filter cut from your quasi-static λ_g at 10 GHz — do its resonances land
high or low, and by roughly how much on this board?

Answer:

## Q4 (module 3) — the shootout, defended

Quote your measured table: microstrip conductor + dielectric vs WR-90 over 30 cm
at 10 GHz. Then two mechanisms and one judgment call: (a) why does the waveguide
win by ~two orders of magnitude — what does it simply *not have*? (b) in your
run, conductor and dielectric loss on RO4350B are nearly tied — which one grows
faster with frequency, and what does that predict at 77 GHz? (c) if waveguide is
84× better, why is the course's front-end still built on microstrip — name the
two costs the loss table cannot see. (And somewhere in here: why is Np→dB 8.686
and not 4.343?)

Answer:

## Q5 (modules 1+2) — what the referee can and cannot catch

skrf `MLine` referees your Hammerstad within 2–3 % — but both are *models*. Name
one class of error the referee catches loudly (think: what did the deliberate bug
in hour 3 get wrong, and would the referee have flagged it?), and one class of
error that sails through the comparison because both sides share the assumption.
What, outside this homework, catches the second kind? (Hour 3's openEMS cell is a
hint; so is the etch tolerance on a 1.11 mm trace.)

Answer:
