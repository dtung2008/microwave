# Homework 4 — Trust, but verify the two-port

**Follows:** Lecture 4 (Microwave network theory: S-parameters)
**Submit:** `hw4_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

Three "measured" two-port S-parameter datasets land on your desk, each with a claim
attached:

- **Network A** — "a passive lowpass filter; some dissipation expected."
- **Network B** — "a LOSSLESS lowpass filter, ideal elements" — so says the file.
- **Network C** — "a passive two-port," per the shipping label.

At least one of them is lying. Your job is to build the machinery that convicts or
acquits *from the data alone*: a conversion library (S↔ABCD↔Z plus a correct cascade),
and the three physics invariants — reciprocity, unitarity, passivity — that every
honest passive network must satisfy. Then deliver verdicts on all three files and
defend them with residuals, not vibes.

This is the course's verification toolkit being born: `is_reciprocal`,
`unitarity_residual`, and `passivity_residual` return in lecture 7 (to audit your
Wilkinson divider) and lecture 11 (to audit a vendor's transistor file). Build them
like you will be trusting them later — because you will be.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `s_to_abcd`, `abcd_to_s`, `s_to_z`, `z_to_s`, `cascade` | the conversion library | ~55 min | 30% |
| 2 | `is_reciprocal`, `unitarity_residual`, `passivity_residual` | **the core** — the invariant suite | ~45 min | 30% |
| 3 | `verdict` | the classifications, A/B/C | ~25 min | 20% |
| — | `ANSWERS.md` | predictions, residuals, defenses | woven in | 20% |

Modules are independently checkable: module 1 is refereed by scikit-rf's own
conversions on the planted data; module 2 is fed planted *analytic* references (a
matched line is unitary by construction; a ×½ pad has ‖SᴴS − I‖ = 3/(2√2) on paper;
an ideal isolator is the textbook non-reciprocal device) — so a broken module 1 never
hides module 2. Module 3 builds on your module 2; the checker prints the harness
referee's residuals next to your verdicts so a module-2 bug cannot hide there either.

**The sealed envelope.** The generator that minted the three datasets sits in the
toolkit under a banner that says so, ground truth included. Commit your verdicts in
ANSWERS.md **before** reading it. The exercise is whether your suite can convict
without the envelope; afterwards, the generator is the cleanest statement of what
each network really is.

Hints for the edges that bite (surfaced on purpose):

- Every S/Z/ABCD array is a `(nf, 2, 2)` stack; `@` matrix-multiplies stacks
  frequency-by-frequency, and `np.swapaxes(s, -1, -2)` is the per-frequency
  transpose. No loops needed anywhere.
- **Sᵀ tests reciprocity; Sᴴ builds unitarity and passivity.** Plain transpose in one,
  conjugate transpose in the others — mixing them is this homework's classic bug, and
  it produces residuals that are *almost* right.
- Passivity is a statement about **singular values** (σ_max ≤ 1 at every frequency),
  not eigenvalues — S is not Hermitian, so `np.linalg.svd`, not `eig`.
- `s_to_abcd` divides by 2·S₂₁. Deep in A's stopband S₂₁ is ~10⁻⁴ — legal in double
  precision, but this is why the referee deltas are ~10⁻¹², not ~10⁻¹⁶.
- `cascade` must route through ABCD (or T). Hour 3 showed what S @ S does: two
  attenuators that "transmit nothing", and a cascade of two reciprocal parts that
  comes out non-reciprocal — which your own `is_reciprocal` will catch.

## Running it — the two commands

```
python hw4_starter.py --check    # measured facts per module (the instrument)
python hw4_starter.py --plot     # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues. The planted data is seeded — every run of `--check` sees identical
numbers.

## The toolkit (provided — think in these nouns)

- `F_HZ`, `Z0_OHM` — the shared "VNA sweep" (0.05–3 GHz, 201 points) and the 50 Ω
  reference.
- `NETWORKS` — the three datasets: `NETWORKS["A"]["s"]` is the `(201, 2, 2)` S array,
  `["claim"]` is the label that came with it.
- `abcd_series(z)`, `abcd_shunt(y)`, `abcd_line(z0, f0, quarter_waves)` — ABCD
  element builders (the generator uses them; your tests can too).
- `to_network(s)` — wrap any S array as a scikit-rf `Network` when you want a second
  opinion or a quick plot.
- `RECIP_TOL`, `UNIT_TOL`, `PASSIV_TOL` — the course tolerances, set ~5× above the
  planted measurement-noise floor (the comment above them says why).
- The **instrument**: the checker calls scikit-rf's `s2a`/`a2s`/`s2z`/`z2s` and the
  `**` cascade operator as module 1's referee, and `_invariants_referee` (the suite
  in ten lines) as the cross-read for module 3. Read them *after* you finish.

## Working with AI

Assumed and welcome. The verdicts and their defenses in ANSWERS.md are the part that
must be yours: commit to Q1 and Q2 **before** you run, then explain any gap. A useful
division of labor: you state the contract ("(nf,2,2) in and out; plain transpose for
reciprocity, conjugate for unitarity; cascade routes through ABCD"), the AI types;
you verify against the skrf referee and the planted analytic values — and then *you*
sign the verdicts, because the residuals will be quoted back to you in lecture 7.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Conversions vs skrf, worst over A/B/C: `s_to_abcd` **1.6e-12**, `s_to_z` **8.1e-12**;
  round trips ≤ **6.3e-14**. Cascade of 6 sections vs skrf `**`: **1.0e-15**.
  (Syllabus bar for all five: 1e-10.)
- ×½ pad unitarity residual = **1.06066** = 3/(2√2); matched line **8.9e-16**.
- Network A: recip **4.6e-04**, unitarity **0.4170**, passivity **0.0000**.
- Network B: recip **4.5e-04**, unitarity **0.0302**, passivity **0.0000** — read
  those three together before believing any file that says "lossless."
- Network C: recip **2.48**, unitarity **5.4453**, passivity **5.3528**; its |S₂₁|
  peaks at **+8.0 dB** into 50 Ω while |S₁₂| sits near −30 dB.

## References

- Steer, *Microwave and RF Design* Vol. 3 chs. 2–3 (free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 4 — [R1]
- scikit-rf documentation (`skrf.network` conversion functions) — [R37]
