# Homework 9 — Copper at last

**Follows:** Lecture 9 (Filters II: distributed realizations)
**Submit:** `hw9_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Homework 8 synthesized a filter out of henries and farads. At 60 MHz you can buy
those. At 2.4 GHz you cannot — a 1270 nH inductor is a self-resonant antenna long
before it is an inductor — so this week the same insertion-loss philosophy gets
etched into the course board (hw5's RO4350B: ε_r = 3.48, h = 0.508 mm). Two
filters:

- **The warm-up:** a 3 GHz stub lowpass — N=3 Chebyshev, 0.5 dB ripple — via
  Richards' transformation and Kuroda's identities. Exact at the band edge *by
  construction*: the checker expects −0.5000 dB at 3 GHz to the last digit.
- **The main event:** a **2.4 GHz coupled-line bandpass** — N=3, 0.5 dB ripple,
  10% fractional bandwidth, 50 Ω — carried all the way to copper: g-values →
  J-inverters → even/odd impedances → (via the toolkit's inverse-Hammerstad
  dimension helper) widths, gaps, and lengths in millimeters.

Then the honesty section: sweep 0.1–10 GHz. Distributed filters are periodic —
somewhere up there your bandpass **opens again**, and Q1 makes you predict where
before you look. Finally an openEMS-style case study (`load_case_study`) sits
"reality" next to your ideal sweep and you quote the gap.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `stub_lowpass` | warm-up: Richards + Kuroda, exact by construction | ~50 min | 25% |
| 2 | `coupled_bpf_z0eo` | **the core** — the synthesis chain to (Z0e, Z0o) | ~40 min | 30% |
| 3 | `bpf_sweep`, `bpf_spec_report`, `find_reentrant` | the honest sweep | ~40 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 20% |

Modules are independently checkable: module 1 is refereed on its own (closed
form + skrf); module 3 is fed `REF_BPF_Z0EO` — this exact spec's **textbook
table** (Pozar Example 8.8), centered at 2.0 GHz — so it works while module 2 is
still broken. The coupled-line section's ABCD is toolkit plumbing
(`coupled_section_abcd`); **the core is knowing what to feed it.**

Edges that bite, surfaced now:

- **Module 1 must return only `"shunt_open"` and `"line"` elements.** Richards
  hands you series short-circuited stubs; microstrip cannot build one (a series
  stub interrupts the ground return). That is what Kuroda is *for* — one
  identity per end, after adding a unit element (a Z₀ line) at each port. If
  `"series_short"` survives in your list, the checker will say so.
- **The commensurate convention is λ/8 at f_c for the LPF (Ω = tan θ = 1 at the
  band edge) and λ/4 at f₀ for the BPF (θ = 90°).** The sweep benches assume
  it; your impedances are frequency-free, which is why neither module 1 nor 2
  takes a frequency argument.
- **Interior vs end J-inverters differ**: the end sections carry a square root,
  the interior ones do not. If your section-2 coupling comes out as strong as
  section 1's, you've square-rooted everything.
- **The ideal transmission zero at 2f₀ sits ON the sweep grid** (4.8 GHz). Your
  `bpf_sweep` will print a few hundred dB there — that is the zero, not a bug.
  (Whether *reality* honors that zero is Q2.)

## Running it — the two commands

```
python hw9_starter.py --check    # measured facts per module (the instrument)
python hw9_starter.py --sweep    # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented"
and the run continues. Everything is deterministic — no RNG anywhere.

## The formula card (lecture 9, hours 1–2; Pozar 8.5, 8.7)

- **Richards:** Ω = tan(βl); cut every element λ/8 at f_c so Ω(f_c) = 1. Then
  L → series short stub of Z = g·Z₀, C → shunt open stub of Z = Z₀/g.
- **Kuroda (the identity hour 1 derived):** a unit element of impedance Z₁
  followed by a series short stub Z₂ equals a shunt open stub Z₁(Z₁+Z₂)/Z₂
  followed by a unit element Z₁+Z₂. (With n² = 1 + Z₂/Z₁: the stub moves
  across the line and both impedances pick up n².)
- **Coupled-line BPF (Δ = fractional bandwidth):**
  J₁Z₀ = √(πΔ/2g₀g₁);  JₖZ₀ = (πΔ/2)/√(g₍ₖ₋₁₎gₖ) for k = 2..N;
  J₍N₊₁₎Z₀ = √(πΔ/2gNg₍N₊₁₎);
  then per section  Z0e = Z₀(1 + JZ₀ + (JZ₀)²),  Z0o = Z₀(1 − JZ₀ + (JZ₀)²).
- **Dimensions** are toolkit: `coupled_dims` (Akhtarzad's single-line
  equivalence over inverse-Hammerstad — quasi-static, thin-strip; a starting
  point a field solver would refine) and `quarter_wave_len_m`.

## The toolkit (provided — think in these nouns)

