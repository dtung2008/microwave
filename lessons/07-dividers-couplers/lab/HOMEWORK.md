# Homework 7 — Feed four antennas

**Follows:** Lecture 7 (Power dividers & couplers)
**Submit:** `hw7_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

A four-element X-band array (lecture 13 will aim it) needs an equal-amplitude,
equal-phase feed: one transmitter in, four antennas out, every output the same to
within hundredths of a dB — and the outputs isolated from each other, because
antennas reflect, and one element's mismatch must not leak into its neighbors'
drive. The classic answer is a **corporate tree of three Wilkinson dividers**.

Then the radar tie-in: bolt a **branch-line hybrid** onto two of the elements and
you have a two-element monopulse comparator — the circuit that tells a fire-control
radar *where in the beam* the target sits, by reading a sum port and a null. This
week you build the feed, certify it with lecture 4's invariants, and watch the null
form out of two paths arriving exactly 180° apart.

Everything is lecture 7: the even/odd analysis (module 1 — the core, and the
technique lecture 9 reuses for coupled lines), skrf `Circuit` assembly (module 2 —
hour 3 built the single Wilkinson; you build the tree), and the Σ/Δ experiment
(module 3).

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `wilkinson_s0` | **the core** — even/odd closed form at f₀, arbitrary (Z_line, R) | ~50 min | 30% |
| 2 | `corporate_feed`, `feed_facts` | the tree in skrf `Circuit`, measured | ~50 min | 30% |
| 3 | `monopulse_response`, `delta_null` | Σ, Δ, and the 180° null | ~25 min | 20% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 20% |

Modules are independently checkable: module 1 is refereed by the skrf-assembled
circuit (the toolkit's `wilkinson_network` — it never saw your algebra, only lines
and a resistor); module 2 by the closed-form ideal tree S(f₀) plus lecture 4's
invariant suite; module 3 by the hybrid's own S-matrix read at the null. A broken
module 1 never hides module 2.

`wilkinson_s0` must be the **closed form for arbitrary arm impedance and resistor**,
not the memorized ideal matrix — the checker feeds it broken designs (thin arms,
the hour-3 doubled resistor) and the formulas must carry the failure modes too.
Run the even/odd analysis on paper first; at f₀ every quarter-wave tangent has gone
to infinity, so take the limits by hand — `np.tan(np.pi/2)` is a bug, not a limit.

Hints for the edges that bite (surfaced on purpose):

- **skrf `Circuit` port order** (verified against the installed 1.13.0 wheel):
  external ports appear in the reduced network in the order their `Port` objects
  first appear in the connections list — *not* alphabetically, *not* creation
  order. List your port connections first, in the order you want. The checker's
  closed-form comparison catches a scramble loudly (outputs land in the wrong rows).
- Every network in a `Circuit` needs a **unique, non-empty `.name`** — three
  `wilkinson_network(name=...)` calls need three names, or the Circuit refuses.
- A connection entry with three nodes (`[(port, 0), (line_a, 0), (line_b, 0)]`)
  is an ideal junction — that *is* the Wilkinson's input tee; no extra tee network.
- The toolkit's lines carry their characteristic impedance as their port reference
  (70.7 Ω arms have 70.7 Ω ports); `Circuit` does the junction bookkeeping.
  Do not renormalize anything by hand.
- Module 3's phase convention: port 3 *leads* port 2 by ψ. If your null lands at
  270° instead of 90°, you conjugated the excitation — say so in ANSWERS.md and
  fix the sign.

## Running it — the two commands

```
python hw7_starter.py --check    # measured facts per module (the instrument)
python hw7_starter.py --plot     # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and
the run continues. No RNG anywhere — every run prints identical numbers.

## The toolkit (provided — think in these nouns)

- `F0_HZ`, `FREQ`, `I_F0`, `Z0_OHM` — 10 GHz design frequency, the 5–15 GHz sweep
  (f₀ sits exactly on the grid at index `I_F0`), the 50 Ω reference.
- `tem_line(z_ohm, deg_at_f0, name)`, `resistor2(r_ohm, name)`,
  `circuit_port(name)` — the element makers (ideal TEM media, real dispersion:
  a 90° line at f₀ is 45° at f₀/2).
- `wilkinson_network(z_line_ohm, r_iso_ohm, name)` — the assembled single
  Wilkinson from hour 3: module 1's referee *and* module 2's building block.
- `branchline_network(name)` — the assembled 3-dB quadrature hybrid
  (1 in, 2 through, 3 coupled, 4 isolated): module 3's device under test.
- `is_reciprocal`, `unitarity_residual`, `passivity_residual` — lecture 4's
  invariant suite, re-provided (you built these in hw4; here they referee).
- `db20(x)`, `s_at_f0(ntwk)` — dB with a −320 dB floor (so ideal nulls print),
  and the S-matrix at exactly f₀.
- The **instrument**: `_ideal_feed_s0` (the tree's closed-form S(f₀) — every path
  is two quarter-wave hops, (−j/√2)² = −½) and `_imbalance_vs_depth` (Q1's
  referee). Read them *after* you finish.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to Q1 and Q2 **before** you run, then explain any gap.
A useful division of labor: you state the contract ("closed form at f₀ for
arbitrary Z_line and R; ports in appearance order; ψ leads on port 3"), the AI
types; you verify against the assembled circuit and the closed-form tree — and then
*you* sign the ANSWERS, because the even/odd reasoning returns on lecture 9's
coupled lines with no checker to lean on.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Module 1, all four (Z_line, R) cases vs the assembled circuit: max|ΔS| ≈
  **2e-16** (bar: 1e-6). Ideal S₂₁ = **−3.0103 dB at −90°**; R doubled to 200 Ω:
  |S₁₁| stays **0**, |S₂₂| = **1/6**, isolation **−15.56 dB**.
- Corporate feed: outputs all **−6.0206 dB** (spread **0.00 dB**), match and worst
  output–output isolation at the **−320 dB float floor**; unitarity residual at f₀
  = **√3 = 1.732051** (Q3 asks why it is not 0).
- Depth instrument: **0.100 / 0.200 / 0.300 dB** at depths 1/2/3.
- Monopulse: boresight Σ = Δ = **−3.0103 dB**; null at ψ = **90.00°**, depth
  **−313 dB** below Σ (float floor); the two paths into Δ: equal amplitudes
  **0.5000**, exactly **180.000000°** apart.

## References

- Steer, *Microwave and RF Design* Vol. 4 chs. 5–6 (free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 7 — [R1]
- scikit-rf documentation (`skrf.circuit.Circuit`) — [R37]
