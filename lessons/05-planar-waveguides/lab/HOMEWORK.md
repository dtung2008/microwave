# Homework 5 — Design the board, spec the pipe

**Follows:** Lecture 5 (Planar lines & waveguides)
**Submit:** `hw5_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

An X-band sensor front-end — the 10 GHz radio the course radar will grow around —
needs two pieces of transmission plumbing designed this week:

- **The board.** Every component between the mixer and the antenna port lives on a
  PCB: Rogers RO4350B, ε_r = 3.48, h = 0.508 mm core, tan δ = 0.0037, 35 μm (1 oz)
  copper. You must give the layout engineer a 50 Ω trace width, the effective
  permittivity and guided wavelength that every stub and coupler in lectures 6–9
  will be cut from, and the physical length of a λ/4 transformer that matches the
  100 Ω antenna feed.
- **The pipe.** The 30 cm run from the front-end to the antenna can be microstrip —
  or a rectangular waveguide. Three candidate sizes sit in the catalog: WR-90,
  WR-75, WR-62. You must compute each one's single-mode band, its in-band β(f) and
  group delay across the 200 MHz signal window, and then referee the loss shootout:
  microstrip vs waveguide over 30 cm at 10 GHz, with numbers.

Everything in this homework is lecture 5: Hammerstad synthesis (module 1 — the
core), the waveguide boundary-value results (module 2), and the loss budget
(module 3). The board you spec here IS the course's board — lecture 9 cuts a
coupled-line filter from your ε_eff, and lecture 11's LNA sits on your 50 Ω trace.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `ms_eps_eff`, `ms_z0`, `ms_width_for`, `quarter_wave` | **the core** — Hammerstad synthesis | ~60 min | 35% |
| 2 | `wg_cutoffs`, `wg_beta`, `wg_group_delay_s` | the waveguide picker | ~45 min | 30% |
| 3 | `loss_shootout` | the verdict table | ~20 min | 15% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 20% |

Modules are independently checkable: module 1 is refereed by scikit-rf's `MLine`
(an independent implementation with *more* physics — dispersion, finite thickness);
module 2 by the analytic f_c = c/2a, the closed-form dβ/dω, and skrf's
`RectangularWaveguide`; module 3 gets **instructor-measured reference inputs**
(`REF_W50_M`, `REF_EPS_EFF_50` in the toolkit), so a broken module 1 never hides
module 3.

## The formula card (lecture 5, hours 1–2; Pozar 3.195–3.197)

Quasi-static Hammerstad, with u = w_eff/h (use the toolkit's thickness correction
`w_eff_m` — 35 μm of copper behaves like a slightly wider thin strip):

- ε_eff = (ε_r+1)/2 + (ε_r−1)/2 · (1 + 12/u)^(−1/2)
- u ≤ 1: Z₀ = (60/√ε_eff) · ln(8/u + u/4)
- u ≥ 1: Z₀ = 120π / [√ε_eff · (u + 1.393 + 0.667·ln(u + 1.444))]
- Synthesis: either Pozar's closed-form A/B formulas, **or** a numeric root on your
  own analysis (`scipy.optimize.brentq` on `ms_z0(w) − Z₀`). Both are legitimate;
  the checker only measures the result.
- λ_g = c / (f·√ε_eff) — the *effective* permittivity, nothing else. (Hour 3's
  deliberate bug used ε_r here; every stub landed 13% short and resonated at
  11.5 GHz instead of 10. Do not re-enact it in your own module.)

Waveguide (TE_mn = transverse-electric mode with m,n half-wave field variations):
f_c(TE_mn) = (c/2)·√((m/a)² + (n/b)²), β(f) = (2π/c)·√(f² − f_c²) for the TE₁₀
mode, and group delay is L·dβ/dω — your module takes the derivative numerically
(`np.gradient`); the checker's referee does it on paper.

Hints for the edges that bite (surfaced on purpose):

- The two Z₀ regimes meet at u = 1; the 50 Ω and 70.7 Ω lines on this stackup
  both land **above** u = 1, but write both branches — lecture 9's high-impedance
  lines will not be so polite.
- Which mode is "next" after TE₁₀? For a standard a ≈ 2b guide, TE₂₀ (at c/a) and
  TE₀₁ (at c/2b) nearly tie. Compute both, take the minimum — don't assume.
- `wg_group_delay_s` gets an *array* window (9.9–10.1 GHz, 201 points). np.gradient
  handles non-scalar spacing if you pass the ω array — read its docstring, or
  derive Δω yourself. The endpoints of a one-sided difference are where the 1% bar
  is usually lost.
- The loss formulas return **Np/m**. The gate to dB is `NP_TO_DB` = 8.6859
  (= 20·log₁₀ e, not 10·log₁₀ e — amplitude decay, power dB; think it through
  once and write it down in ANSWERS Q4).

## Running it — the two commands

```
python hw5_starter.py --check    # measured facts per module (the instrument)
python hw5_starter.py --sweep    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and
the run continues. Everything is deterministic — no RNG anywhere.

