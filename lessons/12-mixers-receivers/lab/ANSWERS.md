# Homework 12 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 1+2 — PREDICT FIRST) — which side of the mirror?

**Before running:** the image sits at f_RF ± 2·IF — a low-side LO puts it *below*
the band, a high-side LO puts it *above*. Given the two hard constraints (the image
band must clear your own 10.0–10.4 GHz tuning band, so 2·IF > 400 MHz; the ADC's
input bandwidth caps IF below 500 MHz), write down where each side's image band can
possibly land — and then say which side survives the emitter table, and specifically
the airfield radar at 9.6 GHz. Commit to a verdict: high-side, low-side, or both.

Prediction:

Now run `--check` and `--plot`, quote the two measured image bands, the collision
list for `BUG_PLAN`, and the feasible-window scan for both sides, and reconcile.

Measured / reconciliation:

## Q2 (module 3 — PREDICT FIRST) — the price of hovering

The clutter line is 60 dB above the drone and carries the LO's skirt: L(f) is
−70 dBc/Hz at 100 Hz falling 20 dB/decade above that (and 30 dB/decade below).
The Doppler bin is 1.5 Hz (ENBW), the visibility bar is 13 dB over the local skirt,
and Doppler is ≈ 68 Hz per m/s at 10.2 GHz. **Before running:** every halving of
drone speed costs how many dB of margin in the 20 dB/decade region? And from the
numbers above, predict the minimum visible speed to the nearest half m/s. (Set the
line power equal to skirt-in-bin × threshold and solve for f.)

Prediction:

Now run `--check`, quote the measured SNR-vs-offset table and v_min, and reconcile
against the analytic bound the checker prints.

Measured / reconciliation:

## Q3 (module 2) — the collision you cannot filter away

Your passing plan still carries two notes: the (2,2) and (3,3) products of the
police/amateur band (10.50–10.55 GHz) reach the IF at certain tunes. Work out where
the offending signal sits when each filter sees it: why is the IF filter completely
blind to these products, and why is whatever the preselector does to them incidental
rather than guaranteed by its spec? Whose job is the dependable rejection, and what
mixer specification would you write into the plan?

Answer:

## Q4 (module 2) — why "filtering lives low," in two numbers

Your `filter_specs` prints n = 7 for the preselector at 10.2 GHz and n = 4 for the
IF filter at 321.4 MHz — yet the IF filter does the *harder* selectivity job
(10 MHz passband, 60 dB in ±25-ish MHz — compare fractional bandwidths). Explain
what makes the high-frequency filter cost more for less. Then the architectural
half: if the IF were 60 MHz, what does the image-band arithmetic say happens to the
preselector spec — what order would reject the image? (Careful: it is not a large
number.)

Answer:

## Q5 (module 1) — what each referee can and cannot catch

Module 1 is checked twice: against a closed-form m,n grid, and against FFT peaks
measured from a behavioral diode mixer. Name one class of mistake only the FFT
referee catches, one class only the closed form catches cleanly, and one class of
error that sails through *both* in agreement — yet would sink the real receiver on
the mast. What activity outside this homework catches the third kind?

Answer:
