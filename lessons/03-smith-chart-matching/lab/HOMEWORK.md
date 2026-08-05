# Homework 3 — Match the antenna, twice

**Follows:** Lecture 3 (The Smith chart & impedance matching)
**Submit:** `hw3_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code, your chart, and your answers. `--check`
prints measured facts about your modules — use it as an instrument; it is not
the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Last week's antenna is back. The 2.4 GHz patch that lied to its feed line —
Z_L = 36 − j21 Ω — reflected 8.1% of everything you sent it (|Γ| = 0.285,
SWR 1.80), and in homework 2 you moved the mismatch around with a λ/4
transformer. This week you *fix* it — twice, because your company is deciding
between two products:

- **Product A, lumped:** an L-section — one series and one shunt component,
  two solder joints. The 2-GHz-and-below world builds matches this way.
- **Product B, distributed:** a single shunt open stub on 50 Ω line — no
  components at all, just copper lengths d and ℓ. The microwave world's way.

Both must be *perfect at 2.4 GHz* — the scikit-rf cascade referee demands
|Γ(f₀)| < 10⁻⁸, and a correct design lands near 10⁻¹⁶, because the algebra
is exact — and then the two products face the question perfection dodges:
**what happens off-frequency, and which design survives the band?**

Everything in this homework is lecture 3: the L-section closed forms from the
chart geometry (module 1), the stub design in admittance country (module 2 —
the core; hour 3's deliberate bug lives and dies here), and the band
comparison (module 3). Lines are ideal lossless 50 Ω throughout (skrf
`DefinedGammaZ0` — same referee family as homework 2).

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `lsection_match` | product A — both topologies, chosen by load region | ~50 min | 30% |
| 2 | `stub_match` | **the core** — product B, designed in admittance | ~50 min | 30% |
| 3 | `rl_bandwidth_hz` | the comparison — measure what each product costs | ~30 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker verifies module 3 against a
planted analytic |Γ(f)| (exact closed-form edges) and against *instructor*
reference designs, so a broken module 1 never hides module 3. The `--smith`
picture likewise falls back to the instructor designs for any module you
haven't finished.

Contract notes (the goal, not the path — how is your business):

- `lsection_match(z_load, z0, f0)` returns a **list of design dicts** (keys
  documented at `gamma_in_lsection`). Try both topologies; the load's chart
  region decides which is real. This load admits one topology and two ±
  solutions — but your function must *discover* that, because the checker
  also feeds it Z_L = 120 + 90j, which lives in the other region.
- `stub_match(z_load, z0, kind)` returns the **two** (d, ℓ) solutions in
  wavelengths (keys at `gamma_in_stub`). The design is frequency-free
  geometry: rotate to the g = 1 circle *of the admittance*, then cancel the
  leftover susceptance with the stub. Hour 3 showed what happens if you do
  this on the wrong chart.
- `rl_bandwidth_hz(f, gamma, f0, rl_db)` walks outward from f₀ to the first
  threshold crossings and interpolates between samples. Return `None` for an
  edge that never crosses inside the sweep — **this will actually happen
  here**, and Q5 asks why.

## Running it — the two commands

```
python hw3_starter.py --check    # measured facts per module (the instrument)
python hw3_starter.py --smith    # the chart + sweep pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented"
and the run continues.

## The toolkit (provided — think in these nouns)

- `Z_ANT`, `F0_HZ`, `Z0_OHM`, `F_BAND_HZ` — the patient and the band.
- `gamma_of_z` / `z_of_gamma` — the bilinear map, both directions.
- `swr_of_gamma`, `return_loss_db`, `db`, `undb` — lecture 1–2 conversions.
- `zin_line(z_load, z0, d_lam)` — lecture 2's tangent transformation.
- `element_of_x(x, f0)` / `element_of_b(b, f0)` — a reactance/susceptance as
  a component `('L', henries)` or `('C', farads)`; sign handled for you.
- The **referee**: `gamma_in_lsection(design, f)` and `gamma_in_stub(design,
  f)` — scikit-rf cascades of your designs against the antenna. Your algebra
  says the match is perfect; the referee *builds the circuit* and measures.
- `REF_LSECTION` / `REF_STUB` — instructor designs (hard-coded measurements)
  that keep module 3 and `--smith` alive before modules 1–2 work.

## Edge cases that will bite (surfaced on purpose)

- **The arctan branch.** `t = tan(βd)` can be negative; add λ/2 (i.e. π to
  the angle) so every length lands in [0, 0.5) wavelengths. A negative stub
  length is a design review you do not want.
- **Signs are components.** Series x > 0 is an inductor, x < 0 a capacitor;
  shunt b > 0 is a capacitor, b < 0 an inductor. `element_of_x/b` encode
  this — read them once.
- **Do not round your design values.** The referee demands |Γ(f₀)| < 10⁻⁸;
  full-precision floats give ~10⁻¹⁶, but hand-rounding to 4 digits gives
  ~10⁻⁵ and the checker will show it. (Real parts come in ±5% tolerance
  bins anyway — Q4 is about what the referee does and does not certify.)
- **Edges may not exist.** The unmatched antenna already sits at 10.90 dB
  return loss, above the 10-dB threshold — some matched sweeps never cross
  it. Return `None`, print gracefully, and think (Q5).

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are
the part that must be yours: commit to the numbers **before** you run, then
explain any gap. A useful division of labor: you state the contract ("two ±
solutions; topology by region; lengths in [0, 0.5)λ; None for a missing
edge"), the AI types; you verify against the skrf referee and the chart —
if the trajectory doesn't pass through the g = 1 circle, no amount of
confident code output matters.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- The patient: |Γ| = **0.2851**, SWR = **1.7976**, RL = **10.90 dB**,
  delivered power **91.9%** unmatched.
- L-section sol 1: series **L = 2.8814 nH**, shunt **C = 0.8271 pF**;
  sol 2: series **C = 45.7359 pF**, shunt **L = 5.3170 nH**; both
  |Γ(f₀)| ≈ **2.7 × 10⁻¹⁶** in the skrf cascade, intermediate point
  exactly on g = 1 (Re y = 1.000000000).
- Stub (open) sol 1: **d = 0.495274 λ (61.87 mm), ℓ = 0.414589 λ
  (51.79 mm)**; sol 2: **d = 0.199260 λ (24.89 mm), ℓ = 0.085411 λ
  (10.67 mm)**; y at the stub plane = **1 ± j0.5949**; |Γ(f₀)| ≈
  **1.8 × 10⁻¹⁶**.
- Worst in-band return loss, 2.0–2.8 GHz: L-section 1 **20.16 dB**,
  L-section 2 **24.32 dB**, stub 1 **4.21 dB**, stub 2 **15.34 dB**.
- True 10-dB-RL bandwidths (wide sweep 0.5–4.5 GHz): stub 1
  **1414.7 MHz** [2.1870, 3.6017 GHz], stub 2 **2187.6 MHz**
  [0.9327, 3.1204 GHz]; both L-sections are **one-sided** (L-section 1
  never crosses on the low side, upper edge 3.5666 GHz; L-section 2 lower
  edge 1.1570 GHz, never crosses on the high side).
- Planted-truth check for module 3: 10-dB edges of |Γ| = |f−f₀|/GHz are
  f₀ ± 316.228 MHz (BW **632.456 MHz**); 15-dB, f₀ ± 177.828 MHz
  (BW **355.656 MHz**). Your measurer should agree to sub-kHz.

## References

- Steer, *Microwave and RF Design* Vol. 3 ch. 6 (matching, free) — [R2]
- Pozar, *Microwave Engineering* 4e ch. 5 — [R1]
- Smith 1939 / 1944, the original chart papers (assigned for the joy of it) — [R19]
- Orfanidis, *Electromagnetic Waves and Antennas* ch. 13 (free) — [R4]
