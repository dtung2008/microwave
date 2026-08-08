# Homework 15 — answer sheet

Name: ___________

Questions marked **PREDICT FIRST** must be answered *before* you run the relevant
command. Write the prediction, run, then reconcile — a wrong prediction explained
well is worth more than a right one unexplained.

## Q1 (modules 2+3 — PREDICT FIRST) — the hovering drone on the map

The quadcopter hovers: its body's range rate is exactly 0, while its blade tips
sweep ±69 m/s. **Before running:** where does the drone's *body* land on the
range-Doppler map (which row, which column, roughly what shape)? And where do the
*blades* go — do they appear at the tip velocity's row, smear across many rows, or
not appear at all in a 5.12 ms CPI? Commit to a sketch, and to one sentence on why
the 80 ms micro-Doppler dwell sees comb lines where the 5.12 ms map sees almost
nothing. (Numbers that help: blade energy spreads over ~355 comb lines; one CPI is
half a rotation.)

Prediction:

Now run `--check` and `--map`, describe what actually sits at the drone's range
column (map panel 1, and the strongest cells the checker reports), and reconcile.

Measured / reconciliation:

## Q2 (module 2 — PREDICT FIRST) — the missing window

The airliner tail is 80 dB re thermal, 155 m (310 range bins) from the drone; the
drone is 22 dB. **Before running:** with the range window removed, predict the
leakage floor (in dB re thermal) the airliner's rectangular-window sidelobes leave
at the drone's range cell — use the ~1/(πΔn) sidelobe amplitude rule of thumb from
lecture 13, or reason from hour 3's measured point (−34 dB at 16 cells) — and then
predict whether the drone survives CFAR. Commit to both numbers before running.

Prediction:

Now run `--check`, quote the two leakage floors, the two CFAR thresholds at the
drone's cell, and the two verdicts; reconcile against your prediction. Then the
sharper question: the no-window map's *airliner and car* are still detected —
explain why leakage that murders the drone leaves the car untouched.

Measured / reconciliation:

## Q3 (module 1) — the triangle has no slack

Your waveform met the spec. Now the customer moves it: a delivery van on the access
road does 30 m/s and must stay unambiguous — fine, it already is — but they also
want the range coverage doubled to 400 m *at the same ADC rate*. Work the triangle:
which knob must move, what does it do to v_unamb, and does the blade comb stay
unaliased? Give the new T_c window ([min, max] µs) and say whether it is empty. If
it is: name the two ways out (one spends ADC, one spends bandwidth) and what each
costs. Closed forms only — no code edits needed.

Answer:

## Q4 (module 3) — the product, and the bird

Your measured HERM spacing is n_blades·f_rot — a *product*. (a) The vendor
datasheet says two blades per rotor: quote your implied f_rot in rpm, and check it
against the spectrogram's blade-flash interval (`--map`, panel 3: flashes every
1/(n_b·f_rot)). (b) A rival analyst claims the same 200 Hz comb could be a
four-blade rotor at 3000 rpm — using only your plots, what *second* measurement
(not the spacing) discriminates the two hypotheses, and why does it work?
(c) A gull with the same RCS hovers in a headwind in the same cell: state two
concrete features of your panels 3–4 that the gull cannot reproduce.

Answer:

## Q5 (modules 1+2) — the coupling you were promised

Hour 1 claimed the R–v coupling is self-limiting: within the unambiguous velocity
window it never exceeds half a range bin. (a) From your own numbers: the car
recedes at 11.8 m/s — how many millimeters does its beat-frequency range read
high, and what fraction of a bin is that? (b) Derive the half-bin claim in two
lines (coupling in bins = f_d·T_c; v_unamb = λ/4T_c). (c) The checker still
demanded recovery within *one* bin, and your worst range error was ~0.35 bins —
itemize where that error actually comes from (there are at least two contributors
besides coupling), and say which one a finer-than-bin (interpolated) estimator
would remove and which it would not.

Answer:
