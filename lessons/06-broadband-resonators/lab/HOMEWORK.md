# Homework 6 — The impossible spec

**Follows:** Lecture 6 (Broadband matching & resonators)
**Submit:** `hw6_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

A client email arrives: *"We need our 12.5 Ω power-amplifier termination matched to
the 50 Ω world — 20 dB return loss, 2 to 4 GHz, full octave. Also attaching three
resonator sweeps from our bench for the oscillator behind it; please report their Qs.
Timeline is tight."*

Three separate questions are hiding in that paragraph, and they are this week's three
modules. First: **is the spec even physical?** The 12.5 Ω termination pad carries
shunt capacitance, and Bode–Fano puts a hard ceiling on match bandwidth for any
C > 0 — a theorem, not a technology limit (module 1: the feasibility verdict, run on
three versions of the client's load). Second: assuming the clean load, **design the
match** — a Chebyshev multisection quarter-wave transformer: find the minimum number
of sections, design the section impedances by the small-reflection recursion, and
then *sweep the exact cascade*, because at a 4:1 impedance ratio the theory that
designed the transformer is politely lying about its ripple (module 2 — the core).
Third: **read the bench sweeps honestly** — extract Q_L by the 3-dB method and
convert to Q_u through the coupling correction; one of the three resonators is a
trap that the correction exists to catch (module 3).

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `bode_fano_best_rl_db`, `bode_fano_max_c_farad` | the physics ceiling | ~30 min | 20% |
| 2 | `cheb_gamma_m`, `cheb_min_n`, `cheb_transformer` | **the core** — the Chebyshev designer | ~75 min | 40% |
| 3 | `q_extract_3db` | the resonator lab | ~45 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs, so
a broken module 1 never hides module 2. The transformer's exact sweep machinery
(`cascade_sweep_gamma`, lecture 4's ABCD cascade) is provided in the toolkit — the
design recursion is yours; the sweeping is plumbing.

Edge cases that bite (surfaced on purpose):

- **The steps go DOWN.** Z_L < Z₀ here, so every partial reflection is negative and
  the section impedances must descend monotonically from 50 toward 12.5. If your
  N=2 design is not `[33.6, 18.6]`-shaped, check the sign of ln(Z_L/Z₀).
- **Even N has a lone middle term.** In the expansion of Γ(θ), the constant
  (cos 0·θ) term appears once, not twice. The self-check that catches both this and
  the sign: `2*sum(G_k)` must equal `ln(zl/z0)` exactly, and G_k = G_{n−k}.
- **|S21(f₀)| in the coupling formula is LINEAR.** Q_u = Q_L/(1 − |S21(f₀)|) with
  |S21| as a magnitude (0.96), never dB (−0.35). Feed it dB and you will invent a
  negative Q — the checker will show you a nonsense number, not an error message.
- **Interpolate the 3-dB crossings.** The half-power points fall between frequency
  samples; nearest-sample bandwidths miss the 2% agreement with the skrf fit.

## Running it — the two commands

```
python hw6_starter.py --check    # measured facts per module (the instrument)
python hw6_starter.py --sweep    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues.

## The toolkit (provided — think in these nouns)

- `CLIENT_SPEC`, `LOAD_MODELS`, `RESONATOR_BENCH` — the job (plain dicts).
- `cheb_t(n, x)` — Chebyshev polynomial, valid outside |x| ≤ 1 too.
- `theta_m_rad(spec)` — band-edge electrical length (60° for this octave).
- `cascade_sweep_gamma(z_sections, f_hz)` — the EXACT transformer response
  (lecture 4's ABCD cascade, provided); `worst_inband_rl_db`, `band_f_hz`, `rl_db`.
- `resonator_dataset(name)` — one bench sweep (f, S21), deterministic noise.
- The **instrument**: `_skrf_cascade_referee` re-sweeps your transformer entirely
  inside scikit-rf (media → line → renormalize → `**`); `_skrf_qfactor_referee`
  re-fits your resonators with `skrf.qfactor.Qfactor` (NPL MAT 58 method — a
  fitting method that shares no code and no idea with your 3-dB ruler). Read them
  *after* you finish; they are also worked examples of the skrf API.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor this week: you state the contract ("expand T_N(sec θ_m
cos θ) into cosine multiples, match term-by-term, middle term counts once, steps go
down; check 2ΣΓ_k = ln(Z_L/Z₀)"), the AI types; you verify against the invariant,
the referee sweep, and the ripple formula. If you cannot state the contract, that is
the signal to re-read section 1.4 of the script — not to paste the whole docstring.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Bode–Fano ceilings over the octave: C = 2.2 pF → **78.96 dB** (feasible);
  C = 10 pF → **17.37 dB** (the 20 dB spec is physically impossible);
  largest C that keeps 20 dB physical: **8.686 pF**.
- Chebyshev theory ripple: N=2 → **20.09 dB**, N=3 → **31.48 dB**, N=4 → **42.92 dB**.
- Exact swept worst in-band RL: N=2 → **18.98 dB** (MISSES the 20 dB spec),
  N=3 → **29.44 dB** (meets, with margin). Minimum N by theory: **2**; minimum N
  that survives the exact sweep: **3** — reconciling those two answers is Q4.
- N=3 section impedances: **[40.40, 25.00, 15.47] Ω** (N=2: [33.65, 18.57]).
- skrf cascade referee agreement: ~1e-15 in |Γ|.
- Resonators (3-dB + coupling correction, vs the MAT58 fit): A → Q_L ≈ 103,
  Q_u ≈ 150; B → Q_L ≈ 399, Q_u ≈ 800; C → Q_L ≈ 474, **Q_u ≈ 12100** — all
  within 2% of the `Qfactor` fits; C's Q_u/Q_L ≈ **25×**.

## References

- Steer, *Microwave and RF Design* Vol. 3 ch. 7 (free) — [R2]
- Pozar chs. 5.5–5.8 (transformers, Bode–Fano), 6 (resonators) — [R1]
- Gregory, "Q-factor Measurement by using a Vector Network Analyser," NPL Report
  MAT 58 (2021), free — the method behind `skrf.qfactor.Qfactor`
