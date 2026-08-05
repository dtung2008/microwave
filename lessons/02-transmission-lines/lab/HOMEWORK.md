# Homework 2 — The feed line that lies

**Follows:** Lecture 2 (Transmission-line theory)
**Submit:** `hw2_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

A rooftop station: 10 m of RG-58-class coax runs up the mast to a 2.4 GHz antenna
that actually measures **Z_L = 36 − j21 Ω**. The previous owner checked return loss
from the shack end of the cable, read **30 dB**, and logged "antenna: excellent."
The antenna is not excellent. It reflects 8.1% of everything that reaches it
(SWR 1.80, return loss 10.90 dB) — the cable's 9.66 dB of one-way loss laundered
the reflection, twice, before the instrument ever saw it.

Your job: build the machinery that tells the truth. First the line engine — γ, Z₀,
Γ, SWR, Z_in from the RLGC cell (module 1, the core, and the tool lectures 3–6 keep
reusing). Then the power accounting — of every watt the transmitter launches, how
much reaches the antenna, how much escapes back, and how much just heats 10 m of
cable (module 2). Then the fix: a quarter-wave transformer at the antenna end,
placed and sized by *your* code, exact at f₀ by construction — and measured
honestly off-frequency (module 3).

The antenna's Z_L is frozen across the sweep to isolate line behavior; it returns,
frequency-dependence and all, in lecture 3 — where this same antenna finally gets
matched with standard 50 Ω parts.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `propagation`, `reflection`, `swr`, `z_in` | **the core** — the line engine | ~50 min | 35% |
| 2 | `power_ledger` | where every milliwatt goes | ~30 min | 25% |
| 3 | `quarter_wave_fix`, `fix_gamma` | the λ/4 fix, and its honest bandwidth | ~45 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Each module has its own referee, so a broken module never hides another: module 1
is measured against scikit-rf's `DistributedCircuit` (an independent solution of
the same RLGC cell — criterion 1e-6, a correct engine lands near 1e-16); module 2
against an **energy-conservation invariant** (lossless: |Γ|² + delivered = 1 to
1e-12 — physics, no library); module 3 against a full skrf rebuild of your
assembly (`DefinedGammaZ0` cascade) plus the |Γ(f₀)| < 1e-10 by-construction test.

Contract notes (the goal, not the path — how is your business):

- `z_in` must use the **lossy (tanh) form** — the lossless tangent has a pole at
  exactly λ/4, which is exactly where module 3 lives. `np.tanh` stays finite where
  `np.tan` explodes (README troubleshooting has the symptom).
- Two gammas live in this file and they are never the same thing: `gamma_per_m`
  is the propagation constant (complex, 1/m); a reflection coefficient is always
  `refl` (complex, dimensionless).
- `power_ledger`'s model: 1 W of wave power incident at the line's input, matched
  generator (nothing re-reflects at the source). Its load reflection is referenced
  to the **line's own z0** — which is complex when lossy. The three fractions must
  sum to 1.
- `quarter_wave_fix` wants the **shortest** spacer that reaches a purely real
  plane (Q1 predicts where that is). Design with the *ideal* line's β = 2πf/v_p,
  not the lossy cable's γ — they differ in the sixth digit, and a 1e-10 criterion
  notices sixth digits.

## Running it — the two commands

```
python hw2_starter.py --check    # measured facts per module (the instrument)
python hw2_starter.py --sweep    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and
the run continues.

## The toolkit (provided — think in these nouns)

- `RG58`, `Z_ANT_OHM`, `F0_HZ`, `FEED_M`, `Z0_SYS_OHM`, `BAND_HZ`, `WIDE_HZ` —
  the cable, the patient, and the sweeps.
- `db` / `undb` — lecture 1's modules, now toolkit; `rl_db(refl)` — return loss.
- `vp_m_s(line)` — phase velocity of a line's lossless skeleton.
- `ideal_line(z0, vp)` / `lossless(line)` — build matching sections; switch a
  cable's loss off (the energy invariant is exact only there).
