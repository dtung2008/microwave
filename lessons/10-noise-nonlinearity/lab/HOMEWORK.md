# Homework 10 — The receiver budget

**Follows:** Lecture 10 (Noise & nonlinearity)
**Submit:** `hw10_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Lecture 1's course radar promised a receiver with NF = 3 dB and never said how.
This week the parts arrive in a box: a run of **cable** (−2 dB), an **LNA**
(low-noise amplifier: 20 dB gain, 1.5 dB NF, −5 dBm IIP3), a **bandpass filter**
(−1.5 dB), a **mixer** (−7 dB conversion, 8 dB NF, +15 dBm IIP3), and an **IF
amplifier** (30 dB, 4 dB NF, +10 dBm IIP3). The box does not say what order to
connect them in — and the order is the entire game. Every ordering has the same
39.5 dB of gain; their noise figures span almost 13 dB, which the radar equation's
fourth root converts into a **factor of 2.1 in drone detection range**. Same parts,
same power, same dish.

Your job: build the cascade engine (Friis's noise formula and the IP3 cascade,
hand-rolled), run the shootout across every sensible ordering, and cash the verdict
out through lecture 1's radar engine — how much farther does the radar see with the
best chain than the worst, and can *any* chain give the customer the drone at 4.3 km?

| element | gain (dB) | NF (dB) | IIP3 (dBm) |
|---|---|---|---|
| cable | −2.0 | 2.0 | ∞ (passive) |
| LNA | +20.0 | 1.5 | −5.0 |
| BPF | −1.5 | 1.5 | ∞ (passive) |
| mixer | −7.0 | 8.0 | +15.0 |
| IF amp | +30.0 | 4.0 | +10.0 |

"Sensible" orderings respect the frequency plan: the BPF is an RF filter, so it
must precede the mixer; the IF amplifier only works after the mixer. Cable and LNA
may go anywhere — that freedom is what you are pricing. The toolkit's
`sensible_orderings()` enumerates all 20.

The **toolkit carries lecture 1's radar engine** (`radar_max_range_m`,
`COURSE_RADAR` — same names, same contract as hw1), so module 3 works even if your
hw1 was never finished.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `cascade_gain_db`, `cascade_nf_db`, `cascade_iip3_dbm` | **the core** — both cascade formulas, hand-rolled | ~50 min | 35% |
| 2 | `mds_dbm`, `sfdr_db`, `shootout` | the 20-ordering shootout, both verdicts | ~35 min | 25% |
| 3 | `range_payoff`, `nf_required_db` | the lecture-1 payoff + the customer's spec | ~30 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds modules 2 and 3 known-good
reference values (instructor NF/IIP3 numbers), so a broken module 1 never hides
them. `nf_required_db` must be the **closed-form inverse** — solve lecture 1's
R_max expression for F on paper first; a numeric search misses the point.

Two hints, because these edges bite everyone once:

- **Friis does not speak dB.** Both cascade formulas run on *linear* noise factors,
  gains, and (milli)watts; convert at the door, in both directions. Hour 3's
  deliberate bug fed decibels straight into Friis and got a *plausible* wrong
  answer — the checker's lossy-first invariant (a 2 dB pad in front must add
  exactly 2.0000 dB of NF) is the tripwire that catches it.
- **Passive elements carry `iip3_dbm = inf`.** Design your IP3 cascade so that
  1/∞ = 0 falls out naturally instead of special-casing — NumPy already knows.

## Running it — the two commands

```
python hw10_starter.py --check    # measured facts per module (the instrument)
python hw10_starter.py --plot    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and
the run continues.

## The toolkit (provided — think in these nouns)

- `RX_ELEMENTS`, `COURSE_RADAR`, `TARGETS` — the parts box and the radar (dicts).
- `chain("lna", "cable", ...)` — names → the element list your engine consumes.
- `sensible_orderings()` — the 20 legal orderings (frequency-plan rule inside).
- `radar_max_range_m(radar, sigma_m2)` — **lecture 1's engine**, verbatim contract.
- `two_tone_iip3_dbm(iip3_dbm)` — the behavioral referee: builds a real
  x + a₃x³ nonlinearity at your claimed intercept, drives two tones, FFTs, and
  extrapolates the intercept back out of the measured spurs. If your cascade IIP3
  is a genuine physical number, this hands it back (and prints the 3:1 slope).
- `HAND_WORKED` — instructor's hand-worked chains (the 0.01 dB check material).

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("linear inside, dB at the door;
1/∞ = 0; NF and IIP3 both input-referred"), the AI types; you verify against the
hand-worked chains, the lossy-first invariant, and the two-tone spurs.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Warm-up chain cable→LNA: NF = **3.5000 dB** *exactly* (loss + LNA NF — the
  lossy-first-element rule), IIP3 = **−3.0000 dBm** exactly.
- Mast chain (LNA→cable→BPF→mixer→IF amp): NF = **2.3387 dB**,
  IIP3 = **−7.3767 dBm**, SFDR = **69.51 dB** in the radar's 1 MHz.
- All 20 orderings share G = **39.5 dB** (gain commutes; nothing else does).
- Best sensitivity: LNA→BPF→mixer→IF amp→cable, MDS = **−111.94 dBm**
  (NF 2.0378). Worst: cable→BPF→mixer→IF amp→LNA, NF = **14.9267 dB**.
- Best SFDR is a *different* chain than best MDS: **69.5065 dB** vs 69.0691.
- The "obvious" chain (cable→BPF→LNA→…) ranks **9th of 20** by sensitivity.
- Drone detection range: best chain **4.339 km**, worst **2.066 km** —
  ×**2.1000**, exactly 10^(ΔNF/40). (Lecture 1's assumed NF 3.0 gave 4.106 km.)
- The customer's 4.3 km spec needs NF ≤ **2.1966 dB** — exactly **1 of 20**
  chains clears it.
- Two-tone referee: spur slope **3.0000**, extrapolated IIP3 within 0.01 dB of
  your cascade number.

## References

- Friis 1944, "Noise Figures of Radio Receivers" (4 pages, assigned whole) — [R20]
- Steer, *Microwave and RF Design* Vol. 1 ch. 4 + Vol. 5 ch. 4 (free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 10 — [R1]
