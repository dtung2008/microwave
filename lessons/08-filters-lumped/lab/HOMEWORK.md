# Homework 8 — Clean the band

**Follows:** Lecture 8 (Filters I: the insertion-loss method)
**Submit:** `hw8_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Lecture 1's course radar mixes its 10 GHz echoes down to an IF (intermediate
frequency) of **60 MHz**, and the IF strip has neighbors. The frequency plan
(lecture 12 will teach you to draft one) parks two known aggressors exactly
±25 MHz away: the second mixer's image band at 35 MHz and a co-site VHF comms
transmitter at 85 MHz. Before the echo reaches the 1 MHz detection bandwidth
you priced in homework 1, a bandpass filter must clean the band:

> **passband 55–65 MHz, ≤ 0.5 dB ripple · ≥ 40 dB rejection at 35 and 85 MHz
> · 50 Ω in and out.**

Your job: build the insertion-loss synthesis machine — g-values by recursion,
order from the rejection spec, scale, transform, sweep — and hand in a spec
table with **measured margins**, not vibes. The same machine, pointed at
copper instead of coils, is lecture 9.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `g_values` | **the core** — both families, any N, by recursion | ~50 min | 35% |
| 2 | `min_order`, `bandpass_ladder` | the synthesizer: spec → henries and farads | ~50 min | 30% |
| 3 | `ladder_sweep`, `spec_report` | the sweep: ABCD → S21/S11 → the spec table | ~35 min | 20% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: module 1 is refereed against scipy on its
own; module 3 gets a known-good reference ladder (`REF_LADDER`, a 10.7 MHz FM
IF filter) so it works even while module 2 is broken. `g_values` must be the
**recursion, not a table lookup** — the checker asks for orders no table in
the book prints, and lecture 9 imports this same engine.

Two edges that bite, surfaced now:

- **The bandpass center is the geometric mean**, f₀ = √(f₁f₂) = 59.7913 MHz —
  not (f₁+f₂)/2 = 60 MHz. Hour 3 built the wrong one: it still *looks*
  perfect on screen and still passes both rejection points; it fails only at
  the 55 MHz spec edge (0.97 dB where 0.5 is allowed). The checker measures
  every branch's resonant frequency for exactly this reason.
- **The two stop frequencies are not equally hard.** The spec is arithmetic
  (±25 MHz); the transformed filter is geometrically symmetric. One of the
  edges decides your order — Q2 asks you to predict which before you sweep.

## Running it — the two commands

```
python hw8_starter.py --check    # measured facts per module (the instrument)
python hw8_starter.py --sweep    # S21/S11 + group delay against the spec mask
```

Run from the `lab/` directory. Unimplemented modules print "not implemented"
and the run continues.

## The toolkit (provided — think in these nouns)

- `SPEC` — the filter spec (plain dict); `F_SWEEP_HZ` — the measurement grid.
- `db`, `undb` — homework 1's machinery, provided this time.
- `abcd_series_z`, `abcd_shunt_y`, `abcd_cascade`, `abcd_to_s` — the cascade
  algebra from lecture 4, vectorized over frequency.
- `group_delay_s` — τ_g = −dφ/dω from a swept S21.
- `cheb_atten_db` — the closed-form Chebyshev attenuation (your stopband
  numbers must land on it).
- `REF_LADDER` — module 3's known-good input.
- The **instruments**: `_scipy_g_referee` — g-values by element extraction
  from `scipy.signal.cheb1ap`/`buttap` (a code path that never touches your
  recursion; read it *after* module 1 — it is the recursion's derivation,
  executed by machine); `_skrf_ladder_referee` — your ladder swept by
  scikit-rf's own lumped-element media.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the
part that must be yours: commit to the numbers **before** you run, then explain
any gap. A useful division of labor: you state the contract ("β and γ from the
ripple; every branch resonates at √(f₁f₂); the load g is not 1 for even N"),
the AI types; you verify against the scipy referee, the analytic rejection
formula, and the skrf sweep.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Chebyshev 0.5 dB N=3: g = **1.5963, 1.0967, 1.5963, 1.0000**; the N=2 load
  is **1.9841** (even N wants unequal terminations — that is not a bug).
- Recursion vs scipy extraction, N = 1..8, worst |Δg|: **7.5e-12** (Butterworth;
  Chebyshev lands near 3e-14 — criterion is 1e-8).
- Mapped stop frequencies: Ω(35 MHz) = **−6.714**, Ω(85 MHz) = **+4.294**.
- Minimum orders: Chebyshev 0.5 dB = **3** (exact 2.972), Butterworth = **4**
  (exact 3.882) — Q1's answer measured.
- The ladder: series **1270.3 nH / 5.578 pF**, shunt **20.30 nH / 349.09 pF**,
  every branch resonant at **59.7913 MHz**.
- Spec table: worst passband attenuation **0.5000 dB** (margin +0.00 — the
  equal-ripple design spends the whole budget); rejection **52.38 dB** at
  35 MHz (+12.38), **40.52 dB** at 85 MHz (+0.52); group delay **68.3 ns** at
  center, **128.5 ns** worst edge.
- Sweep vs skrf referee: max |ΔS21| ≈ **4e-14**.

## References

- Steer, *Microwave and RF Design* Vol. 4 ch. 2 (free) — [R2]
- Pozar, *Microwave Engineering* 4e ch. 8 — [R1]
- Cohn 1957, "Direct-Coupled-Resonator Filters" — [R23]