- `band_edges_hz(f, refl, rl_db, f0)` — the bandwidth measurer: contiguous band
  around f₀ above a return-loss level, edges interpolated. An edge that never
  crosses inside the scan comes back as the scan end — module 3's wide sweep
  exists so the edges are real.
- The **referee**: `_skrf_zin_referee` (skrf's own γ/Z₀ pushed through the
  reflection-rotation identity — no tanh anywhere) and `_skrf_fix_referee` (your
  fix rebuilt as a `DefinedGammaZ0` cascade). Read them *after* you finish; they
  are also the cleanest statement of the physics in the file.

## Edge cases that will bite (surfaced on purpose)

- **The λ/4 pole.** `z_in` at exactly a quarter wave with the lossless tan form
  divides by ~0. Use tanh. (This is the #1 support ticket every year.)
- **The spacer branch.** The rotation equation has infinitely many solutions
  spaced λ/2 apart; take the shortest *positive* one, or your |Γ(f₀)| is still
  perfect and your bandwidth quietly halves — hour 3's deliberate bug, as a
  design decision you make without noticing.
- **Complex z0.** The lossy cable's z0 = 50.0001 − j0.0589 Ω, not 50. The ledger
  references the load to *it*; the system reflection references to 50. Confusing
  the two shifts answers in the third digit — visible against the referee.
- **Broadcasting.** `z_in` must accept `ell_m` *or* `f_hz` as arrays (the checker
  sweeps frequency; the plots sweep both).

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the
part that must be yours: commit to the numbers **before** you run, then explain
any gap. A useful division of labor: you state the contract ("tanh, not tan; the
ledger's fractions sum to 1; shortest spacer; ideal β for the fix"), the AI
types; you verify against the skrf referee and the energy invariant — physics
does not care how the code was produced, only whether it is right.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- The cable at 2.4 GHz: z0 = **50.0001 − j0.0589 Ω**, α = **0.9663 dB/m**
  (9.66 dB per 10 m one-way), v_p = **2×10⁸ m/s**, λ = **83.33 mm** — the feed is
  **120.0 wavelengths** long.
- The patient: |Γ| = **0.2851** at **−109.97°**, SWR = **1.7976**,
  RL = **10.90 dB**.
- `z_in` vs the skrf referee across 2.0–2.8 GHz: max rel err ≈ **5e-16**
  (criterion 1e-6).
- The ledger at f₀, of 1 W incident: delivered **99.3 mW**, reflected back out
  **0.95 mW**, cable heat **899.7 mW**; delivered sits **10.03 dB** below
  incident = 9.66 (line) + 0.37 (mismatch). Lossless residual **0.0e+00**
  (criterion 1e-12).
- **The lie:** return loss 10.90 dB at the antenna, **30.09 dB** at the
  transmitter end of 10 m (≈ RL_L + 2 × line loss).
- The fix: spacer **8.1056 mm = 0.0973 λ** to a **27.8151 Ω** plane (= Z₀/SWR);
  Z_T = **37.2928 Ω**, ℓ_T = **20.8333 mm**; |Γ(f₀)| ≈ **7e-17** (criterion
  1e-10; the skrf rebuild agrees at 4e-17).
- Its bandwidth (wide sweep 0.1–4.8 GHz): 10-dB-RL band **1.2337–3.5663 GHz =
  2332.5 MHz** (97.2% of f₀); 20-dB-RL band **2.1115–2.6885 GHz = 577.0 MHz**
  (24.0%). The deep null is narrow — that asymmetry is Q4.

## References

- Steer, *Microwave and RF Design* Vol. 2 chs. 2–3 (free) — [R2]
- Pozar, *Microwave Engineering* 4e ch. 2 — [R1]
- Orfanidis, *Electromagnetic Waves and Antennas* chs. 10–11 (free) — [R4]
