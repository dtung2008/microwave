# Homework 11 — Your first LNA

**Follows:** Lecture 11 (Amplifier design & the LNA)
**Submit:** `hw11_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints
measured facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## Step 0 — download the device (before anything else)

The device is real: a **Mini-Circuits PGA-103+** MMIC. Follow README.md step 0
(browser download of `PGA-103+_S2P.zip` from the Mini-Circuits product page,
extract **`PGA-103+_5V_Plus25DegC.s2p`** into `lab/`). Without it every command
still runs on a clearly-labeled synthetic device — the physics is the same but
every number differs, and the datasheet cross-check in Q4 has nothing to check
against. One caveat carried from lecture 4: an .s2p carries **no noise data**;
the noise parameters in the toolkit are instructor-modeled (calibrated to the
PGA-103+ datasheet's 50 Ω NF column) and say so in their docstring.

## The story

Lecture 10 designed the course radar's receive chain and concluded the first
stage rules the noise budget. This week the first stage stops being a block
labeled "LNA, NF = 1 dB" and becomes a part you design: a single-stage 2.4 GHz
low-noise amplifier around a measured two-port. Three jobs, in the order a
working engineer does them:

1. **Is it safe?** The stability audit: K, Δ, μ across the *entire* file
   (10 MHz–20 GHz — the vendor measured far beyond the 4 GHz datasheet band,
   and lecture 11 told you why you must look), verdict per band, stability
   circles at the three frequencies the harness flags.
2. **How much gain can I have, and how do I take less?** Matches for a
   transducer-gain target set **2 dB below G_T,max** (MAG at 2.4 GHz, where
   this device is unconditionally stable; where μ < 1 the honest ceiling is
   only the post-stabilization MSG — your ANSWERS discuss the difference),
   verified by cascading real L-section networks around the device.
3. **What does noise cost?** The gain-vs-NF frontier from the noise
   parameters, a design point picked on it, and one paragraph defending it.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `k_delta_mu`, `unstable_bands`, `stability_circles` | the stability audit | ~40 min | 30% |
| 2 | `max_gain_db`, `simultaneous_match`, `gt_db`, `design_for_gain` | **the core** — the gain design | ~60 min | 35% |
| 3 | `nf_db`, `frontier` | the trade | ~35 min | 20% |
| — | `ANSWERS.md` | predictions, measurements, the defense | woven in | 15% |

Modules are independently checkable: the harness referees module 1 against
skrf's own K and a geometry path for μ, module 2 against skrf `max_gain` and a
physical cascade, module 3 against the noise model's own fixed points — a
broken module 1 never hides module 2.

## Edges that bite (surfaced on purpose)

- **Γ_MS has two roots.** Take the `-` root of the quadratic (the one with
  |Γ| < 1) when B₁ > 0 — the checker's `G_T − MAG` identity line goes loud if
  you grab the wrong one.
- **`|S22 − Δ·conj(S11)|` is one modulus of one complex sum**, not a
  combination of moduli. Most wrong μ values on this homework are this line.
- **Stability-circle denominators (|S22|² − |Δ|²) can be negative.** The
  center keeps the sign; the radius takes an absolute value.
- **The G_A circle can enclose the chart center** (it does, for one of the
  two devices) — the "nearest point to the origin" formula c − r·c/|c| still
  works; sketch it before you trust it.
- **Δ is not |Δ|** until the verdict needs it. Return the complex determinant;
  compare magnitudes only in the K–Δ test.
- **Don't hand-parse the .s2p** — it is dB/degree format; `skrf.Network`
  already did this correctly in lecture 4.

`design_for_gain`'s path is yours: the lecture sketched the constant-
available-gain-circle route (draw the G_A = target circle, pick a point,
conjugate-match the output so G_T = G_A), but the contract is only that
`gt_db` of your pair hits the target with both |Γ| < 1 — the cascade referee
measures the result, not the method.

## Running it — the two commands

```
python hw11_starter.py --check    # measured facts per module (the instrument)
python hw11_starter.py --plot     # the three pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented"
and the run continues.

## The toolkit (provided — think in these nouns)

- `the_device()` / `demo_device()` — the vendor Network (or the synthetic
  fallback, clearly labeled) · `at(f_grid, f)` — nearest grid index ·
  `F0_HZ` = 2.4 GHz.
- `noise_params_at(f_hz)` — (F_min linear, Γ_opt, R_n/Z0), instructor-modeled.
- `lsection_for(gamma, f_hz)` / `build_amp(nt, gamma_s, gamma_l)` — lecture 3's
  lossless L-sections, and the full matcher–device–matcher cascade the referee
  measures.
- `system_nf_db(nf1_db, g1_db, nf2_db)` — lecture 10's Friis cascade, for Q5.
- hw4's nouns where you'd expect them: `to_network`, `abcd_series`,
  `abcd_shunt`, `unitarity_residual` (the harness uses it to prove the
  matchers are lossless before trusting the cascade).

## Working with AI

Assumed and welcome. The division of labor that works: you state the contract
("(nf,2,2) in, three arrays out; μ uses one modulus of S22 − Δ·conj(S11); the
verdict needs K AND |Δ|"), the AI types; you verify against the referees and
the identities (`G_T at the simultaneous match = MAG`, `both stability
criteria agree everywhere`) — and you write the predictions before any of it
runs. The frontier defense in Q5 must be argued from your own printed numbers.

## Instructor's measured values (so you can self-calibrate)

With the vendor file (5 V, +25 °C), the reference solution measures:

- At 2.4 GHz: **K = 1.0973, |Δ| = 0.5499, μ = 1.2254**; |S21|² = 9.685 dB,
  MSG = 12.128 dB, **MAG = 10.227 dB**; Γ_MS = 0.413∠−160.8°.
- μ < 1 bands: **0.010–0.110 GHz** (worst 0.294) and **15.10–16.80 GHz**
  (worst 0.710); both criteria agree at 660/660 points.
- Target G_T = 8.227 dB; the cascade referee lands on it to **+0.00e+00 dB**.
- Noise model at 2.4 GHz: NF_min = 0.820 dB, Γ_opt = 0.372∠75.6°; NF at the
  gain match = 1.599 dB; the move to Γ_opt costs **1.433 dB** of G_T.

On the synthetic fallback: μ < 1 band 0.20–1.60 GHz (worst 0.722 at 0.65 GHz);
at 2.4 GHz μ = 1.304, MAG = 18.001 dB; the Γ_opt move costs 0.663 dB.

## References

- Steer, *Microwave and RF Design* Vol. 5 chs. 2–3 (free) — [R2]
- Pozar, *Microwave Engineering* 4e chs. 11–12 — [R1]
- Gonzalez, *Microwave Transistor Amplifiers* (reference) — [R7]
- PGA-103+ datasheet (Mini-Circuits) — your Q4 referee.