## The toolkit (provided — think in these nouns)

- `RO4350B`, `FR4`, `WAVEGUIDES` — the stackups and the pipe catalog (plain dicts).
- `F0_HZ`, `WINDOW_HZ`, `RUN_M`, `Z_ANT_OHM` — the mission numbers: 10 GHz, the
  200 MHz window, the 30 cm run, the 100 Ω antenna feed.
- `w_eff_m(w_m, sub)` — Wheeler's thickness correction (feed its output to the
  zero-thickness Hammerstad formulas).
- `skrf_mline(w_m, sub, ...)`, `skrf_waveguide(name, ...)` — the referees,
  pre-configured (Hammerstad-Jensen + Kirschning-Jansen dispersion; TE₁₀).
- `ms_alpha_c_np_m`, `ms_alpha_d_np_m`, `wg_alpha_c_np_m`, `rs_ohm`, `NP_TO_DB` —
  the loss physics, provided: module 3 assembles a verdict, it does not derive.
- `REF_W50_M`, `REF_EPS_EFF_50` (+ FR-4 twins) — instructor-measured reference
  inputs that decouple module 3 from module 1.
- The **instrument**: `_wg_tau_referee_s` — the closed-form group delay your
  numerical gradient is measured against. Read it *after* you finish; it is also
  the cleanest one-line statement of what group delay is.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to Q1 and Q2 **before** you run, then explain any gap.
A useful division of labor: you state the contract ("thickness-corrected u; both
Z₀ regimes; λ_g uses ε_eff, never ε_r; β only above cutoff; Np→dB is 8.6859"),
the AI types; you verify against skrf, c/2a, and the closed-form dβ/dω — and then
*you* sign the width that goes to the board house, because copper does not take
pull requests.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- 50 Ω on RO4350B: w = **1.1131 mm**, ε_eff = **2.7361**, λ_g(10 GHz) =
  **18.124 mm**. Against skrf MLine across 1–20 GHz: worst Z₀ error **1.73 %**
  (bar 2 %), worst ε_eff error **2.63 %** (bar 3 %).
- λ/4 transformer (70.71 Ω): RO4350B w = **0.5822 mm**, L = **4.6305 mm**;
  on FR-4, L = **4.2080 mm** — ratio **1.1004** (Q1's number).
- Cutoffs: WR-90 **6.557140 GHz**, WR-75 **7.868568 GHz**, WR-62 **9.487824 GHz**
  (all exactly c/2a); next mode = 2× in every case (TE₂₀ and TE₀₁ tie).
- 30 cm group delay at 10 GHz: WR-90 **1.3254 ns**, WR-75 **1.6215 ns**, WR-62
  **3.1674 ns**; window delay spreads **19.9 / 52.5 / 582.7 ps**. Gradient vs
  analytic: worst **0.057 %** (bar 1 %).
- Loss over 30 cm at 10 GHz: RO4350B microstrip **2.694 dB** (1.206 conductor +
  1.488 dielectric) vs WR-90 **0.0321 dB** — a factor of **84** in dB terms.
  Same trace on FR-4: **10.47 dB**, 9.03 of it dielectric.

## References

- Steer, *Microwave and RF Design* Vol. 2 chs. 4–5 (free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 3 (esp. 3.8) — [R1]
- Wheeler, "Transmission-Line Properties of Parallel Strips Separated by a
  Dielectric Sheet," *IEEE Trans. MTT-13*, 1965 — the synthesis formulas' origin
- scikit-rf documentation (`skrf.media.MLine`, `RectangularWaveguide`) — [R37]
