# Homework 12 — The frequency plan

**Follows:** Lecture 12 (Mixers, detectors & receiver architectures)
**Submit:** `hw12_starter.py` (three modules implemented) + `ANSWERS.md`
**Graded by:** the TA, reading your code and your answers. `--check` prints measured
facts about your modules — use it as an instrument; it is not the grade.
**Estimated effort:** ≤ 3 hours including the thinking
**Due:** ___________

## The story

The course radar (lecture 1's X-band perimeter set — the one whose receive chain you
budgeted in homework 10 and whose LNA you designed in homework 11) is finally getting
its receiver architecture. It tunes across **RF 10.0–10.4 GHz**, one 10 MHz channel at
a time, and must deliver that channel to an ADC that tops out at **100 MS/s** (analog
input bandwidth 500 MHz; undersampling is allowed — the IF band just has to fit inside
one Nyquist zone).

The site is not empty. A survey found four strong neighbors: **marine radars at
9.30–9.50 GHz**, the **airfield's own radar at 9.6 GHz** (2 km away, very strong),
**police/amateur activity at 10.50–10.55 GHz**, and a **microwave backhaul link at
11.20–11.70 GHz on the same mast**. Every mixer product `m·f_LO ± n·f_RF` is a door;
your job is to choose the LO side and the IF so that no strong emitter has a key —
and then to find out how slow a drone this receiver can still see once the LO's
phase-noise skirt is sitting on top of 60 dB of ground clutter.

Everything in this homework is lecture 12: the m,n product grid (module 1 — the trig
identities as code), the frequency plan and its audit (module 2 — **the core**), and
the phase-noise-limited Doppler floor (module 3). The filter specs your plan implies
come out in lecture 8's language, and the Doppler question is lecture 14–15's drone
problem arriving early.

## Modules

| # | You implement | Role | Time | Weight |
|---|---|---|---|---|
| 1 | `mixer_products`, `image_band_hz` | the mirror algebra | ~40 min | 25% |
| 2 | `audit_plan`, `filter_specs` | **the core** — the plan, defended | ~60 min | 35% |
| 3 | `doppler_study` | how slow a drone survives the skirt | ~40 min | 25% |
| — | `ANSWERS.md` | predictions, measurements, mechanisms | woven in | 15% |

Modules are independently checkable: the checker feeds each one reference inputs, so
a broken module 1 never hides module 3. Module 2's audit should *call* your module 1
grid, but the checker exercises it with the reference plans (`BUG_PLAN`, `REF_PLAN`)
either way.

Hints for the edges that bite:

- A product of an emitter **band** covers an interval, and `m·f_LO ± n·f_E` is
  monotonic in f_E — the interval's endpoints are enough. No fine emitter grid needed.
- The preselector passes the **whole** tuning band, so an image that falls inside
  10.0–10.4 GHz can never be filtered out — that is the `own_band_clear` check, and
  it is architectural, not a matter of filter order.
- In module 3 the test lines sit on exact integer-Hz bins by construction (the
  toolkit's comb), so there is no scalloping loss to chase. The line's own bin also
  contains skirt — near threshold that is a ~0.2 dB bias; subtracting the skirt
  estimate from the line bin removes it.
- The skirt falls 20 dB/decade through the crossing, so SNR is linear in log₁₀(f)
  there — fit, don't eyeball.

## Running it — the two commands

```
python hw12_starter.py --check    # measured facts per module (the instrument)
python hw12_starter.py --plot     # the two pictures ANSWERS.md asks about
```

Run from the `lab/` directory. Unimplemented modules print "not implemented" and the
run continues. The run is deterministic (fixed seeds).

## The toolkit (provided — think in these nouns)

- `RX`, `EMITTERS`, `BUG_PLAN`, `REF_PLAN` — the receiver spec, the site survey, and
  the two plans the checker exercises (plain dicts).
- `db`, `undb`, `lo_hz` — dB machinery and the LO tuning rule.
- `nyquist_zone(f_hz, fs_hz)` — which ADC zone a frequency sits in.
- `chebyshev_min_order(...)` — lecture 8's order estimate, so your filter specs come
  out as an order, not an adjective.
- `PN_PROFILE_DBC`, `pn_dbc_hz(f)` — the LO phase-noise profile, dBc/Hz vs offset.
- `synth_phase_rad`, `doppler_scene`, `doppler_psd`, `COMB_OFFSETS_HZ`, `ENBW_HZ`,
  `doppler_hz_per_mps` — the module-3 scene: clutter (+60 dB) carrying the LO's
  synthesized phase noise, a comb of 0 dB drone test lines, thermal noise, and the
  course's Doppler processing (1 s Hann frames, 1 Hz bins, 64 s stare).
- The **referees**: `_closed_form_products` (an independent m,n grid),
  `_diode_spectrum` + `_match_products_to_peaks` (an FFT of an actual behavioral
  diode mixer — physics by construction), and `_analytic_vmin_mps` (the integrated
  phase-noise bound). Read them *after* you finish; they are the cleanest statements
  of the physics in the file.

## Working with AI

Assumed and welcome. The predictions and reconciliations in ANSWERS.md are the part
that must be yours: commit to the numbers **before** you run, then explain any gap.
A useful division of labor: you state the contract ("image = f_RF ± 2·IF; a collision
is an interval overlap; severity fatal only for (1,1)"), the AI types; you verify
against the closed-form grid, the FFT referee, and the analytic bound.

## Rules of thumb from the checker facts (instructor's measured values)

So you can self-calibrate — your numbers should land here:

- Products to order 3: **24**, matching the closed form with max |Δf| = 0; the FFT
  referee finds a peak in the exact bin for **24/24**.
- Image bands at IF = 321.4 MHz: low-side **9.3572–9.7572 GHz**, high-side
  **10.6428–11.0428 GHz**.
- `BUG_PLAN` (low-side): own-band clear, ADC zone ok — and **2 fatal image
  collisions** (marine radars; the airfield radar, first colliding tune
  10.2330 GHz). `REF_PLAN` (high-side): **0 fatal**, two higher-order notes
  ((2,2) and (3,3) of the police band), **feasible**.
- Feasible IF windows on a 2.5 MHz grid: low-side **none**; high-side
  **277.5–392.5 MHz** (39 grid points, with gaps at the 300 and 350 MHz zone edges).
- Filter specs for `REF_PLAN`: preselector **n = 7** (n_exact 6.12, 60 dB at
  10.6428 GHz); IF filter **n = 4** (n_exact 3.99, 60 dB at the 300 MHz zone edge).
- Module 3: minimum visible speed measured **2.566 m/s** vs analytic bound
  **2.542 m/s** (skirt crossing at 173.0 Hz) — relative error **0.94%**
  (criterion ≤ 5%).

## References

- Steer, *Microwave and RF Design* Vol. 5 chs. 5–6 (free) — [R2]
- Pozar, *Microwave Engineering* 4e, ch. 13 — [R1]
- TI, "The Fundamentals of Millimeter Wave Radar Sensors" (SPYY005) — [R34]
