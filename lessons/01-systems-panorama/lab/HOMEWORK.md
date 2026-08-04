# Homework 1 — Can this radar see the drone?

**Follows:** Lecture 1 (Microwave systems panorama: dB, link budgets, the radar equation)
**Submit:** `hw1_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

A compact X-band perimeter radar guards an airfield: 10 kW transmit, a 33 dBi dish,
1 MHz of receiver bandwidth, 3 dB noise figure, 6 dB of assorted system losses. Three
very different aircraft will cross its sky this week: an airliner (radar cross section
σ ≈ 40 m²), a fighter (σ ≈ 1 m²), and a small quadcopter drone (σ ≈ 0.01 m²).

Your job: build the machinery that answers *how far away can the radar see each one* —
and understand the answer well enough to explain why the drone is not 4000× harder
than the airliner, only 8× .

Everything in this homework is lecture 1: decibels done right (module 1 — the same
machinery runs a WiFi link budget first, on home turf), the monostatic radar equation
forward and inverted (module 2 — the core), and the three-customer study (module 3).
The radar you model here is **the course radar** — lectures 10, 13, 14, 15, and 16
keep upgrading this same instrument.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `db`, `undb`, `fspl_db`, `link_budget` | the dB machinery, one-way | ~45 min | 25% |
| 2 | `radar_snr_db`, `radar_max_range_m` | **the core** — the radar equation, both directions | ~50 min | 35% |
| 3 | `target_study` | the three-customer verdict | ~25 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs, so a
broken module 1 never hides module 2. `radar_max_range_m` must be the **closed-form
inverse** — invert the radar equation on paper first; a numeric root-search misses the
point (and the σ^¼ insight that Q2 needs).

One hint, because this edge bites everyone once: the radar equation has **R⁴** where
Friis has R². Both of your implementations work in dB throughout; the checker's referee
walks the same physics in watts and square meters with no dB anywhere. If you ever mix
units — watts into a dB slot, dBW into a dBm slot — the two will disagree loudly. That
is the referee principle: two independent implementations, one answer.

## Running it — the two commands

```
python hw1_starter.py --check    # measured facts per module (the instrument)
python hw1_starter.py --plot    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues.

## The toolkit (provided — think in these nouns)

- `WIFI_LINK`, `COURSE_RADAR`, `TARGETS` — the systems under study (plain dicts).
- `wavelength_m(f_hz)` — λ = c/f.
- `noise_floor_w(b_hz, nf_db)` — kT₀B·F in watts (your dB version lives inside
  `link_budget`; this one serves the referee).
- `ratio(x_db)` — the toolkit's own dB→linear (so the referee never depends on your
  `undb`).
- The **instrument**: `_friis_watts_referee`, `_radar_watts_referee` — the linear-watts
  physics chains your dB engines are measured against. Read them *after* you finish;
  they are also the cleanest statement of the physics in the file.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("dB in, dB out; R⁴ not R²;
losses subtract"), the AI types; you verify against the referee and the closed forms.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- `fspl(1 GHz, 1 km)` = **92.45 dB** (a number worth memorizing).
- WiFi link at 50 m: P_r = **−46.03 dBm**, SNR = **47.93 dB**; at 1 km: **21.91 dB**.
- Course radar, σ = 1 m² at 15 km: SNR = **10.49 dB** (just below the 13 dB bar —
  the fighter's R_max is close by).
- Detection ranges: airliner **32.65 km**, fighter **12.98 km**, drone **4.11 km**.
- Doubling radar range costs **12.04 dB** of SNR; σ×2 buys range ×**1.1892** (= 2^¼).

## References

- Steer, *Microwave and RF Design* Vol. 1 chs. 1–2 (free) — [R2]
- Friis 1946, "A Note on a Simple Transmission Formula" (2 pages) — [R21]
- MIT Lincoln Laboratory, *Introduction to Radar Systems*, lecture 2 (free) — [R31]