- `SPEC_LPF`, `SPEC_BPF`, `F_LPF_HZ`, `F_BPF_HZ`, `RO4350B` — the missions.
- `g_values` — **hw8's engine, re-provided** as the instructor reference
  implementation, and still validated against `_scipy_g_referee` on every
  `--check` (trust is earned per run, even for instructor code).
- `richards_omega`, `cheb_atten_db` — the closed-form referee pair: chain them
  and the *entire* stub-filter sweep has an analytic truth to land on.
- `abcd_line`, `abcd_shunt_open_stub`, `abcd_series_short_stub`,
  `abcd_cascade`, `abcd_to_s`, `sweep_stub_filter` — the measurement bench.
- `richards_series_form` — the unbuildable pre-Kuroda network, for the
  equivalence measurement (Q3).
- `coupled_section_abcd` — the coupled-line section from (Z0e, Z0o, θ):
  lecture 7's even/odd analysis, cashed in. Plumbing, not core.
- `coupled_dims`, `quarter_wave_len_m`, `u_for_z0`, `z0_of_u`, `eps_eff_of_u`
  — the dimension helpers (hw5's Hammerstad, re-provided, + Akhtarzad).
- `REF_F0_HZ`, `REF_BPF_Z0EO` — module 3's known-good input (the textbook
  table at 2.0 GHz).
- `load_case_study` — the openEMS case study loader. **openEMS is
  instructor-run only**; if the export `openems_coupled_bpf.s2p` is absent the
  loader generates `PLACEHOLDER_coupled_bpf.s2p` — the ideal model with a
  documented, physically-motivated perturbation (even/odd ε_eff split ±3%,
  +2% dispersion) — and *says so loudly*. Every delta the checker prints from
  it is tagged `[PLACEHOLDER numbers]`. The post-processing is identical
  either way; when the real export lands, only the numbers change.
- The **instruments**: `_scipy_g_referee`, `_skrf_stub_referee` (skrf media
  with γ = jω/c passed explicitly — the field note from lecture 2 applies),
  `_skrf_coupled_referee` (each section rebuilt from two plain skrf lines,
  even/odd combined — a path that never touches the toolkit's cot/csc).

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the
part that must be yours: commit to Q1 and Q2 **before** you run, then explain
any gap. A useful division of labor: you state the contract ("λ/8 at f_c, so
Ω(f_c)=1; no series stubs in the output; end J's carry the square root; θ is
90° at f₀; the reentrant search starts above 1.5f₀"), the AI types; you verify
against the closed form, the textbook table, and the skrf referees — and then
*you* sign the (w, s, ℓ) table, because copper does not take pull requests.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Stub LPF elements: shunt **81.3228 Ω** | line **129.8140 Ω** | shunt
  **45.5917 Ω** | line | shunt (mirror); all λ/8 (ideal-line 12.4914 mm).
  |S21| at 3 GHz = **−0.500000 dB**; vs the mapped-Chebyshev closed form,
  max |Δ| ≈ **3e-14 dB**; vs the skrf referee ≈ **1e-9**; Kuroda equivalence
  vs the series form ≈ **7e-16** (it is an identity, not an approximation).
  Attenuation pole at 6 GHz; passband **again** over 9–15 GHz.
- Coupled BPF: J·Z₀ = **0.3137 / 0.1187 / 0.1187 / 0.3137**; (Z0e, Z0o) =
  **(70.6048, 39.2355)** end sections, **(56.6407, 44.7687)** interior —
  Pozar Example 8.8's table, matched to ≤ 5e-5 Ω. Dimensions on RO4350B:
  end sections **w 0.9307 / s 0.0874 / ℓ 19.036 mm**, interior
  **w 1.1522 / s 0.4567 / ℓ 18.885 mm**.
- Ideal sweep: IL(f₀) **0.0000 dB**; measured 0.5-dB ripple bandwidth
  **9.83 %** (designed 10 — Q4 reconciles the fee); worst attenuation over
  the design band **0.5659 dB** (at the 2.28 GHz edge); attenuation at
  4.8 GHz ≈ **389 dB** (the ideal zero); **first reentrant passband at
  7.2000 GHz** (error vs 3f₀: 0.000%), wide open at 0 dB.
- Case study (PLACEHOLDER until the instructor export lands): center
  **2.4000 → 2.3740 GHz (−26 MHz, −1.08%)**; |S21| at 2.4 GHz **−0.285 dB**;
  near 2f₀ the ideal −77 dB becomes **−0.3 dB** — the spur.
- Sweeps vs skrf referee: max |ΔS21| ≈ **6e-13**.

## References

- Steer, *Microwave and RF Design* Vol. 4 chs. 2–3 (free) — [R2]
- Pozar, *Microwave Engineering* 4e §§8.5–8.8 — [R1]
- Akhtarzad, Rowbotham, Johns, "The Design of Coupled Microstrip Lines,"
  *IEEE Trans. MTT-23*, 1975 — the dimension helper's method
- Richards 1948; Kuroda's identities via Pozar Table 8.7
